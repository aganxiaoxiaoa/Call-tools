#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, datetime as dt, json, os, re, sys
from pathlib import Path
from urllib import request

MODES=['basic','full','product-geometry','scene-detail','people-detail','semantic-full','brand-design','brand-full','graphic-design','style-consistency','commercial-qc','qc','prompt']
SCENES=['product_photo','factory_scene','sample_room','printing_workshop','warehouse','showroom','office','poster','banner','social_post','website_hero','generic']
OBJECTS=['bottle','jar','box','garment','factory','machine','poster','banner','generic']


def qwen_vision(image_path,prompt,model):
    key=os.getenv('DASHSCOPE_API_KEY')
    if not key: raise RuntimeError('缺少 DASHSCOPE_API_KEY')
    base=os.getenv('DASHSCOPE_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1').rstrip('/')
    schema='请仅返回JSON: scene_detail,people_detail,object_inventory,product_semantic_analysis,factory_logic_analysis,brand_visual_analysis,graphic_design_analysis,text_or_label_observation,ai_artifact_risks,commercial_fit,suggestions'
    payload={'model':model or 'qwen-vl-plus','messages':[{'role':'user','content':[{'type':'text','text':schema+'\n'+prompt},{'type':'image_url','image_url':{'url':'file:///'+image_path.replace('\\','/')}}]}]}
    req=request.Request(base+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
    with request.urlopen(req,timeout=45) as r:data=json.loads(r.read().decode('utf-8','ignore'))
    txt=((data.get('choices') or [{}])[0].get('message') or {}).get('content','{}')
    try:return json.loads(txt)
    except Exception:return {'raw_text':txt}


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

    ip=Path(a.image)
    if not ip.exists(): print(f'错误：图片不存在：{ip}',file=sys.stderr); sys.exit(1)

    vision={'enabled':a.use_vision,'provider':a.vision_provider,'model':a.vision_model,'success':False,'fallback_to_local':True,'error':None}
    semantic={'note':'未开启视觉模型，本地模式输出。'}
    if a.use_vision and a.vision_provider=='qwen':
        try:
            semantic=qwen_vision(str(ip),'分析场景/人物/产品/设计',a.vision_model)
            vision['success']=True; vision['fallback_to_local']=False
        except Exception as e:
            vision['error']=str(e)

    out={'image_info':{'filename':ip.name,'mode':a.mode},'color_analysis':{},'local_geometry':{},'scene_detail':{},'people_detail':{},'object_inventory':{},'product_analysis':{},'brand_design_analysis':{},'graphic_design_analysis':{},'style_consistency':{},'ai_qc':{},'business_fit':{},'reference_comparison':{},'semantic_analysis':semantic,'prompts':{},'scores':{},'confidence':{},'vision_model_status':vision}

    ts=dt.datetime.now().strftime('%Y%m%d-%H%M%S'); od=Path(a.output_dir)/ts; od.mkdir(parents=True,exist_ok=True)
    md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    md.write_text('# 统一视觉分析报告\n- 模式: '+a.mode,encoding='utf-8')
    js.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.json: print(json.dumps(out,ensure_ascii=False))
    print(f'FILE:file:///{md.as_posix()}')

if __name__=='__main__':
    main()
