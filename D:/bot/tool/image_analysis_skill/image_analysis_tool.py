#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, base64, datetime as dt, importlib.util, json, os, re, sys
from pathlib import Path
from urllib import request

OUT_ROOT=Path('D:/bot/outputs/image_analysis')
MODEL_ROOT=Path('D:/bot/models/vision')
MODES=['basic','full','product-geometry','scene-detail','people-detail','semantic-full','brand-design','brand-full','graphic-design','style-consistency','commercial-qc','qc','prompt']
SCENES=['product_photo','factory_scene','sample_room','printing_workshop','warehouse','showroom','office','poster','banner','social_post','website_hero','generic']
OBJECTS=['bottle','jar','box','garment','factory','machine','poster','banner','generic']
BACKENDS=['auto','smolvlm2','moondream','florence2','qwen25vl']


def now_dir(base:Path):
    d=base/dt.datetime.now().strftime('%Y%m%d-%H%M%S'); d.mkdir(parents=True,exist_ok=True); return d

def file_uri(p:Path): return f'FILE:file:///{p.as_posix()}'
def parse_pct(v):
    m=re.match(r'\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$',v or '')
    return float(m.group(1))/100 if m else None

def to_data_url(path):
    ext=Path(path).suffix.lower().strip('.')
    mt={'jpg':'image/jpeg','jpeg':'image/jpeg','png':'image/png','webp':'image/webp'}.get(ext,'image/png')
    return f'data:{mt};base64,{base64.b64encode(Path(path).read_bytes()).decode("ascii")}'

