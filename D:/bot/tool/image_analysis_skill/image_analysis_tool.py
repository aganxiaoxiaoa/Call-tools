#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, base64, datetime as dt, json, os, re, sys
from pathlib import Path
from urllib import request

MODES=['basic','full','product-geometry','scene-detail','people-detail','semantic-full','brand-design','brand-full','graphic-design','style-consistency','commercial-qc','qc','prompt']
SCENES=['product_photo','factory_scene','sample_room','printing_workshop','warehouse','showroom','office','poster','banner','social_post','website_hero','generic']
OBJECTS=['bottle','jar','box','garment','factory','machine','poster','banner','generic']


def parse_pct(v):
    m=re.match(r'\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$',v or '')
    return float(m.group(1))/100 if m else None

def to_data_url(path):
    ext=Path(path).suffix.lower().strip('.')
    mt={'jpg':'image/jpeg','jpeg':'image/jpeg','png':'image/png','webp':'image/webp'}.get(ext,'image/png')
    return f"data:{mt};base64,"+base64.b64encode(Path(path).read_bytes()).decode('ascii')

def openai_compat_vision(base,key,model,image_path,prompt):
    schema='仅返回JSON: scene_detail,people_detail,object_inventory,product_semantic_analysis,factory_logic_analysis,brand_visual_analysis,graphic_design_analysis,text_or_label_observation,ai_artifact_risks,commercial_fit,suggestions'
    payload={'model':model,'messages':[{'role':'user','content':[{'type':'text','text':schema+'\n'+prompt},{'type':'image_url','image_url':{'url':to_data_url(image_path)}}]}]}
    req=request.Request(base.rstrip('/')+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
    with request.urlopen(req,timeout=45) as r:data=json.loads(r.read().decode('utf-8','ignore'))
    txt=((data.get('choices') or [{}])[0].get('message') or {}).get('content','{}')
    try:return json.loads(txt)
    except: return {'raw_text':txt}

def main():
    p=argparse.ArgumentParser(description='统一视觉分析工具')
    p.add_argument('--image',required=True); p.add_argument('--brand',default='Generic'); p.add_argument('--industry',default=''); p.add_argument('--use-case',default='product photo',dest='use_case')
    p.add_argument('--mode',default='full',choices=MODES); p.add_argument('--analysis-depth',default='standard',choices=['basic','standard','deep'])
    p.add_argument('--scene-type',default='generic',choices=SCENES); p.add_argument('--object-type',default='generic',choices=OBJECTS)
    p.add_argument('--reference'); p.add_argument('--reference-dir'); p.add_argument('--expected-height-change'); p.add_argument('--text'); p.add_argument('--ratio'); p.add_argument('--use-alpha',action='store_true')
    p.add_argument('--use-vision',action='store_true'); p.add_argument('--vision-provider',default='none',choices=['none','qwen','gemini','openai','local']); p.add_argument('--vision-model',default='qwen-vl-plus')
    p.add_argument('--ocr',action='store_true'); p.add_argument('--detect-people',action='store_true',default=True); p.add_argument('--detect-products',action='store_true',default=True); p.add_argument('--detect-layout',action='store_true',default=True)
    p.add_argument('--output-dir',default='D:/bot/outputs/image_analysis'); p.add_argument('--json',action='store_true')
    a=p.parse_args()

    from PIL import Image, ImageStat
    try: import numpy as np
    except ImportError: np=None

    ip=Path(a.image)
    if not ip.exists(): print('图片不存在',file=sys.stderr); sys.exit(1)

    im=Image.open(ip); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb)
    mean=st.mean; brightness=round(sum(mean)/3,2); contrast=round(sum(st.stddev)/3,2)

    # local-basic
    casts=[]
    if mean[0]-mean[2]>12: casts.append('yellow_cast')
    if mean[0]-mean[1]>10: casts.append('red_cast')
    if mean[0]>mean[1]>mean[2] and mean[0]-mean[2]>18: casts.append('orange_cast')
    if abs(mean[0]-mean[1])<6 and abs(mean[1]-mean[2])<6: casts.append('gray_cast')

    if np is None:
        bbox=[0,0,w-1,h-1]; conf='low'; sat=None
    else:
        arr=np.array(rgb).astype(np.float32); mx=arr.max(axis=2); mn=arr.min(axis=2); sat=round(float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100),2)
        alpha=np.array(im.convert('RGBA'))[:,:,3]
        if (a.use_alpha or 'A' in im.getbands()) and (alpha<250).mean()>0.02: mask=alpha>12
        else:
            bg=np.vstack([arr[0,0],arr[0,-1],arr[-1,0],arr[-1,-1]]).mean(axis=0); mask=np.linalg.norm(arr-bg,axis=2)>22
        ys,xs=np.where(mask)
        bbox=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else [0,0,w-1,h-1]
        wr,hr=(bbox[2]-bbox[0]+1)/w,(bbox[3]-bbox[1]+1)/h
        conf='high'
        if wr>0.95 and hr>0.95: conf='low'
        elif wr>0.9 or hr>0.9: conf='medium'

    x1,y1,x2,y2=bbox; sw,sh=x2-x1+1,y2-y1+1
    geom={'subject_bbox':{'left':x1,'top':y1,'right':x2,'bottom':y2},'subject_width_px':sw,'subject_height_px':sh,'subject_height_ratio':round(sh/h,4),'subject_width_ratio':round(sw/w,4),'margins':{'top':y1,'bottom':h-1-y2,'left':x1,'right':w-1-x2},'crop_risk':[],'confidence':conf}
    if sh/h>0.9: geom['crop_risk'].append('主体过大')
    if sh/h<0.35: geom['crop_risk'].append('主体过小')
    if min(x1,y1,w-1-x2,h-1-y2)<8: geom['crop_risk'].append('接近裁切')
    if not geom['crop_risk']: geom['crop_risk']=['低']

    ar=sw/max(1,sh); product={'product_aspect_ratio':round(ar,4),'label_estimate':int(sh*0.42),'cap_estimate':int(sh*0.16),'label_height_ratio':round(0.42,4),'cap_height_ratio':round(0.16,4)}

    ref={}
    if a.reference and Path(a.reference).exists():
        rim=Image.open(a.reference); rw,rh=rim.size
        rb=[0,0,rw-1,rh-1] if np is None else [0,0,rw-1,rh-1]
        rsh=rb[3]-rb[1]+1; actual=(sh/h)/(rsh/max(1,rh)); exp=parse_pct(a.expected_height_change); expected=None if exp is None else 1+exp; diff=None if expected is None else actual-expected
        verdict='无法可靠判断'
        if expected is not None:
            if abs(actual-0.75)<=0.08: verdict='只是矮 25%'
            elif actual<=0.6: verdict='接近砍半'
            elif actual>0.85: verdict='高度变化不足'
        ref={'reference_subject_height_px':rsh,'current_subject_height_px':sh,'expected_ratio':expected,'actual_ratio':round(actual,4),'difference':None if diff is None else round(diff,4),'verdict':verdict}

    # vision status
    vision={'local_basic_available':True,'semantic_vision_available':False,'vision_provider_used':'none','fallback_reason':None,'error':None,'fallback_to_local_basic':True}
    semantic={'local_can_judge':['geometry','color','crop','proportion'],'need_vision':['label text','cap identity','scene objects','people','device logic']}
    if a.ocr: semantic['ocr_status']='not_implemented'
    if a.use_vision:
        if a.vision_provider=='qwen':
            key=os.getenv('DASHSCOPE_API_KEY')
            if not key:
                vision.update({'vision_provider_used':'qwen','error':'qwen_error = 缺少 DASHSCOPE_API_KEY','fallback_reason':'missing_api_key'})
            else:
                try:
                    sem=openai_compat_vision(os.getenv('DASHSCOPE_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1'),key,a.vision_model,str(ip),'分析场景语义和人物细节')
                    semantic.update(sem if isinstance(sem,dict) else {}); vision.update({'semantic_vision_available':True,'vision_provider_used':'qwen','fallback_to_local_basic':False,'fallback_reason':None})
                except Exception as e:
                    vision.update({'vision_provider_used':'qwen','error':str(e),'fallback_reason':'remote_call_failed'})
        elif a.vision_provider=='local':
            base=os.getenv('LOCAL_VISION_BASE_URL','http://127.0.0.1:1234/v1')
            key=os.getenv('LOCAL_VISION_API_KEY','lm-studio')
            model=a.vision_model or os.getenv('LOCAL_VISION_MODEL','qwen2.5-vl-7b-instruct')
            try:
                sem=openai_compat_vision(base,key,model,str(ip),'分析场景语义和人物细节')
                semantic.update(sem if isinstance(sem,dict) else {}); vision.update({'semantic_vision_available':True,'vision_provider_used':'local','fallback_to_local_basic':False,'fallback_reason':None})
            except Exception as e:
                vision.update({'vision_provider_used':'local','error':str(e),'fallback_reason':'local_endpoint_unavailable'})

    out={'image_info':{'filename':ip.name,'image_size':f'{w}x{h}','file_size':ip.stat().st_size},'color_analysis':{'average_brightness':brightness,'contrast':contrast,'saturation':sat,'casts':casts},'local_geometry':geom,'product_analysis':product,'brand_design_analysis':{},'graphic_design_analysis':{},'style_consistency':{'note':'basic'},'ai_qc':{},'business_fit':{},'reference_comparison':ref,'semantic_analysis':semantic,'prompts':{},'scores':{},'confidence':{'subject':conf},'vision_model_status':vision}

    md=['# 统一视觉分析报告','## 执行摘要',f"- local_basic_available: true",f"- semantic_vision_available: {str(vision['semantic_vision_available']).lower()}",f"- vision_provider_used: {vision['vision_provider_used']}",f"- fallback_reason: {vision['fallback_reason']}",
        '## 基础信息',f"- 尺寸: {w}x{h}",f"- 文件大小: {ip.stat().st_size}",
        '## 色彩分析',f"- 亮度: {brightness}",f"- 对比度: {contrast}",f"- 饱和度: {sat}",f"- 偏色: {', '.join(casts) if casts else '低'}",
        '## 主体几何',f"- bbox left: {x1}",f"- bbox top: {y1}",f"- bbox right: {x2}",f"- bbox bottom: {y2}",f"- 主体高度占比: {geom['subject_height_ratio']}",f"- 主体宽度占比: {geom['subject_width_ratio']}",f"- 裁切风险: {', '.join(geom['crop_risk'])}",f"- 置信度: {conf}",
        '## 产品比例',f"- product_aspect_ratio: {product['product_aspect_ratio']}",f"- label_estimate: {product['label_estimate']}",f"- cap_estimate: {product['cap_estimate']}",
        '## 参考图对比'] + ([f"- {k}: {v}" for k,v in ref.items()] if ref else ['- 未提供']) + ['## 视觉说明',f"- local_can_judge: {', '.join(semantic['local_can_judge'])}",f"- need_vision: {', '.join(semantic['need_vision'])}"]

    ts=dt.datetime.now().strftime('%Y%m%d-%H%M%S'); od=Path(a.output_dir)/ts; od.mkdir(parents=True,exist_ok=True)
    mdp=od/'image_analysis_report.md'; jsp=od/'image_analysis_report.json'
    mdp.write_text('\n'.join(md),encoding='utf-8'); jsp.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.json: print(json.dumps(out,ensure_ascii=False))
    print(f'FILE:file:///{mdp.as_posix()}')

if __name__=='__main__':
    main()
