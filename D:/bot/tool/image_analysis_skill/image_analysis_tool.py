#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, datetime as dt, json, math, re, sys
from pathlib import Path
try:
    from PIL import Image, ImageStat
except ImportError:
    print('错误：缺少 pillow，请安装：pip install pillow', file=sys.stderr); sys.exit(2)
try:
    import numpy as np
except ImportError:
    np=None
try:
    import cv2
except ImportError:
    cv2=None

IMG_EXT={'.jpg','.jpeg','.png','.webp','.bmp','.tif','.tiff'}

def pct(s):
    if not s:return None
    m=re.match(r'\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$',s); return float(m.group(1))/100 if m else None

def top_colors(img):
    if np is None:
        q=img.convert('P',palette=Image.ADAPTIVE,colors=5); pal=q.getpalette(); return [{'rgb':pal[i*3:i*3+3],'count':int(c)} for c,i in sorted(q.getcolors() or [],reverse=True)[:5]]
    a=np.array(img.resize((min(320,img.width),min(320,img.height)))).reshape(-1,3); q=(a//32)*32; u,c=np.unique(q,axis=0,return_counts=True); idx=np.argsort(c)[::-1][:5]
    return [{'rgb':u[i].astype(int).tolist(),'count':int(c[i])} for i in idx]

def detect_bbox(im,use_alpha=False):
    w,h=im.size
    if np is None: return [0,0,w-1,h-1],'low','fallback'
    rgba=np.array(im.convert('RGBA'))
    if (use_alpha or 'A' in im.getbands()) and rgba[:,:,3].max()>6:
        m=rgba[:,:,3]>10; method='alpha'; conf='high'
    else:
        rgb=np.array(im.convert('RGB')).astype(np.float32)
        bg=np.vstack([rgb[0,0],rgb[0,-1],rgb[-1,0],rgb[-1,-1]]).mean(axis=0); d=np.linalg.norm(rgb-bg,axis=2); m=d>22
        if cv2 is not None:
            m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))>0
            m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))>0
        method='bg-edge'; conf='low' if m.mean()<0.02 or m.mean()>0.95 else 'medium'
    ys,xs=np.where(m)
    if len(xs)==0:return [0,0,w-1,h-1],'low','fallback_full'
    return [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],conf,method

def geom(bbox,w,h):
    x1,y1,x2,y2=bbox; sw=max(1,x2-x1+1); sh=max(1,y2-y1+1)
    risks=[]
    if y1<=2:risks.append('顶部可能被切掉')
    if y2>=h-3:risks.append('底部可能被切掉')
    if sh/h>0.9:risks.append('主体过大>90%')
    if sh/h<0.35:risks.append('主体过小<35%')
    if min(x1,y1,w-1-x2,h-1-y2)<8:risks.append('边缘过近有裁切风险')
    return {'subject_bbox':bbox,'subject_width_px':sw,'subject_height_px':sh,'subject_width_ratio':round(sw/w,4),'subject_height_ratio':round(sh/h,4),
            'margins':{'left':x1,'right':w-1-x2,'top':y1,'bottom':h-1-y2},'crop_risk':risks or ['低']}

def bottle(g):
    sh,sw=g['subject_height_px'],g['subject_width_px']; ar=sw/max(1,sh)
    cap=int(sh*0.16); label=int(sh*0.42)
    v='接近4oz/120mL Boston round' if 0.28<=ar<=0.45 else ('过高过瘦' if ar<0.28 else '偏矮偏胖')
    return {'product_aspect_ratio':round(ar,4),'cap_estimate':cap,'label_estimate':label,'cap_height_ratio':round(cap/sh,4),'label_height_ratio':round(label/sh,4),'shape_verdict':v}

def ref_cmp(cur,ref,exp):
    if not ref:return {}
    actual=cur['subject_height_ratio']/max(1e-6,ref['subject_height_ratio']); er=1+(exp or 0) if exp is not None else None
    if er is None:ver='无目标变更，仅输出实际比例'
    elif abs(actual-0.75)<=0.08:ver='只是矮 25%'
    elif actual<=0.6:ver='接近砍半，不符合要求'
    else:ver='高度变化不足'
    return {'reference_height_px':ref['subject_height_px'],'current_height_px':cur['subject_height_px'],'expected_ratio':er,'actual_ratio':round(actual,4),'difference':None if er is None else round(actual-er,4),'verdict':ver}

