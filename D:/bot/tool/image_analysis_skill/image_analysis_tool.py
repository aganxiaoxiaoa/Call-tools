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
    b64=base64.b64encode(Path(path).read_bytes()).decode('ascii')
    return f'data:{mt};base64,{b64}'

def openai_compat_vision(base_url, api_key, model, image_path, prompt):
    schema='仅返回JSON: scene_detail,people_detail,object_inventory,product_semantic_analysis,factory_logic_analysis,brand_visual_analysis,graphic_design_analysis,text_or_label_observation,ai_artifact_risks,commercial_fit,suggestions'
    payload={'model':model,'messages':[{'role':'user','content':[{'type':'text','text':schema+'\n'+prompt},{'type':'image_url','image_url':{'url':to_data_url(image_path)}}]}]}
    req=request.Request(base_url.rstrip('/')+'/chat/completions',data=json.dumps(payload).encode('utf-8'),headers={'Authorization':f'Bearer {api_key}','Content-Type':'application/json'})
    with request.urlopen(req,timeout=45) as r: data=json.loads(r.read().decode('utf-8','ignore'))
    txt=((data.get('choices') or [{}])[0].get('message') or {}).get('content','{}')
    try:return json.loads(txt)
    except:return {'raw_text':txt}

def local_openai_compat_vision(image_path, prompt, model=None):
    base_url=os.getenv('LOCAL_VISION_BASE_URL','http://127.0.0.1:1234/v1')
    api_key=os.getenv('LOCAL_VISION_API_KEY','lm-studio')
    use_model=model or os.getenv('LOCAL_VISION_MODEL')
    if not use_model:
        return None, {'error':'missing LOCAL_VISION_MODEL (or --vision-model)','fallback_reason':'missing_local_model','base_url':base_url}
    try:
        sem=openai_compat_vision(base_url, api_key, use_model, image_path, prompt)
        return sem, {'base_url':base_url,'model':use_model,'fallback_reason':None,'error':None}
    except Exception as e:
        return None, {'base_url':base_url,'model':use_model,'fallback_reason':'local_endpoint_unavailable','error':str(e)}

def local_cv_analysis(image_path, brand, scene_type, object_type, use_alpha, reference, expected_height_change):
    try:
        from PIL import Image, ImageStat
    except ImportError:
        raise RuntimeError('缺少 pillow，请安装：pip install pillow')
    try: import numpy as np
    except ImportError: np=None

    im=Image.open(image_path); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb); mean=st.mean
    brightness=round(sum(mean)/3,2); contrast=round(sum(st.stddev)/3,2)
    sat=None
    if np is not None:
        arr=np.array(rgb).astype('float32'); mx=arr.max(axis=2); mn=arr.min(axis=2); sat=round(float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100),2)
    casts=[]
    if mean[0]-mean[2]>12: casts.append('yellow_cast')
    if mean[0]-mean[1]>10: casts.append('red_cast')
    if mean[0]>mean[1]>mean[2] and mean[0]-mean[2]>18: casts.append('orange_cast')
    if abs(mean[0]-mean[1])<6 and abs(mean[1]-mean[2])<6: casts.append('gray_cast')

    if np is None:
        b=[0,0,w-1,h-1]; conf='low'; method='numpy_missing'
    else:
        rgba=np.array(im.convert('RGBA')); alpha=rgba[:,:,3]
        if (use_alpha or 'A' in im.getbands()) and (alpha<250).mean()>0.02: mask=alpha>12; method='alpha-mask'
        else:
            rr=np.array(rgb).astype('float32'); bg=np.vstack([rr[0,0],rr[0,-1],rr[-1,0],rr[-1,-1]]).mean(axis=0); mask=np.linalg.norm(rr-bg,axis=2)>22; method='bg-diff'
        ys,xs=np.where(mask)
        if len(xs)==0: b=[0,0,w-1,h-1]; conf='low'; method='fallback'
        else:
            b=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
            wr,hr=(b[2]-b[0]+1)/w,(b[3]-b[1]+1)/h
            conf='high'
            if wr>0.95 and hr>0.95: conf='low'
            elif wr>0.9 or hr>0.9: conf='medium'

    x1,y1,x2,y2=b; sw,sh=x2-x1+1,y2-y1+1
    geom={'subject_bbox':{'left':x1,'top':y1,'right':x2,'bottom':y2},'subject_width_px':sw,'subject_height_px':sh,'subject_height_ratio':round(sh/h,4),'subject_width_ratio':round(sw/w,4),'margins':{'top':y1,'bottom':h-1-y2,'left':x1,'right':w-1-x2},'crop_risk':[],'confidence':conf,'method':method}
    if sh/h>0.9: geom['crop_risk'].append('主体过大')
    if sh/h<0.35: geom['crop_risk'].append('主体过小')
    if min(x1,y1,w-1-x2,h-1-y2)<8: geom['crop_risk'].append('接近裁切')
    if not geom['crop_risk']: geom['crop_risk']=['低']

    ar=sw/max(1,sh)
    product={'product_aspect_ratio':round(ar,4),'label_estimate':int(sh*0.42),'cap_estimate':int(sh*0.16),'label_height_ratio':0.42,'cap_height_ratio':0.16}

    ref={}
    if reference and Path(reference).exists():
        rim=Image.open(reference); rw,rh=rim.size; rb=[0,0,rw-1,rh-1]; rsh=rb[3]-rb[1]+1
        actual=(sh/h)/(rsh/max(1,rh)); exp=parse_pct(expected_height_change); expected=None if exp is None else 1+exp; diff=None if expected is None else actual-expected
        verdict='无法可靠判断'
        if expected is not None:
            if abs(actual-0.75)<=0.08: verdict='只是矮 25%'
            elif actual<=0.6: verdict='接近砍半'
            elif actual>0.85: verdict='高度变化不足'
        ref={'reference_subject_height_px':rsh,'current_subject_height_px':sh,'expected_ratio':expected,'actual_ratio':round(actual,4),'difference':None if diff is None else round(diff,4),'verdict':verdict}

    return {'image_info':{'filename':Path(image_path).name,'image_size':f'{w}x{h}','file_size':Path(image_path).stat().st_size},'color_analysis':{'average_brightness':brightness,'contrast':contrast,'saturation':sat,'casts':casts},'local_geometry':geom,'product_analysis':product,'reference_comparison':ref}

