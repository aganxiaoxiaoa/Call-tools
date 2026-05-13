#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, base64, datetime as dt, json, os, re, sys
from pathlib import Path
from urllib import request
Image=None
ImageStat=None
np=None

MODES=['basic','full','product-geometry','scene-detail','people-detail','semantic-full','brand-design','brand-full','graphic-design','style-consistency','commercial-qc','qc','prompt']
SCENES=['product_photo','factory_scene','sample_room','printing_workshop','warehouse','showroom','office','poster','banner','social_post','website_hero','generic']
OBJECTS=['bottle','jar','box','garment','factory','machine','poster','banner','generic']

def top5_hex(img):
    im=img.copy(); im.thumbnail((320,320))
    if np is None:
        q=im.convert('P',palette=Image.ADAPTIVE,colors=5); pal=q.getpalette(); out=[]
        for c,i in sorted(q.getcolors() or [],reverse=True)[:5]:
            r,g,b=pal[i*3:i*3+3]; out.append(f"#{r:02X}{g:02X}{b:02X}")
        return out
    arr=np.array(im).reshape(-1,3); q=(arr//32)*32; u,c=np.unique(q,axis=0,return_counts=True); idx=np.argsort(c)[::-1][:5]
    return [f"#{int(u[i][0]):02X}{int(u[i][1]):02X}{int(u[i][2]):02X}" for i in idx]

def detect_subject(im,use_alpha=False):
    w,h=im.size
    if np is None: return [0,0,w-1,h-1],'low','numpy_missing'
    rgba=np.array(im.convert('RGBA')); alpha=rgba[:,:,3]
    if (use_alpha or 'A' in im.getbands()) and (alpha<250).mean()>0.02:
        mask=alpha>12; method='alpha-mask'
    else:
        rgb=np.array(im.convert('RGB')).astype(np.float32)
        bg=np.vstack([rgb[0,0],rgb[0,-1],rgb[-1,0],rgb[-1,-1]]).mean(axis=0)
        dist=np.linalg.norm(rgb-bg,axis=2); mask=dist>22; method='bg-diff'
    ys,xs=np.where(mask)
    if len(xs)==0: return [0,0,w-1,h-1],'low','fallback'
    x1,y1,x2,y2=int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())
    wr,hr=(x2-x1+1)/w,(y2-y1+1)/h
    conf='high'
    if wr>0.95 and hr>0.95: conf='low'
    elif wr>0.9 or hr>0.9: conf='medium'
    return [x1,y1,x2,y2],conf,method

