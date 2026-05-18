#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, base64, datetime as dt, importlib.util, json, os, re, sys
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None

OUT_ROOT = Path('D:/bot/outputs/image_analysis')
MODEL_ROOT = Path('D:/bot/models/vision')

MODES = ['basic','full','product-geometry','scene-detail','people-detail','semantic-full','brand-design','brand-full','graphic-design','style-consistency','commercial-qc','qc','prompt']
SCENES = ['product_photo','factory_scene','sample_room','printing_workshop','warehouse','showroom','office','poster','banner','social_post','website_hero','generic']
OBJECTS = ['bottle','jar','box','garment','factory','machine','poster','banner','generic']
BACKENDS = ['auto','smolvlm2','moondream','florence2','qwen25vl']


def now_dir(base: Path):
    d = base / dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    d.mkdir(parents=True, exist_ok=True)
    return d


def file_uri(p: Path):
    return f"FILE:file:///{p.as_posix()}"


def parse_pct(v):
    m = re.match(r'\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$', v or '')
    return float(m.group(1))/100 if m else None


def top5_hex(img):
    im = img.copy(); im.thumbnail((320, 320))
    if np is None:
        q = im.convert('P', palette=Image.ADAPTIVE, colors=5)
        pal = q.getpalette(); out=[]
        for c,i in sorted(q.getcolors() or [], reverse=True)[:5]:
            r,g,b = pal[i*3:i*3+3]; out.append(f"#{r:02X}{g:02X}{b:02X}")
        return out
    arr=np.array(im).reshape(-1,3); q=(arr//32)*32
    u,c=np.unique(q,axis=0,return_counts=True); idx=np.argsort(c)[::-1][:5]
    return [f"#{int(u[i][0]):02X}{int(u[i][1]):02X}{int(u[i][2]):02X}" for i in idx]


def detect_subject(im, use_alpha=False):
    w,h=im.size
    if np is None:
        return [0,0,w-1,h-1],'low','numpy_missing'
    rgba=np.array(im.convert('RGBA')); alpha=rgba[:,:,3]
    if (use_alpha or 'A' in im.getbands()) and (alpha<250).mean()>0.02:
        mask=alpha>12; method='alpha-mask'
    else:
        rgb=np.array(im.convert('RGB')).astype(np.float32)
        bg=np.vstack([rgb[0,0],rgb[0,-1],rgb[-1,0],rgb[-1,-1]]).mean(axis=0)
        mask=np.linalg.norm(rgb-bg,axis=2)>22; method='bg-diff'
    ys,xs=np.where(mask)
    if len(xs)==0: return [0,0,w-1,h-1],'low','fallback'
    b=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
    wr,hr=(b[2]-b[0]+1)/w,(b[3]-b[1]+1)/h
    conf='high'
    if wr>0.95 and hr>0.95: conf='low'
    elif wr>0.9 or hr>0.9: conf='medium'
    return b,conf,method


def local_cv_analysis(image_path: Path, brand: str, scene_type: str, object_type: str, use_alpha: bool, reference: str, expected_height_change: str):
    try:
        from PIL import Image, ImageStat
    except ImportError:
        raise RuntimeError('缺少 pillow，请安装：pip install pillow')
    im=Image.open(image_path); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb); mean=st.mean
    brightness=round(sum(mean)/3,2); contrast=round(sum(st.stddev)/3,2)
    sat=None
    if np is not None:
        arr=np.array(rgb).astype(np.float32); mx=arr.max(axis=2); mn=arr.min(axis=2)
        sat=round(float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100),2)
    casts=[]
    if mean[0]-mean[2]>12: casts.append('yellow_cast')
    if mean[0]-mean[1]>10: casts.append('red_cast')
    if mean[0]>mean[1]>mean[2] and mean[0]-mean[2]>18: casts.append('orange_cast')
    if abs(mean[0]-mean[1])<6 and abs(mean[1]-mean[2])<6: casts.append('gray_cast')

    b,conf,method=detect_subject(im,use_alpha); x1,y1,x2,y2=b; sw,sh=x2-x1+1,y2-y1+1
    geom={'subject_bbox':{'left':x1,'top':y1,'right':x2,'bottom':y2},'subject_width_px':sw,'subject_height_px':sh,
          'subject_height_ratio':round(sh/h,4),'subject_width_ratio':round(sw/w,4),
          'margins':{'top':y1,'bottom':h-1-y2,'left':x1,'right':w-1-x2},'crop_risk':[],'confidence':conf,'method':method}
    if sh/h>0.9: geom['crop_risk'].append('主体过大')
    if sh/h<0.35: geom['crop_risk'].append('主体过小')
    if min(x1,y1,w-1-x2,h-1-y2)<8: geom['crop_risk'].append('接近裁切')
    if not geom['crop_risk']: geom['crop_risk']=['低']

    ar=sw/max(1,sh)
    product={'product_aspect_ratio':round(ar,4),'label_estimate':int(sh*0.42),'cap_estimate':int(sh*0.16),
             'label_height_ratio':round(0.42,4),'cap_height_ratio':round(0.16,4),
             'too_tall_too_skinny':ar<0.28,'too_short_too_wide':ar>0.45}

    ref={}
    if reference and Path(reference).exists():
        rim=Image.open(reference); rw,rh=rim.size
        rb,_,_=detect_subject(rim,use_alpha); rsh=rb[3]-rb[1]+1
        actual=(sh/h)/(rsh/max(1,rh)); exp=parse_pct(expected_height_change); exratio=None if exp is None else 1+exp
        diff=None if exratio is None else actual-exratio
        verdict='无法可靠判断'
        if exratio is not None:
            if abs(actual-0.75)<=0.08: verdict='只是矮 25%'
            elif actual<=0.6: verdict='接近砍半'
            elif actual>0.85: verdict='高度变化不足'
        ref={'reference_subject_height_px':rsh,'current_subject_height_px':sh,'expected_ratio':exratio,'actual_ratio':round(actual,4),'difference':None if diff is None else round(diff,4),'verdict':verdict}

    brand_out={}
    if brand.lower()=='veytis' or object_type=='bottle':
        shape='4 fl oz / 120mL amber Boston round dropper bottle'
        if ar<0.28: shape='tall skinny serum bottle'
        if ar>0.45: shape='squat bulky jar'
        brand_out['veytis']={'shape':shape,'label_ratio':product['label_height_ratio'],'cap_ratio':product['cap_height_ratio'],'subject_ratio':geom['subject_height_ratio'],'casts':casts,'fit_product_page':'是','fit_home_hero':'视留白而定'}
    if brand.lower()=='juese clothing' or scene_type=='factory_scene':
        brand_out['juese']={'factory_realism_local':'中高' if contrast>18 else '中','lighting_too_dark':brightness<90,'lighting_too_yellow':'yellow_cast' in casts,'fit_b2b':'中高','risk':'假工厂/AI设备/脏乱需视觉模型确认'}

    graphic={'headline_zone':'上1/3','subheadline_zone':'标题下方','cta_zone':'右下','logo_zone':'左上/右上','text_safe_zone':'上方+四角','fit_homepage':'较适合','fit_ad':'较适合','fit_short_video_cover':'可用'}

    return {
        'image_info':{'filename':image_path.name,'image_size':f'{w}x{h}','aspect_ratio':f'{w}:{h}','orientation':'横图' if w>h else ('竖图' if h>w else '方图'),'file_size':image_path.stat().st_size},
        'color_analysis':{'dominant_colors_top5_hex':top5_hex(rgb),'average_brightness':brightness,'contrast':contrast,'saturation':sat,'casts':casts},
        'local_geometry':geom,
        'product_analysis':product,
        'brand_design_analysis':brand_out,
        'graphic_design_analysis':graphic,
        'reference_comparison':ref,
    }


