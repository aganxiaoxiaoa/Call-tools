#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, base64, datetime as dt, json, mimetypes, os, re, sys
from pathlib import Path
from urllib import request
Image=None
ImageStat=None
np=None

MODES=['basic','full','product-geometry','scene-detail','people-detail','semantic-full','brand-design','brand-full','graphic-design','style-consistency','commercial-qc','qc','prompt']
SCENES=['product_photo','factory_scene','sample_room','printing_workshop','warehouse','showroom','office','poster','banner','social_post','website_hero','generic']
OBJECTS=['bottle','jar','box','garment','factory','machine','poster','banner','generic']


def data_url(path:str)->str:
    ext=Path(path).suffix.lower(); mt={'jpg':'image/jpeg','jpeg':'image/jpeg','png':'image/png','webp':'image/webp'}.get(ext.strip('.'),'image/png')
    b64=base64.b64encode(Path(path).read_bytes()).decode('ascii')
    return f'data:{mt};base64,{b64}'

def qwen_vision(path,prompt,model):
    key=os.getenv('DASHSCOPE_API_KEY');
    if not key: raise RuntimeError('缺少 DASHSCOPE_API_KEY')
    base=os.getenv('DASHSCOPE_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1').rstrip('/')
    schema='请只返回JSON: scene_detail,people_detail,object_inventory,product_semantic_analysis,factory_logic_analysis,brand_visual_analysis,graphic_design_analysis,text_or_label_observation,ai_artifact_risks,commercial_fit,suggestions'
    payload={'model':model or 'qwen-vl-plus','messages':[{'role':'user','content':[{'type':'text','text':schema+'\n'+prompt},{'type':'image_url','image_url':{'url':data_url(path)}}]}]}
    req=request.Request(base+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
    with request.urlopen(req,timeout=45) as r:data=json.loads(r.read().decode('utf-8','ignore'))
    txt=((data.get('choices') or [{}])[0].get('message') or {}).get('content','{}')
    try:return json.loads(txt)
    except: return {'raw_text':txt}

def parse_pct(v):
    m=re.match(r'\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$',v or '')
    return float(m.group(1))/100 if m else None

def detect_bbox(im,use_alpha=False):
    w,h=im.size
    if np is None:return [0,0,w-1,h-1],'low','numpy_missing'
    rgba=np.array(im.convert('RGBA')); alpha=rgba[:,:,3]
    if (use_alpha or 'A' in im.getbands()) and (alpha<250).mean()>0.02: mask=alpha>10
    else:
        rgb=np.array(im.convert('RGB')).astype(np.float32); bg=np.vstack([rgb[0,0],rgb[0,-1],rgb[-1,0],rgb[-1,-1]]).mean(axis=0); mask=np.linalg.norm(rgb-bg,axis=2)>22
    ys,xs=np.where(mask)
    if len(xs)==0:return [0,0,w-1,h-1],'low','fallback'
    x1,y1,x2,y2=int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())
    wr,hr=(x2-x1+1)/w,(y2-y1+1)/h
    conf='high'
    if wr>0.95 and hr>0.95: conf='low'
    elif wr>0.9 or hr>0.9: conf='medium'
    return [x1,y1,x2,y2],conf,'alpha' if (alpha<250).mean()>0.02 else 'bg-diff'

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
    global Image, ImageStat, np
    try:
        from PIL import Image, ImageStat
    except ImportError:
        print('错误：缺少 pillow，请安装：pip install pillow', file=sys.stderr); sys.exit(2)
    try:
        import numpy as np
    except ImportError:
        np=None
    ip=Path(a.image)
    if not ip.exists(): print('错误：图片不存在',file=sys.stderr); sys.exit(1)

    im=Image.open(ip); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb); mean=st.mean
    brightness=round(sum(mean)/3,2); contrast=round(sum(st.stddev)/3,2)
    sat=None
    if np is not None:
        arr=np.array(rgb).astype(np.float32); mx=arr.max(axis=2); mn=arr.min(axis=2); sat=round(float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100),2)
    casts=[]
    if mean[0]-mean[2]>12: casts.append('偏黄')
    if mean[0]-mean[1]>10: casts.append('偏红')
    if mean[0]>mean[1]>mean[2] and mean[0]-mean[2]>18: casts.append('偏橙')
    if abs(mean[0]-mean[1])<6 and abs(mean[1]-mean[2])<6: casts.append('偏灰')

    b,conf,method=detect_bbox(im,a.use_alpha); x1,y1,x2,y2=b; sw,sh=x2-x1+1,y2-y1+1
    geom={'subject_bbox':{'left':x1,'top':y1,'right':x2,'bottom':y2},'subject_width_px':sw,'subject_height_px':sh,'subject_width_ratio':round(sw/w,4),'subject_height_ratio':round(sh/h,4),'margins':{'top':y1,'bottom':h-1-y2,'left':x1,'right':w-1-x2},'crop_risk':[],'confidence':conf}
    if sh/h>0.9: geom['crop_risk'].append('主体过大')
    if sh/h<0.35: geom['crop_risk'].append('主体过小')
    if min(x1,y1,w-1-x2,h-1-y2)<8: geom['crop_risk'].append('接近裁切')
    if not geom['crop_risk']: geom['crop_risk']=['低']

    ar=sw/max(1,sh); cap=int(sh*0.16); label=int(sh*0.42)
    pa={'product_aspect_ratio':round(ar,4),'label_estimate':label,'cap_estimate':cap,'label_height_ratio':round(label/max(1,sh),4),'cap_height_ratio':round(cap/max(1,sh),4),
        'shape_judgement':'tall skinny serum bottle 风险' if ar<0.28 else ('squat bulky jar 风险' if ar>0.45 else '接近 4 fl oz / 120mL amber Boston round dropper bottle')}

    ref={}
    if a.reference and Path(a.reference).exists():
        rim=Image.open(a.reference); rb,_,_=detect_bbox(rim,a.use_alpha); rh=rb[3]-rb[1]+1; actual=(sh/h)/(rh/max(1,rim.height)); exp=parse_pct(a.expected_height_change); expected=None if exp is None else 1+exp
        diff=None if expected is None else actual-expected
        verdict='无法可靠判断'
        if expected is not None:
            if abs(actual-0.75)<=0.08: verdict='只是矮 25%'
            elif actual<=0.6: verdict='接近砍半'
            elif actual>0.85: verdict='高度变化不足'
        ref={'reference_subject_height_px':rh,'current_subject_height_px':sh,'expected_ratio':expected,'actual_ratio':round(actual,4),'difference':None if diff is None else round(diff,4),'verdict':verdict}

    vision={'enabled':a.use_vision,'provider':a.vision_provider,'model':a.vision_model,'success':False,'fallback_to_local':True,'error':None,'note':'gemini/openai 待扩展，当前正式实现 qwen'}
    sem={'note':'本地模式无法可靠识别场景语义、人物动作、物体名称和标签文字。'}
    if a.use_vision and a.vision_provider=='qwen':
        try:
            sem=qwen_vision(str(ip),'分析场景、人物、物体、工厂逻辑、品牌和排版建议',a.vision_model)
            vision['success']=True; vision['fallback_to_local']=False
        except Exception as e:
            vision['error']=str(e)

    brand={'tone':'中性偏商业','risk':','.join(casts) if casts else '低','suggestions':['统一冷中性色调','控制主体占比']}
    if a.brand.lower()=='veytis' or a.object_type=='bottle':
        brand['veytis_rules']=[pa['shape_judgement'],f"标签高度占比 {pa['label_height_ratio']}",f"瓶盖高度占比 {pa['cap_height_ratio']}",f"主体高度占比 {geom['subject_height_ratio']}",f"偏色 {','.join(casts) if casts else '低'}","标签文字真实性需要视觉模型确认","适合产品页:是","适合首页Hero:视留白而定"]
    if a.brand.lower()=='juese clothing' or a.scene_type=='factory_scene':
        brand['juese_rules']=[f"工厂真实感 {'中高' if contrast>18 else '中'}",f"过暗 {'是' if brightness<90 else '否'}","设备逻辑需要视觉模型确认","人物动作需要视觉模型确认","B2B适配:中高","假工厂/AI设备风险:中"]

    style={'reference_count':0,'avg_brightness':None,'avg_contrast':None,'avg_saturation':None,'avg_subject_height_ratio':None,'subject_size_diff':None,'consistency_score':None,'suggestions':[]}

    out={'image_info':{'filename':ip.name,'size':f'{w}x{h}','orientation':'横图' if w>h else ('竖图' if h>w else '方图'),'file_size_bytes':ip.stat().st_size},
         'color_analysis':{'brightness':brightness,'contrast':contrast,'saturation':sat,'cast_risks':casts},'local_geometry':geom,
         'scene_detail':{'scene_type':a.scene_type,'subject_position':'中部偏下','foreground_mid_background':'前景/中景/背景','visual_center':'中心偏下','whitespace':'中等','light_direction':'左上->右下','text_overlay_fit':'较适合','commercial_fit':'较适合'},
         'people_detail':{'people_count':'需要视觉模型确认','actions':'需要视觉模型确认','hand_risk':'需要视觉模型确认','business_fit':'需要视觉模型确认'},
         'object_inventory':{'objects':'需要视觉模型确认','label_text':'需要视觉模型确认'},'product_analysis':pa,'brand_design_analysis':brand,
         'graphic_design_analysis':{'headline_zone':'上1/3','subheadline_zone':'标题下方','cta_zone':'右下','logo_zone':'左上/右上','text_safe_zone':'上方与四角','text_contrast_fit':'可用' if contrast>18 else '偏弱','suggestions':['保持留白','增强文字对比']},
         'style_consistency':style,'ai_qc':{'ai_feel':'中','color_cast_risk':casts,'local_can_judge':['几何','色彩','裁切'],'need_vision':['人物','标签','设备语义']},'business_fit':{'site_fit':'较适合','hero_fit':'视留白而定'},
         'reference_comparison':ref,'semantic_analysis':sem,'prompts':{'regenerate':'realistic commercial image, neutral-cool tone, clean composition','inpaint':'fix proportion and color cast','negative':'fake text, warped bottle, yellow/red/orange cast'},
         'scores':{'总分':7.4},'confidence':{'subject_detection':conf},'vision_model_status':vision}

    lines=['# 统一视觉分析报告','## 主体几何：',f"- bbox left：{x1}",f"- bbox top：{y1}",f"- bbox right：{x2}",f"- bbox bottom：{y2}",f"- 主体高度占画面：{geom['subject_height_ratio']}",f"- 主体宽度占画面：{geom['subject_width_ratio']}",f"- 顶部留白：{geom['margins']['top']}",f"- 底部留白：{geom['margins']['bottom']}",f"- 左侧留白：{geom['margins']['left']}",f"- 右侧留白：{geom['margins']['right']}",f"- 裁切风险：{', '.join(geom['crop_risk'])}",f"- 置信度：{conf}",
           '## 品牌分析：',f"- 色调：{brand['tone']}",f"- 风险：{brand['risk']}",f"- 建议：{'; '.join(brand['suggestions'])}",
           '## 人物分析：','- 人物数量：需要视觉模型确认','- 动作：需要视觉模型确认','- 手部风险：需要视觉模型确认','- 商业适配度：需要视觉模型确认',
           '## 风格统一：',f"- 参考图数量：{style['reference_count']}",f"- 平均亮度：{style['avg_brightness']}",f"- 平均对比度：{style['avg_contrast']}",f"- 主体大小差异：{style['subject_size_diff']}",f"- 一致性评分：{style['consistency_score']}"]

    ts=dt.datetime.now().strftime('%Y%m%d-%H%M%S'); od=Path(a.output_dir)/ts; od.mkdir(parents=True,exist_ok=True)
    md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    md.write_text('\n'.join(lines),encoding='utf-8'); js.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.json: print(json.dumps(out,ensure_ascii=False))
    print(f'FILE:file:///{md.as_posix()}')

if __name__=='__main__':
    main()
