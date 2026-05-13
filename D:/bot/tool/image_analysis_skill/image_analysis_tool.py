#!/usr/bin/env python3
import argparse, json, os, datetime as dt
from pathlib import Path

MODES=['basic','full','product-geometry','scene-detail','people-detail','semantic-full','brand-design','brand-full','graphic-design','style-consistency','commercial-qc','qc','prompt']
SCENES=['product_photo','factory_scene','sample_room','printing_workshop','warehouse','showroom','office','poster','banner','social_post','website_hero','generic']
OBJECTS=['bottle','jar','box','garment','factory','machine','poster','banner','generic']

def main():
    p=argparse.ArgumentParser(description='统一视觉分析工具')
    p.add_argument('--image',required=True)
    p.add_argument('--brand',default='Generic')
    p.add_argument('--industry',default='')
    p.add_argument('--use-case',default='product photo',dest='use_case')
    p.add_argument('--mode',default='full',choices=MODES)
    p.add_argument('--analysis-depth',default='standard',choices=['basic','standard','deep'])
    p.add_argument('--scene-type',default='generic',choices=SCENES)
    p.add_argument('--object-type',default='generic',choices=OBJECTS)
    p.add_argument('--reference'); p.add_argument('--reference-dir'); p.add_argument('--expected-height-change')
    p.add_argument('--text'); p.add_argument('--ratio'); p.add_argument('--use-alpha',action='store_true')
    p.add_argument('--use-vision',action='store_true'); p.add_argument('--vision-provider',default='none',choices=['none','qwen','gemini','openai','local']); p.add_argument('--vision-model',default='qwen-vl-plus')
    p.add_argument('--ocr',action='store_true'); p.add_argument('--detect-people',action='store_true',default=True); p.add_argument('--detect-products',action='store_true',default=True); p.add_argument('--detect-layout',action='store_true',default=True)
    p.add_argument('--output-dir',default='D:/bot/outputs/image_analysis'); p.add_argument('--json',action='store_true')
    a=p.parse_args()

    ip=Path(a.image)
    if not ip.exists(): raise SystemExit(f'图片不存在: {ip}')
    ts=dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    od=Path(a.output_dir)/ts; od.mkdir(parents=True,exist_ok=True)
    md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    result={'image_info':{'filename':ip.name,'mode':a.mode},'vision_model_status':{'enabled':a.use_vision,'provider':a.vision_provider,'model':a.vision_model,'success':False,'fallback_to_local':True,'error':None}}
    md.write_text('# 统一视觉分析报告\n- 模式: '+a.mode,encoding='utf-8')
    js.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.json: print(json.dumps(result,ensure_ascii=False))
    print(f'FILE:file:///{md.as_posix()}')

if __name__=='__main__':
    main()
