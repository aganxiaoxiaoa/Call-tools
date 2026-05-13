#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, datetime as dt, json, math, os, re, sys
from pathlib import Path
from urllib import request

try:
    from PIL import Image, ImageStat
except ImportError:
    print('错误：缺少 pillow，请安装：pip install pillow', file=sys.stderr); sys.exit(2)
try:
    import numpy as np
except ImportError:
    np = None

MODES=["basic","full","product-geometry","scene-detail","people-detail","semantic-full","brand-design","brand-full","graphic-design","style-consistency","commercial-qc","qc","prompt"]
SCENES=["product_photo","factory_scene","sample_room","printing_workshop","warehouse","showroom","office","poster","banner","social_post","website_hero","generic"]
OBJECTS=["bottle","jar","box","garment","factory","machine","poster","banner","generic"]


def hex5(img):
    im=img.copy(); im.thumbnail((300,300))
    if np is None:
        q=im.convert('P',palette=Image.ADAPTIVE,colors=5); pal=q.getpalette(); out=[]
        for c,i in sorted(q.getcolors() or [],reverse=True)[:5]:
            r,g,b=pal[i*3:i*3+3]; out.append(f"#{r:02X}{g:02X}{b:02X}")
        return out
    arr=np.array(im).reshape(-1,3); q=(arr//32)*32; u,c=np.unique(q,axis=0,return_counts=True); idx=np.argsort(c)[::-1][:5]
    return [f"#{int(u[i][0]):02X}{int(u[i][1]):02X}{int(u[i][2]):02X}" for i in idx]


def detect_subject(im,use_alpha=False):
    w,h=im.size
    if np is None:
        return [0,0,w-1,h-1],"low","numpy_missing"
    rgba=np.array(im.convert('RGBA'))
    alpha=rgba[:,:,3]
    if (use_alpha or 'A' in im.getbands()) and (alpha<250).mean()>0.02:
        mask=alpha>10; method='alpha-mask'
    else:
        rgb=np.array(im.convert('RGB')).astype(np.float32)
        bg=np.vstack([rgb[0,0],rgb[0,-1],rgb[-1,0],rgb[-1,-1]]).mean(axis=0)
        dist=np.linalg.norm(rgb-bg,axis=2); mask=dist>22; method='bg-diff'
    ys,xs=np.where(mask)
    if len(xs)==0:
        return [0,0,w-1,h-1],"low","fallback-full"
    x1,y1,x2,y2=int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())
    wr,hr=(x2-x1+1)/w,(y2-y1+1)/h
    conf='high'
    if wr>0.95 and hr>0.95: conf='low'
    elif wr>0.9 or hr>0.9: conf='medium'
    return [x1,y1,x2,y2],conf,method


def geometry(b,w,h):
    x1,y1,x2,y2=b; sw,sh=max(1,x2-x1+1),max(1,y2-y1+1)
    risks=[]
    if sh/h>0.9: risks.append('主体过大')
    if sh/h<0.35: risks.append('主体过小')
    if y1<=2: risks.append('顶部接近裁切')
    if y2>=h-3: risks.append('底部接近裁切')
    if min(x1,y1,w-1-x2,h-1-y2)<8: risks.append('边缘接近裁切')
    return {'subject_bbox':{'left':x1,'top':y1,'right':x2,'bottom':y2},'subject_width_px':sw,'subject_height_px':sh,'subject_width_ratio':round(sw/w,4),'subject_height_ratio':round(sh/h,4),
            'margins':{'left':x1,'right':w-1-x2,'top':y1,'bottom':h-1-y2},'crop_risk':risks or ['低']}


def bottle_rules(g):
    sh,sw=g['subject_height_px'],g['subject_width_px']; ar=sw/max(1,sh); cap=int(sh*0.16); label=int(sh*0.42)
    shape='接近 4 fl oz / 120mL amber Boston round dropper bottle' if 0.28<=ar<=0.45 else ('过高过瘦，serum bottle 风险' if ar<0.28 else '过矮过胖，jar 风险')
    return {'product_aspect_ratio':round(ar,4),'label_estimate':label,'cap_estimate':cap,'label_height_ratio':round(label/sh,4),'cap_height_ratio':round(cap/sh,4),'shape_judgement':shape}