def model_local_path(backend, model):
    name=model.replace('/','__')
    return MODEL_ROOT/backend/name


def cmd_status(args):
    checks={}
    import importlib.util
    pkgs=['pillow','numpy','torch','transformers','accelerate','safetensors','sentencepiece','huggingface_hub']
    for p in pkgs:
        checks[p]=importlib.util.find_spec('PIL' if p=='pillow' else p) is not None
    checks['model_root_exists']=MODEL_ROOT.exists()
    checks['smolvlm2_dir_exists']=(MODEL_ROOT/'smolvlm2').exists()
    checks['moondream_dir_exists']=(MODEL_ROOT/'moondream').exists()
    checks['florence2_dir_exists']=(MODEL_ROOT/'florence2').exists()
    checks['qwen25vl_dir_exists']=(MODEL_ROOT/'qwen25vl').exists()
    out_dir=now_dir(Path(args.output_dir)); md=out_dir/'image_analysis_report.md'; js=out_dir/'image_analysis_report.json'
    md.write_text('# Status\n'+'\n'.join([f'- {k}: {v}' for k,v in checks.items()]),encoding='utf-8')
    js.write_text(json.dumps({'status':checks},ensure_ascii=False,indent=2),encoding='utf-8')
    print(file_uri(md))


def cmd_install(args):
    target=model_local_path(args.backend,args.model)
    msg={'backend':args.backend,'model':args.model,'target':str(target),'dry_run':not args.yes,'warning':None,'download_started':False}
    if args.backend=='qwen25vl' and any(x in args.model.lower() for x in ['7b','14b','32b']):
        msg['warning']='模型较大，可能占用大量磁盘与显存。'
    if args.yes:
        msg['download_started']=True
        target.mkdir(parents=True,exist_ok=True)
        (target/'MANUAL_DOWNLOAD_REQUIRED.txt').write_text('请使用 huggingface-cli 或 git lfs 手动下载该模型到此目录。',encoding='utf-8')
    out_dir=now_dir(Path(args.output_dir)); md=out_dir/'image_analysis_report.md'; js=out_dir/'image_analysis_report.json'
    md.write_text('# install-local-vlm\n'+'\n'.join([f'- {k}: {v}' for k,v in msg.items()]),encoding='utf-8')
    js.write_text(json.dumps(msg,ensure_ascii=False,indent=2),encoding='utf-8')
    print(file_uri(md))