def render_detailed_markdown(out):
    info=out['image_info']; color=out['color_analysis']; geo=out['local_geometry']; prod=out['product_analysis']; st=out['vision_model_status']
    lines=['# 统一视觉分析报告','', '## 图像信息', f"- 文件名: {info['filename']}", f"- 尺寸: {info['image_size']}", f"- 文件大小: {info['file_size']} bytes", '', '## local-basic 颜色分析', f"- 平均亮度: {color['average_brightness']}", f"- 对比度: {color['contrast']}", f"- 饱和度: {color.get('saturation')}", f"- 偏色风险: {', '.join(color.get('casts') or ['none'])}", '', '## local-basic 几何分析', f"- 检测方法: {geo.get('method')}", f"- 置信度: {geo['confidence']}", f"- 主体框: {geo['subject_bbox']}", f"- 主体宽高比(相对画面): W={geo['subject_width_ratio']} H={geo['subject_height_ratio']}", f"- 边距: {geo['margins']}", f"- 裁切风险: {', '.join(geo['crop_risk'])}", '', '## 产品结构估计', f"- 产品宽高比: {prod['product_aspect_ratio']}", f"- 标签高度估计(px): {prod['label_estimate']}", f"- 瓶盖高度估计(px): {prod['cap_estimate']}"]
    if out.get('reference_comparison'):
        lines += ['', '## 参考图对比', f"- 对比结果: {out['reference_comparison']}"]
    lines += ['', '## 语义视觉状态', f"- local_basic_available: {str(st['local_basic_available']).lower()}", f"- semantic_vision_available: {str(st['semantic_vision_available']).lower()}", f"- vision_provider_used: {st['vision_provider_used']}", f"- fallback_to_local_basic: {str(st['fallback_to_local_basic']).lower()}", f"- fallback_reason: {st['fallback_reason']}", f"- error: {st['error']}"]
    sem=out.get('semantic_analysis',{})
    if sem:
        lines += ['', '## 语义输出', '```json', json.dumps(sem, ensure_ascii=False, indent=2), '```']
    return '\n'.join(lines)

def cmd_status(args):
    pkgs=['pillow','numpy','torch','transformers','accelerate','safetensors','sentencepiece','huggingface_hub']
    checks={}
    for p in pkgs: checks[p]=importlib.util.find_spec('PIL' if p=='pillow' else p) is not None
    checks['model_root_exists']=MODEL_ROOT.exists()
    for b in ['smolvlm2','moondream','florence2','qwen25vl']: checks[f'{b}_dir_exists']=(MODEL_ROOT/b).exists()
    od=now_dir(Path(args.output_dir)); md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    md.write_text('# Status\n'+'\n'.join([f'- {k}: {v}' for k,v in checks.items()]),encoding='utf-8')
    js.write_text(json.dumps({'status':checks},ensure_ascii=False,indent=2),encoding='utf-8')
    print(file_uri(md))

def cmd_install(args):
    backend=args.backend; model=args.model
    if not model:
        print('install-local-vlm 需要 --model',file=sys.stderr); sys.exit(1)
    target=MODEL_ROOT/backend/model.replace('/','__'); target.mkdir(parents=True,exist_ok=True)
    result={'backend':backend,'model':model,'target':str(target),'dry_run':not args.yes,'downloaded':False,'error':None,'warning':'下载模型不等于可推理，需本地 OpenAI-compatible 服务（LM Studio/Ollama/vLLM 等）已启动。'}
    if backend=='qwen25vl' and any(x in model.lower() for x in ['7b','14b','32b']): result['warning']+=' 模型较大，磁盘/显存压力高。'
    if args.yes:
        spec=importlib.util.find_spec('huggingface_hub')
        if spec is None:
            result['error']='缺少 huggingface_hub，请先安装。'
        else:
            try:
                from huggingface_hub import snapshot_download
                snapshot_download(repo_id=model, local_dir=str(target), local_dir_use_symlinks=False)
                result['downloaded']=True
            except Exception as e:
                result['error']=str(e)
    od=now_dir(Path(args.output_dir)); md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    md.write_text('# install-local-vlm\n'+'\n'.join([f'- {k}: {v}' for k,v in result.items()]),encoding='utf-8')
    js.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(file_uri(md))