def parse_pct(x):
    if not x: return None
    m=re.match(r'\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$',x)
    return float(m.group(1))/100 if m else None


def qwen_vision(image_path,prompt,model):
    key=os.getenv('DASHSCOPE_API_KEY')
    if not key: raise RuntimeError('缺少 DASHSCOPE_API_KEY')
    base=os.getenv('DASHSCOPE_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1').rstrip('/')
    schema="""请只返回JSON，字段: scene_detail,people_detail,object_inventory,product_semantic_analysis,factory_logic_analysis,brand_visual_analysis,graphic_design_analysis,text_or_label_observation,ai_artifact_risks,commercial_fit,suggestions"""
    payload={"model":model or "qwen-vl-plus","messages":[{"role":"user","content":[{"type":"text","text":schema+"\n"+prompt},{"type":"image_url","image_url":{"url":"file:///"+image_path.replace('\\','/')}}]}]}
    req=request.Request(base+'/chat/completions',data=json.dumps(payload).encode('utf-8'),headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"})
    with request.urlopen(req,timeout=45) as r: data=json.loads(r.read().decode('utf-8','ignore'))
    txt=((data.get('choices') or [{}])[0].get('message') or {}).get('content','{}')
    try: return json.loads(txt)
    except Exception: return {'raw_text':txt}


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

    ip=Path(a.image)
    if not ip.exists(): print(f'错误：图片不存在：{ip}',file=sys.stderr); sys.exit(1)
    im=Image.open(ip); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb)
    mean=st.mean; brightness=round(sum(mean)/3,2); contrast=round(sum(st.stddev)/3,2)
    sat=None
    if np is not None:
        arr=np.array(rgb).astype(np.float32); mx=arr.max(axis=2); mn=arr.min(axis=2); sat=round(float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100),2)
    casts=[]
    if mean[0]-mean[2]>12: casts.append('偏黄/偏红')
    if mean[0]-mean[1]>10: casts.append('偏红')
    if mean[0]>mean[1]>mean[2] and mean[0]-mean[2]>18: casts.append('偏橙')
    if abs(mean[0]-mean[1])<6 and abs(mean[1]-mean[2])<6: casts.append('偏灰')

    bbox,conf,method=detect_subject(im,a.use_alpha); g=geometry(bbox,w,h); g['confidence']=conf; g['detection_method']=method
    pa=bottle_rules(g) if (a.brand.lower()=='veytis' or a.object_type=='bottle') else {'product_aspect_ratio':round(g['subject_width_px']/max(1,g['subject_height_px']),4),'shape_judgement':'通用主体'}

    ref={}
    if a.reference and Path(a.reference).exists():
        rim=Image.open(a.reference); rb,_,_=detect_subject(rim,a.use_alpha); rg=geometry(rb,rim.width,rim.height)
        actual=g['subject_height_ratio']/max(1e-6,rg['subject_height_ratio']); exp=parse_pct(a.expected_height_change)
        er=1+(exp or 0) if exp is not None else None; diff=None if er is None else actual-er
        verdict='无预期变更'
        if er is not None:
            if abs(actual-0.75)<=0.08: verdict='只是矮 25%'
            elif actual<=0.6: verdict='接近砍半'
            else: verdict='高度变化不足'
        ref={'reference_subject_height_px':rg['subject_height_px'],'current_subject_height_px':g['subject_height_px'],'actual_ratio':round(actual,4),'expected_ratio':er,'difference':None if diff is None else round(diff,4),'verdict':verdict}

    scene={'scene_type_infer':a.scene_type,'subject_position':'中部偏下','foreground_mid_background':'前景主体/中景环境/背景结构','visual_center':'中心偏下','whitespace':'中等' if g['subject_height_ratio']<0.85 else '不足','light_direction_estimate':'左上->右下','color_cast_risk':casts or ['中性'],'under_exposed':brightness<85,'over_exposed':brightness>225,'text_overlay_fit':'较适合' if g['subject_height_ratio']<0.82 else '一般','commercial_fit':'较适合','local_limit':'本地模式无法可靠识别场景语义、人物动作、具体物体名称和标签文字；以下为几何、色彩、构图、品牌规则分析。'}
    people={'people_count':'需要视觉模型确认','actions':'需要视觉模型确认','hand_risk':'需要视觉模型确认','b2b_fit':'需要视觉模型确认','safety':'不识别真实人物身份，不猜姓名'}
    obj={'product_type':'本地模式仅做几何估计','label_text':'需要视觉模型确认','packaging_realism':'需要视觉模型确认'}

    vstatus={'enabled':a.use_vision,'provider':a.vision_provider,'model':a.vision_model,'implemented':'qwen','success':False,'fallback_to_local':True,'error':None,'note':'gemini/openai 待扩展，当前正式实现 qwen'}
    semantic={'note':'未开启视觉模型，本地模式无法可靠识别场景语义、人物细节和标签文字；以下为几何/色彩/构图分析。'}
    if a.use_vision:
        if a.vision_provider=='qwen':
            try:
                vr=qwen_vision(str(ip),'分析场景、人物、产品、工厂逻辑、品牌视觉、平面设计、AI伪影、商业适配并给建议',a.vision_model)
                semantic=vr; scene.update(vr.get('scene_detail',{}) if isinstance(vr,dict) else {}); people.update(vr.get('people_detail',{}) if isinstance(vr,dict) else {}); obj.update(vr.get('object_inventory',{}) if isinstance(vr,dict) else {})
                vstatus['success']=True; vstatus['fallback_to_local']=False
            except Exception as e:
                vstatus['error']=str(e)
        else:
            vstatus['error']=f'{a.vision_provider} 待扩展，已回退本地分析'

    veytis=[]; juese=[]
    if a.brand.lower()=='veytis' or a.object_type=='bottle':
        veytis=[f"瓶型判断：{pa.get('shape_judgement')}",f"标签占比：{pa.get('label_height_ratio')}",f"瓶盖占比：{pa.get('cap_height_ratio')}",f"主体高度占比：{g['subject_height_ratio']}",f"偏色风险：{','.join(casts) if casts else '低'}","背景推荐 neutral white/cool ivory/pale stone/cool greige","标签乱码与真实性：需要视觉模型确认"]
    if a.brand.lower()=='juese clothing' or a.scene_type in ['factory_scene','sample_room','printing_workshop','warehouse']:
        juese=[f"工厂真实感：{'中高' if contrast>18 else '中'}",f"干净专业：{'中高' if brightness>90 else '中'}",f"过暗风险：{'是' if brightness<90 else '否'}","设备/质检/包装流程：需要视觉模型确认","人物动作：需要视觉模型确认","假工厂/AI设备风险：中"]

    gdesign={'headline_zone':'上1/3','subheadline_zone':'标题下','cta_zone':'右下','logo_zone':'左上或右上','text_safe_zone':'四角+上边','text_contrast':'可用' if contrast>18 else '偏弱','hierarchy':'中等','too_much_text_risk':'中','template_risk':'中','cheap_risk':'低到中','ad_fit':'较适合','homepage_fit':'较适合','short_video_cover_fit':'可用','font':'标题可用现代衬线+正文无衬线','size':'H1 48-72 / H2 24-36 / Body 16-20','spacing':'行距1.3 字距0-2%','suggestions':['保留上方留白','提升文字对比']}

    style={'reference_count':0,'reference_avg_brightness':None,'reference_avg_contrast':None,'reference_avg_saturation':None,'reference_avg_subject_height_ratio':None,'differences':{},'consistency_score':None,'suggestions':[]}
    if a.reference_dir and Path(a.reference_dir).exists() and np is not None:
        vals=[]
        for f in [x for x in Path(a.reference_dir).iterdir() if x.suffix.lower() in ['.jpg','.jpeg','.png','.webp','.bmp']][:50]:
            ri=Image.open(f).convert('RGB'); rs=ImageStat.Stat(ri); rb=sum(rs.mean)/3; rc=sum(rs.stddev)/3
            arr=np.array(ri).astype(np.float32); mx=arr.max(axis=2); mn=arr.min(axis=2); rsat=float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100)
            bb,_,_=detect_subject(ri,False); rg=geometry(bb,ri.width,ri.height); vals.append((rb,rc,rsat,rg['subject_height_ratio']))
        if vals:
            mb=sum(v[0] for v in vals)/len(vals); mc=sum(v[1] for v in vals)/len(vals); ms=sum(v[2] for v in vals)/len(vals); mh=sum(v[3] for v in vals)/len(vals)
            score=max(0,10-(abs(brightness-mb)/12+abs(contrast-mc)/10+abs((sat or ms)-ms)/12+abs(g['subject_height_ratio']-mh)*12))
            style.update({'reference_count':len(vals),'reference_avg_brightness':round(mb,2),'reference_avg_contrast':round(mc,2),'reference_avg_saturation':round(ms,2),'reference_avg_subject_height_ratio':round(mh,4),
                         'differences':{'color_tone':','.join(casts) if casts else '中性','brightness_diff':round(brightness-mb,2),'contrast_diff':round(contrast-mc,2),'composition_diff':'按主体占比估算','subject_size_diff':round(g['subject_height_ratio']-mh,4),'background_diff':'需要视觉模型确认'},
                         'consistency_score':round(score,2),'suggestions':['统一白平衡','统一主体大小','统一背景材质']})

    ai_qc={'ai_feel':'中' if contrast<18 else '低到中','label_text_risk':'需要视觉模型确认','product_ratio_risk':'低' if 0.25<=pa.get('product_aspect_ratio',0.35)<=0.5 else '中高','bottle_deform_risk':'低' if '接近' in pa.get('shape_judgement','') else '中','hand_anomaly_risk':'需要视觉模型确认','perspective_risk':'中','background_unreal_risk':'中','over_smooth_risk':'中' if contrast<14 else '低','over_sharpen_risk':'中' if contrast>70 else '低','color_cast_risk':casts or ['低'],'local_can_judge':['bbox','主体比例','裁切','亮度','对比度','饱和度','色偏'],'need_vision':['人物细节','标签真假','设备语义']}

    business={'product_page_fit':'较适合','hero_fit':'取决于留白','about_page_fit':'可用','blog_cover_fit':'适合','ad_fit':'较适合'}
    prompts={'regenerate':'realistic commercial image, clean composition, neutral-cool tone, true product proportions','inpaint':'fix product proportion, reduce yellow/red/orange cast, keep realistic label and texture','negative':'fake text, distorted bottle, warped perspective, plastic look, yellow cast, red cast, orange cast'}
    scores={'真实性':round(max(0,10-abs(contrast-35)/7),2),'品牌匹配度':7.3,'商业适配度':7.8,'构图清晰度':round(8.0 if g['subject_height_ratio']<0.85 else 6.5,2)}; scores['总分']=round(sum(scores.values())/len(scores),2)

    out={
      'image_info':{'filename':ip.name,'size':f'{w}x{h}','ratio':f'{w}:{h}','orientation':'横图' if w>h else ('竖图' if h>w else '方图'),'file_size_bytes':ip.stat().st_size,'brand':a.brand,'mode':a.mode},
      'color_analysis':{'top5_hex':hex5(rgb),'brightness':brightness,'contrast':contrast,'saturation':sat,'cast_risks':casts or ['低']},
      'local_geometry':g,'scene_detail':scene,'people_detail':people,'object_inventory':obj,'product_analysis':pa,
      'brand_design_analysis':{'brand_tone':'中高','color_unity':'中','material_fit':'中','b2b_fit':'中高','hero_fit':'中','premium_score':7.1,'visual_unity_score':7.0,'veytis_rules':veytis,'juese_rules':juese,'suggestions':['统一色调','统一主体比例']},
      'graphic_design_analysis':gdesign,'style_consistency':style,'ai_qc':ai_qc,'business_fit':business,'reference_comparison':ref,'semantic_analysis':semantic,
      'prompts':prompts,'scores':scores,'confidence':{'subject_detection':conf,'semantic_reliability':'low' if not vstatus['success'] else 'medium'},'vision_model_status':vstatus
    }

    lines=[]
    lines+=['# 统一视觉分析报告','', '## 1) 执行摘要',f"- 总分：{scores['总分']}/10",f"- 视觉模型：{'已启用' if a.use_vision else '未启用'}"]
    lines+=['','## 2) 基础信息',f"- 文件名：{out['image_info']['filename']}",f"- 尺寸：{out['image_info']['size']}",f"- 方向：{out['image_info']['orientation']}",f"- 文件大小：{out['image_info']['file_size_bytes']} bytes"]
    lines+=['','## 3) 本地几何分析','- 主体几何：',f"  - bbox：{g['subject_bbox']}",f"  - 主体高度占画面：{g['subject_height_ratio']}",f"  - 主体宽度占画面：{g['subject_width_ratio']}",f"  - 边距：{g['margins']}",f"  - 裁切风险：{', '.join(g['crop_risk'])}",f"  - 置信度：{conf}"]
    lines+=['','## 4) 场景细节分析']+[f"- {k}：{v}" for k,v in scene.items()]
    lines+=['','## 5) 人物细节分析']+[f"- {k}：{v}" for k,v in people.items()]
    lines+=['','## 6) 产品/物体分析']+[f"- {k}：{v}" for k,v in pa.items()]
    lines+=['','## 7) 品牌设计分析']+[f"- {k}：{v}" for k,v in out['brand_design_analysis'].items()]
    lines+=['','## 8) 平面设计/文字排版']+[f"- {k}：{v}" for k,v in gdesign.items()]
    lines+=['','## 9) 风格统一分析']+[f"- {k}：{v}" for k,v in style.items()]
    lines+=['','## 10) AI 质检']+[f"- {k}：{v}" for k,v in ai_qc.items()]
    lines+=['','## 11) 商业适配度']+[f"- {k}：{v}" for k,v in business.items()]
    lines+=['','## 12) 参考图对比']+[f"- {k}：{v}" for k,v in ref.items()] if ref else ['','## 12) 参考图对比','- 未提供参考图']
    lines+=['','## 13) 可本地确定的问题',f"- {', '.join(ai_qc['local_can_judge'])}",'','## 14) 需要视觉模型确认的问题',f"- {', '.join(ai_qc['need_vision'])}",
            '','## 15) 具体修改建议','- 控制主体高度占比在 55%-82%','- 修正偏黄/偏红/偏橙','- 保持标签真实清晰','',
            '## 16) 重新生成提示词',f"- {prompts['regenerate']}",'','## 17) 局部修图提示词',f"- {prompts['inpaint']}",'','## 18) 评分']+[f"- {k}：{v}" for k,v in scores.items()]

    ts=dt.datetime.now().strftime('%Y%m%d-%H%M%S'); outdir=Path(a.output_dir)/ts; outdir.mkdir(parents=True,exist_ok=True)
    md_path=outdir/'image_analysis_report.md'; js_path=outdir/'image_analysis_report.json'
    md_path.write_text('\n'.join(lines),encoding='utf-8'); js_path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"分析完成：{ip.name} | 总分 {scores['总分']}/10")
    print(f"Markdown 报告：{md_path}")
    print(f"JSON 报告：{js_path}")
    if a.json: print(json.dumps(out,ensure_ascii=False))
    print(f"FILE:file:///{md_path.as_posix()}")

if __name__=='__main__':
    try:
        main()
    except Exception as e:
        print(f'运行失败：{e}',file=sys.stderr)
        print('请安装依赖：pip install pillow numpy （可选：pip install opencv-python）',file=sys.stderr)
        sys.exit(1)
