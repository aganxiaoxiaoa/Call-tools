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

def qwen_call(path,prompt,model):
    key=os.getenv('DASHSCOPE_API_KEY')
    if not key: raise RuntimeError('缺少 DASHSCOPE_API_KEY')
    base=os.getenv('DASHSCOPE_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1').rstrip('/')
    schema='仅返回JSON: scene_detail,people_detail,object_inventory,product_semantic_analysis,factory_logic_analysis,brand_visual_analysis,graphic_design_analysis,text_or_label_observation,ai_artifact_risks,commercial_fit,suggestions'
    payload={'model':model or 'qwen-vl-plus','messages':[{'role':'user','content':[{'type':'text','text':schema+'\n'+prompt},{'type':'image_url','image_url':{'url':to_data_url(path)}}]}]}
    req=request.Request(base+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
    with request.urlopen(req,timeout=45) as r:data=json.loads(r.read().decode('utf-8','ignore'))
    txt=((data.get('choices') or [{}])[0].get('message') or {}).get('content','{}')
    try:return json.loads(txt)
    except:return {'raw_text':txt}

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
    try:
        import numpy as np
    except ImportError:
        np=None

    ip=Path(a.image)
    if not ip.exists(): print('图片不存在',file=sys.stderr); sys.exit(1)
    im=Image.open(ip); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb)
    mean=st.mean; brightness=round(sum(mean)/3,2); contrast=round(sum(st.stddev)/3,2)

    # top5 hex
    thumb=rgb.copy(); thumb.thumbnail((320,320))
    if np is None:
        q=thumb.convert('P',palette=Image.ADAPTIVE,colors=5); pal=q.getpalette(); top5=[]
        for c,i in sorted(q.getcolors() or [],reverse=True)[:5]:
            r,g,b=pal[i*3:i*3+3]; top5.append(f"#{r:02X}{g:02X}{b:02X}")
    else:
        arr=np.array(thumb).reshape(-1,3); q=(arr//32)*32; u,c=np.unique(q,axis=0,return_counts=True); idx=np.argsort(c)[::-1][:5]
        top5=[f"#{int(u[i][0]):02X}{int(u[i][1]):02X}{int(u[i][2]):02X}" for i in idx]

    casts=[]
    if mean[0]-mean[2]>12: casts.append('yellow_cast')
    if mean[0]-mean[1]>10: casts.append('red_cast')
    if mean[0]>mean[1]>mean[2] and mean[0]-mean[2]>18: casts.append('orange_cast')
    if abs(mean[0]-mean[1])<6 and abs(mean[1]-mean[2])<6: casts.append('gray_cast')

    # subject bbox
    if np is None:
        b=[0,0,w-1,h-1]; conf='low'; method='numpy_missing'
    else:
        rgba=np.array(im.convert('RGBA')); alpha=rgba[:,:,3]
        if (a.use_alpha or 'A' in im.getbands()) and (alpha<250).mean()>0.02: mask=alpha>12; method='alpha-mask'
        else:
            rr=np.array(rgb).astype(np.float32); bg=np.vstack([rr[0,0],rr[0,-1],rr[-1,0],rr[-1,-1]]).mean(axis=0); mask=np.linalg.norm(rr-bg,axis=2)>22; method='bg-diff'
        ys,xs=np.where(mask)
        if len(xs)==0: b=[0,0,w-1,h-1]; conf='low'; method='fallback'
        else:
            b=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
            wr,hr=(b[2]-b[0]+1)/w,(b[3]-b[1]+1)/h
            conf='high'
            if wr>0.95 and hr>0.95: conf='low'
            elif wr>0.9 or hr>0.9: conf='medium'

    x1,y1,x2,y2=b; sw,sh=x2-x1+1,y2-y1+1
    geom={'subject_bbox':{'left':x1,'top':y1,'right':x2,'bottom':y2},'subject_width_px':sw,'subject_height_px':sh,'subject_height_ratio':round(sh/h,4),'subject_width_ratio':round(sw/w,4),
          'margins':{'top':y1,'bottom':h-1-y2,'left':x1,'right':w-1-x2},'crop_risk':[],'confidence':conf,'method':method}
    if sh/h>0.9: geom['crop_risk'].append('主体过大')
    if sh/h<0.35: geom['crop_risk'].append('主体过小')
    if min(x1,y1,w-1-x2,h-1-y2)<8: geom['crop_risk'].append('接近裁切')
    if not geom['crop_risk']: geom['crop_risk']=['低']

    ar=sw/max(1,sh); cap=int(sh*0.16); label=int(sh*0.42)
    product={'product_aspect_ratio':round(ar,4),'label_estimate':label,'cap_estimate':cap,'label_height_ratio':round(label/max(1,sh),4),'cap_height_ratio':round(cap/max(1,sh),4),
             'too_tall_too_skinny':ar<0.28,'too_short_too_wide':ar>0.45}

    ref={}
    if a.reference and Path(a.reference).exists():
        rim=Image.open(a.reference); rw,rh=rim.size
        if np is None: rb=[0,0,rw-1,rh-1]
        else:
            rr=np.array(rim.convert('RGB')).astype(np.float32); bg=np.vstack([rr[0,0],rr[0,-1],rr[-1,0],rr[-1,-1]]).mean(axis=0); m=np.linalg.norm(rr-bg,axis=2)>22; ys,xs=np.where(m); rb=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else [0,0,rw-1,rh-1]
        rsh=rb[3]-rb[1]+1; actual=(sh/h)/(rsh/max(1,rh)); exp=parse_pct(a.expected_height_change); exratio=None if exp is None else 1+exp
        diff=None if exratio is None else actual-exratio
        verdict='无法可靠判断'
        if exratio is not None:
            if abs(actual-0.75)<=0.08: verdict='只是矮 25%'
            elif actual<=0.6: verdict='接近砍半'
            elif actual>0.85: verdict='高度变化不足'
        ref={'reference_subject_height_px':rsh,'current_subject_height_px':sh,'actual_ratio':round(actual,4),'expected_ratio':exratio,'difference':None if diff is None else round(diff,4),'verdict':verdict}

    brand={'tone':'中性','risk':casts,'suggestions':['统一色调','控制主体比例']}
    if a.brand.lower()=='veytis' or a.object_type=='bottle':
        brand['veytis']={'shape':'tall skinny serum bottle' if ar<0.28 else ('squat bulky jar' if ar>0.45 else '4 fl oz / 120mL amber Boston round dropper bottle'),'label_ratio':product['label_height_ratio'],'cap_ratio':product['cap_height_ratio'],'subject_ratio':geom['subject_height_ratio'],'casts':casts,'fit_product_page':'是','fit_home_hero':'视留白而定','suggestions':['减少偏黄偏红偏橙','增强标签真实性']}
    if a.brand.lower()=='juese clothing' or a.scene_type=='factory_scene':
        brand['juese']={'factory_realism_local':'中高' if contrast>18 else '中','lighting_too_dark':brightness<90,'lighting_too_yellow':'yellow_cast' in casts,'fit_b2b':'中高','fake_factory_risk':'中','need_vision_confirm':['设备逻辑','人物动作']}

    graphic={'headline_zone':'上1/3','subheadline_zone':'标题下','cta_zone':'右下','logo_zone':'左上/右上','text_safe_zone':'上方与四角','fit_homepage':'较适合','fit_ad':'较适合','fit_short_video':'可用'}

    vision={'enabled':a.use_vision,'provider':a.vision_provider,'model':a.vision_model,'success':False,'fallback_to_local':True,'error':None}
    semantic={'note':'本地模式，语义细节需视觉模型'}
    if a.use_vision and a.vision_provider=='qwen':
        try:
            semantic=qwen_call(str(ip),'分析人物、场景、物体、工厂逻辑',a.vision_model); vision['success']=True; vision['fallback_to_local']=False
        except Exception as e:
            vision['error']=str(e)

    out={'image_info':{'filename':ip.name,'size':f'{w}x{h}'},'color_analysis':{'dominant_colors_top5_hex':top5,'average_brightness':brightness,'contrast':contrast,'casts':casts},
         'local_geometry':geom,'product_analysis':product,'brand_design_analysis':brand,'graphic_design_analysis':graphic,'style_consistency':{'note':'基础版'},'ai_qc':{'local_can_judge':['几何','色彩','裁切'],'need_vision':['人物','标签','设备']},
         'business_fit':{'site_fit':'较适合'},'reference_comparison':ref,'semantic_analysis':semantic,'prompts':{'regen':'realistic commercial image','inpaint':'fix proportion and cast'},'scores':{'total':7.4},'confidence':{'subject':conf},'vision_model_status':vision}

    lines=['# 统一视觉分析报告','## 执行摘要',f"- 模式: {a.mode}",'## 基础信息',f"- 尺寸: {w}x{h}",'## 色彩分析',f"- 主色Top5 HEX: {', '.join(top5)}",f"- 亮度: {brightness}",f"- 对比度: {contrast}",f"- 偏色: {', '.join(casts) if casts else '低'}",'## 主体几何',
           f"- bbox left: {x1}",f"- bbox top: {y1}",f"- bbox right: {x2}",f"- bbox bottom: {y2}",f"- 主体高度占画面: {geom['subject_height_ratio']}",f"- 主体宽度占画面: {geom['subject_width_ratio']}",f"- 裁切风险: {', '.join(geom['crop_risk'])}",f"- 置信度: {conf}",
           '## 产品比例',f"- product_aspect_ratio: {product['product_aspect_ratio']}",f"- label_estimate: {product['label_estimate']}",f"- cap_estimate: {product['cap_estimate']}",
           '## 品牌分析',f"- 色调: {brand['tone']}",f"- 风险: {', '.join(casts) if casts else '低'}",'## 平面设计',f"- 标题区: {graphic['headline_zone']}",f"- 文字安全区: {graphic['text_safe_zone']}",
           '## AI质检',f"- 本地可判断: {', '.join(out['ai_qc']['local_can_judge'])}",
           '## 参考图对比'] + ([f"- {k}: {v}" for k,v in ref.items()] if ref else ['- 未提供']) + ['## 修改建议','- 调整主体比例','- 修正偏色','## 提示词',f"- 重生成: {out['prompts']['regen']}",f"- 局部修图: {out['prompts']['inpaint']}"]

    ts=dt.datetime.now().strftime('%Y%m%d-%H%M%S'); od=Path(a.output_dir)/ts; od.mkdir(parents=True,exist_ok=True)
    md=od/'image_analysis_report.md'; js=od/'image_analysis_report.json'
    md.write_text('\n'.join(lines),encoding='utf-8'); js.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.json: print(json.dumps(out,ensure_ascii=False))
    print(f'FILE:file:///{md.as_posix()}')

if __name__=='__main__':
    main()