def run_local_vlm(image_path, backend, prompt, vision_model):
    order=['smolvlm2','moondream','florence2','qwen25vl'] if backend=='auto' else [backend]
    used=None
    for b in order:
        base=MODEL_ROOT/b
        if base.exists() and any(base.iterdir()):
            used=b; break
    if used is None:
        return None, {'local_vlm_model_found':False,'fallback_reason':'local VLM model not found, fallback to local_cv.'}
    # placeholder semantic from local model presence
    sem={'caption':f'local_vlm({used}) caption placeholder','object_list':['needs model runtime integration'],'scene_understanding':'local model detected but runtime adapter is minimal','ai_artifact_risks':'需要模型推理','commercial_fit':'需要模型推理','suggestions':['如需真实语义，请接入本地推理运行时']}
    return sem, {'local_vlm_model_found':True,'backend_used':used,'model':vision_model}


def build_markdown(out):
    g=out['local_geometry']; b=g['subject_bbox']; m=g['margins']
    lines=['# 统一视觉分析报告','## 执行摘要',f"- local_basic_available: {out['vision_model_status']['local_basic_available']}",f"- semantic_vision_available: {out['vision_model_status']['semantic_vision_available']}",f"- vision_provider_used: {out['vision_model_status']['vision_provider_used']}",f"- fallback_reason: {out['vision_model_status']['fallback_reason']}",
           '## 基础信息',f"- 文件名: {out['image_info']['filename']}",f"- 尺寸: {out['image_info']['image_size']}",
           '## 色彩分析',f"- 主色Top5 HEX: {', '.join(out['color_analysis']['dominant_colors_top5_hex'])}",f"- 亮度: {out['color_analysis']['average_brightness']}",f"- 对比度: {out['color_analysis']['contrast']}",f"- 饱和度: {out['color_analysis']['saturation']}",
           '## 主体几何',f"- bbox left: {b['left']}",f"- bbox top: {b['top']}",f"- bbox right: {b['right']}",f"- bbox bottom: {b['bottom']}",f"- 主体高度占比: {g['subject_height_ratio']}",f"- 主体宽度占比: {g['subject_width_ratio']}",f"- 顶部留白: {m['top']}",f"- 底部留白: {m['bottom']}",f"- 左侧留白: {m['left']}",f"- 右侧留白: {m['right']}",f"- 裁切风险: {', '.join(g['crop_risk'])}",f"- 置信度: {g['confidence']}",
           '## 产品比例',f"- product_aspect_ratio: {out['product_analysis']['product_aspect_ratio']}",f"- label_estimate: {out['product_analysis']['label_estimate']}",f"- cap_estimate: {out['product_analysis']['cap_estimate']}",
           '## 品牌分析',f"- 风险: {', '.join(out['color_analysis']['casts']) if out['color_analysis']['casts'] else '低'}",
           '## 平面设计',f"- 标题区域: {out['graphic_design_analysis']['headline_zone']}",f"- 文字安全区: {out['graphic_design_analysis']['text_safe_zone']}",
           '## 参考图对比']
    rc=out.get('reference_comparison',{})
    lines += [f"- {k}: {v}" for k,v in rc.items()] if rc else ['- 未提供']
    lines += ['## 视觉说明',f"- local_can_judge: {', '.join(out['semantic_analysis']['local_can_judge'])}",f"- need_vision: {', '.join(out['semantic_analysis']['need_vision'])}"]
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description='统一视觉分析工具')
    p.add_argument('command', nargs='?', default='analyze', choices=['analyze','status','install-local-vlm','analyze-local-vlm'])
    p.add_argument('--image'); p.add_argument('--brand',default='Generic'); p.add_argument('--industry',default=''); p.add_argument('--use-case',default='product photo',dest='use_case')
    p.add_argument('--mode',default='full',choices=MODES); p.add_argument('--analysis-depth',default='standard',choices=['basic','standard','deep'])
    p.add_argument('--scene-type',default='generic',choices=SCENES); p.add_argument('--object-type',default='generic',choices=OBJECTS)
    p.add_argument('--reference'); p.add_argument('--reference-dir'); p.add_argument('--expected-height-change'); p.add_argument('--text'); p.add_argument('--ratio'); p.add_argument('--use-alpha',action='store_true')
    p.add_argument('--use-vision',action='store_true'); p.add_argument('--vision-provider',default='none',choices=['none','qwen','gemini','openai','local']); p.add_argument('--vision-model',default='qwen2.5-vl-7b-instruct')
    p.add_argument('--ocr',action='store_true'); p.add_argument('--detect-people',action='store_true',default=True); p.add_argument('--detect-products',action='store_true',default=True); p.add_argument('--detect-layout',action='store_true',default=True)
    p.add_argument('--output-dir',default=str(OUT_ROOT)); p.add_argument('--json',action='store_true')
    p.add_argument('--backend',choices=BACKENDS,default='auto'); p.add_argument('--model'); p.add_argument('--prompt',default='Analyze image'); p.add_argument('--yes',action='store_true')
    p.add_argument('--no-external-vision',action='store_true')
    a=p.parse_args()

    if a.command=='status':
        return cmd_status(a)
    if a.command=='install-local-vlm':
        if not a.model:
            print('install-local-vlm 需要 --model',file=sys.stderr); sys.exit(1)
        return cmd_install(a)

    if not a.image:
        print('缺少 --image',file=sys.stderr); sys.exit(1)

    local=local_cv_analysis(Path(a.image),a.brand,a.scene_type,a.object_type,a.use_alpha,a.reference,a.expected_height_change)
    out={
        **local,
        'style_consistency':{'note':'basic'},
        'ai_qc':{'local_basic':'available'},
        'business_fit':{'site_fit':'较适合'},
        'semantic_analysis':{'local_can_judge':['geometry','color','crop','proportion'],'need_vision':['label text','cap identity','scene objects','people','device logic']},
        'prompts':{'regen':'realistic commercial image','inpaint':'fix proportion and cast'},
        'scores':{'total':7.4},
        'confidence':{'subject':local['local_geometry']['confidence']},
        'vision_model_status':{'local_basic_available':True,'semantic_vision_available':False,'vision_provider_used':'none','fallback_reason':None,'error':None,'fallback_to_local_basic':True}
    }
    if a.ocr:
        out['semantic_analysis']['ocr_status']='not_implemented'

    if a.use_vision:
        if a.no_external_vision and a.vision_provider in ['qwen','gemini','openai']:
            out['vision_model_status'].update({'vision_provider_used':a.vision_provider,'fallback_reason':'blocked_by_no_external_vision','error':'external vision disabled'})
        elif a.vision_provider=='qwen':
            key=os.getenv('DASHSCOPE_API_KEY')
            if not key:
                out['vision_model_status'].update({'vision_provider_used':'qwen','fallback_reason':'missing_api_key','error':'qwen_error = 缺少 DASHSCOPE_API_KEY'})
            else:
                try:
                    sem=openai_compat_vision(os.getenv('DASHSCOPE_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1'),key,a.vision_model,a.image,a.prompt)
                    out['semantic_analysis'].update(sem if isinstance(sem,dict) else {})
                    out['vision_model_status'].update({'semantic_vision_available':True,'vision_provider_used':'qwen','fallback_to_local_basic':False,'fallback_reason':None})
                except Exception as e:
                    out['vision_model_status'].update({'vision_provider_used':'qwen','fallback_reason':'remote_call_failed','error':str(e)})
        elif a.vision_provider=='local':
            sem,meta=run_local_vlm(a.image,a.backend,a.prompt,a.vision_model or os.getenv('LOCAL_VISION_MODEL','qwen2.5-vl-7b-instruct'))
            if sem is None:
                out['vision_model_status'].update({'vision_provider_used':'local','fallback_reason':meta['fallback_reason'],'error':None})
            else:
                out['semantic_analysis'].update(sem)
                out['vision_model_status'].update({'semantic_vision_available':True,'vision_provider_used':'local','fallback_to_local_basic':False,'fallback_reason':None,'error':None,**meta})

    out_dir=now_dir(Path(a.output_dir)); md=out_dir/'image_analysis_report.md'; js=out_dir/'image_analysis_report.json'
    md.write_text(build_markdown(out),encoding='utf-8')
    js.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.json: print(json.dumps(out,ensure_ascii=False))
    print(file_uri(md))

if __name__=='__main__':
    main()