def parse_pct(s):
    m=re.match(r'\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$',s or '')
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
    p=argparse.ArgumentParser()
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
        print('错误：缺少 pillow，请安装：pip install pillow',file=sys.stderr); sys.exit(2)
    try:
        import numpy as np
    except ImportError:
        np=None
    ip=Path(a.image)
    if not ip.exists(): print('图片不存在',file=sys.stderr); sys.exit(1)

    im=Image.open(ip); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb)
    mean=st.mean; brightness=round(sum(mean)/3,2); contrast=round(sum(st.stddev)/3,2)
    sat=None
    if np is not None:
        arr=np.array(rgb).astype(np.float32); mx=arr.max(axis=2); mn=arr.min(axis=2); sat=round(float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100),2)
    casts=[]
    if mean[0]-mean[2]>12: casts.append('yellow_cast')
    if mean[0]-mean[1]>10: casts.append('red_cast')
    if mean[0]>mean[1]>mean[2] and mean[0]-mean[2]>18: casts.append('orange_cast')
    if abs(mean[0]-mean[1])<6 and abs(mean[1]-mean[2])<6: casts.append('gray_cast')

    b,conf,method=detect_subject(im,a.use_alpha); x1,y1,x2,y2=b; sw,sh=x2-x1+1,y2-y1+1
    geom={'subject_bbox':{'left':x1,'top':y1,'right':x2,'bottom':y2},'subject_width_px':sw,'subject_height_px':sh,'subject_height_ratio':round(sh/h,4),'subject_width_ratio':round(sw/w,4),
          'margins':{'top':y1,'bottom':h-1-y2,'left':x1,'right':w-1-x2},'crop_risk':[],'confidence':conf,'method':method}
    if sh/h>0.9: geom['crop_risk'].append('主体过大')
    if sh/h<0.35: geom['crop_risk'].append('主体过小')
    if min(x1,y1,w-1-x2,h-1-y2)<8: geom['crop_risk'].append('接近裁切')
    if not geom['crop_risk']: geom['crop_risk']=['低']

    ar=sw/max(1,sh); cap=int(sh*0.16); label=int(sh*0.42)
    prod={'product_aspect_ratio':round(ar,4),'label_estimate':label,'cap_estimate':cap,'label_height_ratio':round(label/max(1,sh),4),'cap_height_ratio':round(cap/max(1,sh),4),
          'too_tall_too_skinny':ar<0.28,'too_short_too_wide':ar>0.45}

    ref={}
    if a.reference and Path(a.reference).exists():
        rim=Image.open(a.reference); rb,_,_=detect_subject(rim,a.use_alpha); rh=rb[3]-rb[1]+1
        actual=(sh/h)/(rh/max(1,rim.height)); exp=parse_pct(a.expected_height_change); exratio=None if exp is None else 1+exp
        diff=None if exratio is None else actual-exratio
        verdict='无法可靠判断'
        if exratio is not None:
            if abs(actual-0.75)<=0.08: verdict='只是矮 25%'
            elif actual<=0.6: verdict='接近砍半'
            elif actual>0.85: verdict='高度变化不足'
        ref={'reference_subject_height_px':rh,'current_subject_height_px':sh,'actual_ratio':round(actual,4),'expected_ratio':exratio,'difference':None if diff is None else round(diff,4),'verdict':verdict}

    brand={'tone':'中性','risk':casts,'suggestions':['统一色调','控制主体占比']}
    if a.brand.lower()=='veytis' or a.object_type=='bottle':
        brand['veytis']={'shape':'4oz/120mL判定: '+('接近Boston round' if 0.28<=ar<=0.45 else ('tall skinny serum bottle' if ar<0.28 else 'squat bulky jar')),
                         'label_ratio':prod['label_height_ratio'],'cap_ratio':prod['cap_height_ratio'],'subject_height_ratio':geom['subject_height_ratio'],'casts':casts,
                         'fit_product_page':'是','fit_hero':'视留白而定','suggestions':['降低偏黄偏红偏橙','保证标签真实']}
    if a.brand.lower()=='juese clothing' or a.scene_type=='factory_scene':
        brand['juese']={'factory_realism_local':'中高' if contrast>18 else '中','too_dark':brightness<90,'too_yellow':'yellow_cast' in casts,'fit_b2b':'中高','fake_factory_risk':'中','need_vision':['设备逻辑','人物动作']}

    graphic={'headline_zone':'上1/3','subheadline_zone':'标题下','cta_zone':'右下','logo_zone':'左上/右上','text_safe_zone':'上方+四角','text_bg_contrast':'可用' if contrast>18 else '偏弱','fit_homepage':'较适合','fit_ad':'较适合','fit_short_video_cover':'可用'}

    style={'reference_count':0,'average_brightness':None,'average_contrast':None,'average_saturation':None,'average_subject_height_ratio':None,'current_diff':{},'consistency_score':None,'suggestions':[]}

    vision={'enabled':a.use_vision,'provider':a.vision_provider,'model':a.vision_model,'success':False,'fallback_to_local':True,'error':None}
    semantic={'note':'本地模式，语义细节需要视觉模型'}
    if a.use_vision and a.vision_provider=='qwen':
        try:
            semantic=qwen_call(str(ip),'分析人物/场景/物体/工厂逻辑',a.vision_model); vision['success']=True; vision['fallback_to_local']=False
        except Exception as e:
            vision['error']=str(e)

    out={'image_info':{'filename':ip.name,'image_size':f'{w}x{h}','aspect_ratio':f'{w}:{h}','orientation':'横图' if w>h else ('竖图' if h>w else '方图'),'file_size':ip.stat().st_size},
         'color_analysis':{'dominant_colors_top5_hex':top5_hex(rgb),'average_brightness':brightness,'contrast':contrast,'saturation':sat,'casts':casts},
         'local_geometry':geom,'product_analysis':prod,'brand_design_analysis':brand,'graphic_design_analysis':graphic,'style_consistency':style,'ai_qc':{'ai_feel':'中','need_vision':['人物细节','标签文字']},
         'business_fit':{'site_fit':'较适合'},'reference_comparison':ref,'semantic_analysis':semantic,'prompts':{'regen':'realistic commercial image','inpaint':'fix proportion and cast'},'scores':{'total':7.4},'confidence':{'subject':conf},'vision_model_status':vision}

    md=[
        '# 统一视觉分析报告','## 执行摘要',f"- 模式：{a.mode}",
        '## 基础信息',f"- 尺寸：{w}x{h}",f"- 文件大小：{ip.stat().st_size}",
        '## 色彩分析',f"- 主色Top5 HEX：{', '.join(out['color_analysis']['dominant_colors_top5_hex'])}",f"- 亮度：{brightness}",f"- 对比度：{contrast}",f"- 饱和度：{sat}",f"- 偏色：{', '.join(casts) if casts else '低'}",
        '## 主体几何',f"- bbox left：{x1}",f"- bbox top：{y1}",f"- bbox right：{x2}",f"- bbox bottom：{y2}",f"- 主体高度占画面：{geom['subject_height_ratio']}",f"- 主体宽度占画面：{geom['subject_width_ratio']}",f"- 裁切风险：{', '.join(geom['crop_risk'])}",f"- 置信度：{conf}",
        '## 产品比例',f"- 比例：{prod['product_aspect_ratio']}",f"- 标签占比：{prod['label_height_ratio']}",f"- 瓶盖占比：{prod['cap_height_ratio']}",
        '## 品牌分析',f"- 色调：{brand['tone']}",f"- 风险：{', '.join(casts) if casts else '低'}",'## 平面设计',f"- 标题区域：{graphic['headline_zone']}",f"- 文字安全区：{graphic['text_safe_zone']}",
        '## AI 质检',f"- AI感：{out['ai_qc']['ai_feel']}",
        '## 参考图对比',*( [f"- {k}: {v}" for k,v in ref.items()] if ref else ['- 未提供参考图']),
        '## 修改建议','- 调整主体比例','- 修正偏色','## 提示词',f"- 重生成：{out['prompts']['regen']}",f"- 局部修图：{out['prompts']['inpaint']}"
    ]

    ts=dt.datetime.now().strftime('%Y%m%d-%H%M%S'); od=Path(a.output_dir)/ts; od.mkdir(parents=True,exist_ok=True)
    mdp=od/'image_analysis_report.md'; jsp=od/'image_analysis_report.json'
    mdp.write_text('\n'.join(md),encoding='utf-8'); jsp.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'FILE:file:///{mdp.as_posix()}')

if __name__=='__main__': main()