def local_scene(scene_type,g,brightness,contrast,color_bias):
    return {'scene_type_judgement':scene_type,'elements':['主体产品/对象','背景结构','光源区域','地面/墙面/台面'],'space_structure':{'前景':'主体附近','中景':'主体主要区域','背景':'环境层',
    '主体位置':'中部偏下','视觉重心':'中心偏下','景深关系':'中等','拥挤度':'中等' if g['subject_height_ratio']>0.78 else '较疏朗','留白':'中等' if g['subject_height_ratio']<0.85 else '不足','文字适配':'可放文字' if g['subject_height_ratio']<0.82 else '需扩展留白'},
    'lighting_logic':{'主光方向':'左上->右下(估计)','阴影方向':'右下(估计)','不合理光斑风险':'低到中','过暗':brightness<85,'过曝':brightness>225,'偏色':color_bias,'真实摄影逻辑': '基本合理' if contrast>12 else '偏平'},
    'realism_checks':{'真实照片感':'中高' if contrast>18 else '中','AI合成感':'中' if contrast<16 else '低到中','样板间/假场景风险':'中','透视错误风险':'中低'}}

def local_people(detect_people,scene_type):
    if not detect_people:return {'enabled':False,'message':'已关闭人物检测'}
    return {'enabled':True,'people_count_estimate':0,'positions':[],'actions':'本地模式无法可靠识别人动作','pose_naturalness':'未知','hand_risk':'未知','face_naturalness':'未知(不做身份识别)',
            'clothing_scene_fit':'未知','gaze':'未知','interaction':'未知','staged_risk':'中','b2b_fit':'需视觉模型确认','ai_people_risks':['手指异常需视觉模型','人脸变形需视觉模型']}