def openai_compat_vision(base_url, api_key, model, image_path, prompt):
    payload={'model':model,'messages':[{'role':'user','content':[{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':to_data_url(image_path)}}]}]}
    req=request.Request(base_url.rstrip('/')+'/chat/completions',data=json.dumps(payload).encode('utf-8'),headers={'Authorization':f'Bearer {api_key}','Content-Type':'application/json'})
    with request.urlopen(req,timeout=60) as r: data=json.loads(r.read().decode('utf-8','ignore'))
    txt=((data.get('choices') or [{}])[0].get('message') or {}).get('content','{}')
    try:return json.loads(txt)
    except:return {'raw_text':txt}

def openrouter_vision(image_path,prompt,model):
    key=os.getenv('OPENROUTER_API_KEY')
    if not key: return None, {'fallback_reason':'missing_api_key','error':'missing OPENROUTER_API_KEY'}
    try: return openai_compat_vision('https://openrouter.ai/api/v1',key,model or 'z-ai/glm-4.5v',image_path,prompt), {'fallback_reason':None,'error':None}
    except Exception as e: return None, {'fallback_reason':'remote_call_failed','error':str(e)}

def dashscope_vision(image_path,prompt,model):
    key=os.getenv('DASHSCOPE_API_KEY')
    if not key: return None, {'fallback_reason':'missing_api_key','error':'missing DASHSCOPE_API_KEY'}
    try: return openai_compat_vision('https://dashscope.aliyuncs.com/compatible-mode/v1',key,model or 'qwen-vl-plus',image_path,prompt), {'fallback_reason':None,'error':None}
    except Exception as e: return None, {'fallback_reason':'remote_call_failed','error':str(e)}

def openai_vision(image_path,prompt,model):
    key=os.getenv('OPENAI_API_KEY')
    if not key: return None, {'fallback_reason':'missing_api_key','error':'missing OPENAI_API_KEY'}
    use_model=model or os.getenv('OPENAI_VISION_MODEL') or 'gpt-4.1-mini'
    try: return openai_compat_vision('https://api.openai.com/v1',key,use_model,image_path,prompt), {'fallback_reason':None,'error':None}
    except Exception as e: return None, {'fallback_reason':'remote_call_failed','error':str(e)}

def local_openai_compat_vision(image_path,prompt,model):
    base=os.getenv('LOCAL_VISION_BASE_URL','http://127.0.0.1:1234/v1'); key=os.getenv('LOCAL_VISION_API_KEY','lm-studio'); m=model or os.getenv('LOCAL_VISION_MODEL')
    if not m: return None, {'fallback_reason':'missing_local_model','error':'missing LOCAL_VISION_MODEL'}
    try: return openai_compat_vision(base,key,m,image_path,prompt), {'fallback_reason':None,'error':None}
    except Exception as e: return None, {'fallback_reason':'local_endpoint_unavailable','error':str(e)}

def local_cv_analysis(image_path, brand, scene_type, object_type, use_alpha, reference, expected_height_change):
    from PIL import Image, ImageStat
    try: import numpy as np
    except ImportError: np=None
    im=Image.open(image_path); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb); mean=st.mean
    brightness=round(sum(mean)/3,2); contrast=round(sum(st.stddev)/3,2)
    sat=None; top_hex=[]
    if np is not None:
        arr=np.array(rgb).reshape(-1,3).astype('int32')
        mx=np.max(arr,axis=1); mn=np.min(arr,axis=1); sat=round(float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100),2)
        q=(arr//16)*16
        vals,counts=np.unique(q,axis=0,return_counts=True)
        idx=np.argsort(counts)[::-1][:5]
        top_hex=[('#%02X%02X%02X'%tuple(vals[i]), int(counts[i])) for i in idx]
    casts=[]
    if mean[0]-mean[2]>12: casts.append('yellow_cast')
    if mean[0]-mean[1]>10: casts.append('red_cast')
    if mean[0]>mean[1]>mean[2] and mean[0]-mean[2]>18: casts.append('orange_cast')
    if abs(mean[0]-mean[1])<6 and abs(mean[1]-mean[2])<6: casts.append('gray_cast')
    b=[0,0,w-1,h-1]; conf='low'; method='fallback'
    if np is not None:
        rgba=np.array(im.convert('RGBA')); alpha=rgba[:,:,3]
        if (use_alpha or 'A' in im.getbands()) and (alpha<250).mean()>0.02: mask=alpha>12; method='alpha-mask'
        else:
            rr=np.array(rgb).astype('float32'); bg=np.vstack([rr[0,0],rr[0,-1],rr[-1,0],rr[-1,-1]]).mean(axis=0); mask=np.linalg.norm(rr-bg,axis=2)>22; method='bg-diff'
        ys,xs=np.where(mask)
        if len(xs)>0:
            b=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]; wr,hr=(b[2]-b[0]+1)/w,(b[3]-b[1]+1)/h
            conf='high' if wr<=0.9 and hr<=0.9 else 'medium'
    x1,y1,x2,y2=b; sw,sh=x2-x1+1,y2-y1+1
    margins={'top':y1,'bottom':h-1-y2,'left':x1,'right':w-1-x2}; crop_risk=[]
    if sh/h>0.9: crop_risk.append('主体过大')
    if sh/h<0.35: crop_risk.append('主体过小')
    if min(margins.values())<8: crop_risk.append('接近裁切')
    if not crop_risk: crop_risk=['低']
    product_aspect=round(sw/max(1,sh),4)
    label_estimate=int(sh*0.42); cap_estimate=int(sh*0.16)
    veytis='likely_bottle' if 0.22 <= product_aspect <= 0.62 else 'non_standard_bottle_ratio'
    factory='looks_realistic' if contrast>20 and brightness>30 else 'possibly_flat_or_ai_like'
    gd={'title_zone':'top_20_percent','cta_zone':'bottom_18_percent','logo_zone':'top_left_safe','text_safe_zone':'center_60_percent'}
    ref={}
    if reference and Path(reference).exists():
        rim=Image.open(reference); rw,rh=rim.size; rsh=rh; actual=(sh/h)/(rsh/max(1,rh)); exp=parse_pct(expected_height_change); expected=None if exp is None else 1+exp
        ref={'reference_subject_height_px':rsh,'current_subject_height_px':sh,'expected_ratio':expected,'actual_ratio':round(actual,4),'difference':None if expected is None else round(actual-expected,4)}
    return {
        'image_info':{'filename':Path(image_path).name,'image_size':f'{w}x{h}','file_size':Path(image_path).stat().st_size},
        'color_analysis':{'top5_hex':top_hex,'average_brightness':brightness,'contrast':contrast,'saturation':sat,'casts':casts},
        'local_geometry':{'subject_bbox':{'left':x1,'top':y1,'right':x2,'bottom':y2},'subject_width_ratio':round(sw/w,4),'subject_height_ratio':round(sh/h,4),'margins':margins,'crop_risk':crop_risk,'confidence':conf,'method':method},
        'product_analysis':{'product_aspect_ratio':product_aspect,'label_estimate':label_estimate,'cap_estimate':cap_estimate,'label_height_ratio':0.42,'cap_height_ratio':0.16,'veytis_bottle_shape':veytis,'juese_factory_realism':factory},
        'graphic_design_analysis':gd,
        'reference_comparison':ref,
        'ai_qc':{'local_can_judge':['color_cast','bbox','crop_risk','label_cap_ratio','basic_realism'],'need_vision':['text_legibility','brand_logo_truth','semantic_scene_consistency']}
    }

def render_detailed_markdown(out):
    return '# 统一视觉分析报告\n\n```json\n'+json.dumps(out,ensure_ascii=False,indent=2)+'\n```'

def cmd_status(args):
    pkgs=['pillow','numpy','torch','transformers','accelerate','safetensors','sentencepiece','huggingface_hub']; checks={}
    for p in pkgs: checks[p]=importlib.util.find_spec('PIL' if p=='pillow' else p) is not None
    checks['model_root_exists']=MODEL_ROOT.exists(); checks['smolvlm2_dir_exists']=(MODEL_ROOT/'smolvlm2').exists()
    od=now_dir(Path(args.output_dir)); md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    md.write_text('# Status\n'+'\n'.join([f'- {k}: {v}' for k,v in checks.items()]),encoding='utf-8')
    js.write_text(json.dumps({'status':checks},ensure_ascii=False,indent=2),encoding='utf-8'); print(file_uri(md))

def cmd_install(args):
    if not args.model:
        print('install-local-vlm 需要 --model',file=sys.stderr); sys.exit(1)
    target=MODEL_ROOT/args.backend/args.model.replace('/','__'); target.mkdir(parents=True,exist_ok=True)
    result={'backend':args.backend,'model':args.model,'target':str(target),'dry_run':not args.yes,'downloaded':False,'error':None}
    if args.yes:
        if importlib.util.find_spec('huggingface_hub') is None:
            result['error']='缺少 huggingface_hub，请先安装。'
        else:
            try:
                from huggingface_hub import snapshot_download
                snapshot_download(repo_id=args.model, local_dir=str(target), local_dir_use_symlinks=False)
                result['downloaded']=True
            except Exception as e:
                result['error']=str(e)
    od=now_dir(Path(args.output_dir)); md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    md.write_text('# install-local-vlm\n'+'\n'.join([f'- {k}: {v}' for k,v in result.items()]),encoding='utf-8')
    js.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); print(file_uri(md))

def main():
    p=argparse.ArgumentParser(description='统一视觉分析工具')
    p.add_argument('command', nargs='?', default='analyze', choices=['analyze','status','install-local-vlm','analyze-local-vlm'])
    p.add_argument('--image'); p.add_argument('--brand',default='Generic'); p.add_argument('--mode',default='full',choices=MODES)
    p.add_argument('--scene-type',default='generic',choices=SCENES); p.add_argument('--object-type',default='generic',choices=OBJECTS)
    p.add_argument('--reference'); p.add_argument('--expected-height-change'); p.add_argument('--use-alpha',action='store_true')
    p.add_argument('--use-vision',action='store_true'); p.add_argument('--vision-provider',default='none',choices=['none','qwen','dashscope','openrouter','openai','gemini','local']); p.add_argument('--vision-model',default='')
    p.add_argument('--output-dir',default=str(OUT_ROOT)); p.add_argument('--json',action='store_true'); p.add_argument('--prompt',default='Analyze this image semantically.'); p.add_argument('--no-external-vision',action='store_true')
    p.add_argument('--backend',choices=BACKENDS,default='auto'); p.add_argument('--model'); p.add_argument('--yes',action='store_true')
    a=p.parse_args()
    if a.command=='status': return cmd_status(a)
    if a.command=='install-local-vlm': return cmd_install(a)
    if not a.image: print('缺少 --image',file=sys.stderr); sys.exit(1)
    local=local_cv_analysis(a.image,a.brand,a.scene_type,a.object_type,a.use_alpha,a.reference,a.expected_height_change)
    out={**local,'semantic_analysis':{},'vision_model_status':{'local_basic_available':True,'semantic_vision_available':False,'vision_provider_used':'none','fallback_reason':None,'error':None,'fallback_to_local_basic':True}}
    external={'qwen','dashscope','openrouter','openai','gemini'}
    if a.use_vision:
        if a.no_external_vision and a.vision_provider in external:
            out['vision_model_status'].update({'vision_provider_used':a.vision_provider,'fallback_reason':'blocked_by_no_external_vision','error':'external vision disabled'})
        else:
            sem=None; meta={'fallback_reason':None,'error':None}
            if a.vision_provider in ['qwen','dashscope']: sem,meta=dashscope_vision(a.image,a.prompt,a.vision_model)
            elif a.vision_provider=='openrouter': sem,meta=openrouter_vision(a.image,a.prompt,a.vision_model)
            elif a.vision_provider=='openai': sem,meta=openai_vision(a.image,a.prompt,a.vision_model)
            elif a.vision_provider=='local': sem,meta=local_openai_compat_vision(a.image,a.prompt,a.vision_model)
            elif a.vision_provider=='gemini': meta={'fallback_reason':'not_implemented','error':'gemini provider not implemented yet'}
            if sem is not None:
                out['semantic_analysis'].update(sem if isinstance(sem,dict) else {'raw_text':str(sem)})
                out['vision_model_status'].update({'semantic_vision_available':True,'vision_provider_used':a.vision_provider,'fallback_to_local_basic':False,'fallback_reason':None,'error':None})
            else:
                out['vision_model_status'].update({'vision_provider_used':a.vision_provider,'fallback_reason':meta.get('fallback_reason'),'error':meta.get('error')})
    od=now_dir(Path(a.output_dir)); md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    md.write_text(render_detailed_markdown(out),encoding='utf-8')
    js.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.json: print(json.dumps(out,ensure_ascii=False))
    print(file_uri(md))

if __name__=='__main__': main()