def main():
    p=argparse.ArgumentParser(description='统一视觉分析工具')
    p.add_argument('command', nargs='?', default='analyze', choices=['analyze','status','install-local-vlm','analyze-local-vlm'])
    p.add_argument('--image'); p.add_argument('--brand',default='Generic'); p.add_argument('--industry',default=''); p.add_argument('--use-case',default='product photo',dest='use_case')
    p.add_argument('--mode',default='full',choices=MODES); p.add_argument('--analysis-depth',default='standard',choices=['basic','standard','deep'])
    p.add_argument('--scene-type',default='generic',choices=SCENES); p.add_argument('--object-type',default='generic',choices=OBJECTS)
    p.add_argument('--reference'); p.add_argument('--reference-dir'); p.add_argument('--expected-height-change'); p.add_argument('--text'); p.add_argument('--ratio'); p.add_argument('--use-alpha',action='store_true')
    p.add_argument('--use-vision',action='store_true'); p.add_argument('--vision-provider',default='none',choices=['none','qwen','gemini','openai','local']); p.add_argument('--vision-model',default='')
    p.add_argument('--ocr',action='store_true'); p.add_argument('--detect-people',action='store_true',default=True); p.add_argument('--detect-products',action='store_true',default=True); p.add_argument('--detect-layout',action='store_true',default=True)
    p.add_argument('--output-dir',default=str(OUT_ROOT)); p.add_argument('--json',action='store_true')
    p.add_argument('--backend',choices=BACKENDS,default='auto'); p.add_argument('--model'); p.add_argument('--prompt',default='Analyze image'); p.add_argument('--yes',action='store_true')
    p.add_argument('--no-external-vision',action='store_true')
    a=p.parse_args()

    if a.command=='status': return cmd_status(a)
    if a.command=='install-local-vlm': return cmd_install(a)
    if not a.image: print('缺少 --image',file=sys.stderr); sys.exit(1)

    local=local_cv_analysis(a.image,a.brand,a.scene_type,a.object_type,a.use_alpha,a.reference,a.expected_height_change)
    out={**local,'brand_design_analysis':{},'graphic_design_analysis':{},'style_consistency':{'note':'basic'},'ai_qc':{},'business_fit':{},
         'semantic_analysis':{'local_can_judge':['geometry','color','crop','proportion'],'need_vision':['label text','cap identity','scene objects','people','device logic']},
         'prompts':{},'scores':{},'confidence':{'subject':local['local_geometry']['confidence']},
         'vision_model_status':{'local_basic_available':True,'semantic_vision_available':False,'vision_provider_used':'none','fallback_reason':None,'error':None,'fallback_to_local_basic':True}}

    if a.use_vision:
        if a.no_external_vision and a.vision_provider in ['qwen','gemini','openai']:
            out['vision_model_status'].update({'vision_provider_used':a.vision_provider,'fallback_reason':'blocked_by_no_external_vision','error':'external vision disabled'})
        elif a.vision_provider=='qwen':
            key=os.getenv('DASHSCOPE_API_KEY')
            if not key:
                out['vision_model_status'].update({'vision_provider_used':'qwen','fallback_reason':'missing_api_key','error':'qwen_error = 缺少 DASHSCOPE_API_KEY'})
            else:
                try:
                    sem=openai_compat_vision(os.getenv('DASHSCOPE_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1'),key,a.vision_model or 'qwen-vl-plus',a.image,a.prompt)
                    out['semantic_analysis'].update(sem if isinstance(sem,dict) else {})
                    out['vision_model_status'].update({'semantic_vision_available':True,'vision_provider_used':'qwen','fallback_to_local_basic':False,'fallback_reason':None})
                except Exception as e:
                    out['vision_model_status'].update({'vision_provider_used':'qwen','fallback_reason':'remote_call_failed','error':str(e)})
        elif a.vision_provider=='local':
            sem,meta=local_openai_compat_vision(a.image,a.prompt,a.vision_model or os.getenv('LOCAL_VISION_MODEL'))
            out['vision_model_status'].update({'vision_provider_used':'local','fallback_reason':meta.get('fallback_reason'),'error':meta.get('error')})
            if sem is not None:
                out['semantic_analysis'].update(sem if isinstance(sem,dict) else {'raw_text':str(sem)})
                out['vision_model_status'].update({'semantic_vision_available':True,'fallback_to_local_basic':False,'fallback_reason':None,'error':None})

    od=now_dir(Path(a.output_dir)); md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    md.write_text(render_detailed_markdown(out),encoding='utf-8')
    js.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.json: print(json.dumps(out,ensure_ascii=False))
    print(file_uri(md))

if __name__=='__main__':
    main()