def run_vision_analysis(image_path,prompt,provider,model):
    # 占位：实际接入由用户本地环境配置。此函数仅示范接口与回退结构。
    raise RuntimeError(f'vision provider={provider}, model={model} 当前未在本地配置')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--image',required=True); p.add_argument('--brand',default='Generic'); p.add_argument('--industry',default=''); p.add_argument('--use-case',default='product photo',dest='use_case')
    p.add_argument('--mode',default='full',choices=['scene-detail','people-detail','semantic-full','brand-full','commercial-qc','style-consistency','graphic-design','product-geometry','full'])
    p.add_argument('--analysis-depth',default='standard',choices=['basic','standard','deep'])
    p.add_argument('--scene-type',default='generic',choices=['product_photo','factory_scene','showroom','office','warehouse','workshop','poster','banner','social_post','website_hero','generic'])
    p.add_argument('--object-type',default='generic',choices=['bottle','jar','box','garment','factory','poster','banner','generic'])
    p.add_argument('--reference'); p.add_argument('--reference-dir'); p.add_argument('--expected-height-change'); p.add_argument('--text'); p.add_argument('--ratio')
    p.add_argument('--use-alpha',action='store_true'); p.add_argument('--use-vision',action='store_true'); p.add_argument('--vision-provider',default='none',choices=['none','qwen','gemini','openai','local'])
    p.add_argument('--vision-model',default=''); p.add_argument('--ocr',action='store_true'); p.add_argument('--detect-people',action='store_true',default=True)
    p.add_argument('--detect-products',action='store_true',default=True); p.add_argument('--detect-layout',action='store_true',default=True)
    a=p.parse_args()

    ip=Path(a.image)
    if not ip.exists(): print(f'错误：图片不存在：{ip}',file=sys.stderr); sys.exit(1)
    im=Image.open(ip); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb); mean=[round(x,2) for x in st.mean]
    brightness=round(sum(mean)/3,2); contrast=round(sum(st.stddev)/3,2)
    sat=None
    if np is not None:
        ar=np.array(rgb).astype(np.float32); mx=ar.max(axis=2); mn=ar.min(axis=2); sat=round(float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100),2)
    color_bias='偏黄/偏红' if mean[0]-mean[2]>12 else ('偏冷' if mean[2]-mean[0]>12 else '中性')

    bbox,conf,method=detect_bbox(im,a.use_alpha); g=geom(bbox,w,h); g['detection_confidence']=conf; g['method']=method
    pa=bottle(g) if (a.object_type=='bottle' or a.brand.lower()=='veytis') else {'product_aspect_ratio':round(g['subject_width_px']/max(1,g['subject_height_px']),4)}

    rc={}
    if a.reference and Path(a.reference).exists():
        rim=Image.open(a.reference); rb,_,_=detect_bbox(rim,a.use_alpha); rc=ref_cmp(g,geom(rb,rim.width,rim.height),pct(a.expected_height_change))

    style={'consistency_score':None,'diff':{},'suggestions':[]}
    if a.reference_dir and Path(a.reference_dir).exists():
        vals=[]
        for f in [x for x in Path(a.reference_dir).iterdir() if x.suffix.lower() in IMG_EXT][:40]:
            ri=Image.open(f).convert('RGB'); rs=ImageStat.Stat(ri); rb=sum(rs.mean)/3; rct=sum(rs.stddev)/3; bb,_,_=detect_bbox(ri,False); rg=geom(bb,ri.width,ri.height)
            vals.append((rb,rct,rg['subject_height_ratio']))
        if vals:
            mb=sum(x[0] for x in vals)/len(vals); mc=sum(x[1] for x in vals)/len(vals); mh=sum(x[2] for x in vals)/len(vals)
            db,dc,dh=brightness-mb,contrast-mc,g['subject_height_ratio']-mh; score=max(0,10-(abs(db)/12+abs(dc)/10+abs(dh)*12))
            style={'consistency_score':round(score,2),'diff':{'色调差异':color_bias,'亮度差异':round(db,2),'对比度差异':round(dc,2),'主体大小差异':round(dh,4),'构图差异':'中(按主体占比估算)'},
                   'suggestions':['统一白平衡','统一主体高度占比','统一背景材质与对比度曲线']}

    scene=local_scene(a.scene_type,g,brightness,contrast,color_bias)
    people=local_people(a.detect_people,a.scene_type)
    obj_inv={'local_detectable':['主体bbox','主体比例','背景亮暗结构','近似色调'],'semantic_limit':'本地无法可靠识别精确物体类别/标签文字语义'}
    semantic={'message':'未开启视觉模型，本地模式无法可靠识别场景语义、人物细节和标签文字；以下为几何/色彩/构图分析。'}
    vision_status={'enabled':a.use_vision,'provider':a.vision_provider,'model':a.vision_model or 'none','success':False,'fallback_to_local':True,'error':None}

    if a.use_vision and a.vision_provider!='none':
        try:
            vr=run_vision_analysis(str(ip),'analyze scene people objects',a.vision_provider,a.vision_model)
            semantic=vr.get('semantic_analysis',semantic); scene=vr.get('scene_detail',scene); people=vr.get('people_detail',people); obj_inv=vr.get('object_inventory',obj_inv)
            vision_status.update({'success':True,'fallback_to_local':False})
        except Exception as e:
            vision_status['error']=str(e)

    brand_notes=[]
    if a.brand.lower()=='veytis':
        if color_bias=='偏黄/偏红': brand_notes.append('Veytis 色调不合规：偏黄/偏红')
        brand_notes.append(f"瓶型检查：{pa.get('shape_verdict','未启用')}")
    if 'juese' in a.brand.lower() or a.scene_type in ('factory_scene','workshop','warehouse','showroom'):
        brand_notes += ['应体现 documentary factory realism','避免脏乱/过暗/假设备']

    gd={'headline_area':'上1/3','subheadline_area':'标题下','cta_area':'右下','logo_area':'左上或右上','text_bg_contrast':round((contrast/64)*10,2),'hierarchy':'中高','text_overload_risk':'中' if a.analysis_depth=='deep' else '低中',
        'template_risk':'中','cheap_risk':'低' if contrast>24 else '中','ad_fit':'适合' if brightness>85 else '一般','homepage_fit':'适合' if g['subject_height_ratio']<0.85 else '偏满','short_cover_fit':'可用',
        'text_safe_zone':'四角与上方留白区'}

    ai_qc={'ai_feel':'中' if contrast<18 else '低中','label_text_risk':'需视觉模型/OCR确认' if not a.ocr else '已请求OCR(若视觉不可用则回退)','product_ratio_risk':'低' if 0.25<=pa.get('product_aspect_ratio',0.33)<=0.5 else '中高',
           'bottle_deform_risk':'低' if '接近4oz' in pa.get('shape_verdict','') else '中','perspective_risk':scene['realism_checks']['透视错误风险'],'background_logic_risk':'中',
           'local_confirmed':['bbox','主体比例','裁切风险','色偏','亮度','对比度'],'need_vision':['人物动作细节','标签文字真实性','设备语义逻辑']}

    business={'independent_site':'适合' if g['subject_height_ratio']<0.88 else '需优化','homepage_hero':gd['homepage_fit'],'product_page':'适合','about_page':'可用','blog_cover':'适合','ad_fit':gd['ad_fit'],
              'b2b_scene_fit':'需视觉模型确认' if not vision_status['success'] else '已评估','major_issues':g['crop_risk'],'suggestions':['统一中性偏冷色调','保持主体占比55%-82%','增强文字安全区']}

    prompts={'regenerate':'realistic commercial image, clean composition, neutral-cool tone, consistent product proportion, realistic texture','inpaint':'fix crop and proportion, remove warm cast, improve label realism, keep natural shadows','negative':'fake text, warped object, wrong perspective, plastic look, yellow/red cast','zh':'用于重生成和局部修图，优先修正比例、偏色、语义真实性。'}

    scores={'真实感':round(max(0,10-abs(contrast-35)/7),2),'品牌匹配度':round(7.0 if brand_notes else 8.2,2),'商业适配度':round(8.0 if brightness>90 else 6.9,2),'构图与留白':round(8.1 if g['subject_height_ratio']<0.85 else 6.6,2),'风格统一潜力':round(style['consistency_score'] if style['consistency_score'] is not None else 6.8,2)}
    scores['总分']=round(sum(scores.values())/len(scores),2)

    out={'image_info':{'file':str(ip),'size':f'{w}x{h}','brand':a.brand,'scene_type':a.scene_type,'mode':a.mode,'analysis_depth':a.analysis_depth},'local_geometry':g,
         'scene_detail':scene,'people_detail':people,'object_inventory':obj_inv,'product_analysis':pa,'brand_design_analysis':{'tone':'中高','notes':brand_notes,'veytis_rules':'已检查' if a.brand.lower()=='veytis' else 'n/a','juese_rules':'已检查' if 'juese' in a.brand.lower() else 'n/a'},
         'graphic_design_analysis':gd,'style_consistency':style,'ai_qc':ai_qc,'business_fit':business,'reference_comparison':rc,'semantic_analysis':semantic,
         'prompts':prompts,'scores':scores,'confidence':{'subject_detection':conf,'local_only':not vision_status['success'],'semantic_reliability':'low' if not vision_status['success'] else 'medium/high'},'vision_model_status':vision_status}

    md=['# 统一视觉分析报告','## 1. 执行摘要',f"- 总分：{scores['总分']}，模式：{a.mode}，视觉模型：{'开启' if a.use_vision else '未开启'}",'## 2. 基础信息',f"- {out['image_info']}",'## 3. 本地几何分析',f"- {g}",'## 4. 场景细节分析',f"- {scene}",'## 5. 人物细节分析',f"- {people}",'## 6. 产品/物体分析',f"- {pa}",'## 7. 品牌设计分析',f"- {out['brand_design_analysis']}",'## 8. 平面设计/文字排版',f"- {gd}",'## 9. 风格统一分析',f"- {style}",'## 10. AI 质检',f"- {ai_qc}",'## 11. 商业适配度',f"- {business}",'## 12. 参考图对比',f"- {rc or '未提供'}",'## 13. 可本地确定的问题',f"- {ai_qc['local_confirmed']}",'## 14. 需要视觉模型确认的问题',f"- {ai_qc['need_vision']}",'## 15. 具体修改建议','- 校正偏黄/偏红\n- 控制主体占比\n- 清理背景干扰','## 16. 重新生成提示词',f"- {prompts['regenerate']}",'## 17. 局部修图提示词',f"- {prompts['inpaint']}",'## 18. 评分',f"- {scores}"]

    t=dt.datetime.now().strftime('%Y%m%d-%H%M%S'); od=Path(f'D:/bot/outputs/image_analysis/{t}'); od.mkdir(parents=True,exist_ok=True)
    mdp=od/'image_analysis_report.md'; jsp=od/'image_analysis_report.json'
    mdp.write_text('\n\n'.join(md),encoding='utf-8'); jsp.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"分析完成：{ip.name} | 总分 {scores['总分']}/10")
    print(f'Markdown 报告：{mdp}')
    print(f'JSON 报告：{jsp}')
    print(f'FILE:file:///{mdp.as_posix()}')

if __name__=='__main__':
    try: main()
    except Exception as e:
        print(f'运行失败：{e}',file=sys.stderr); print('请安装依赖：pip install pillow numpy （可选：pip install opencv-python）',file=sys.stderr); sys.exit(1)
