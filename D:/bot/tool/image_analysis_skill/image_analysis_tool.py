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
    np = None
try:
    import cv2
except ImportError:
    cv2 = None

IMG_EXT={'.jpg','.jpeg','.png','.webp','.bmp','.tif','.tiff'}

def ratio_text(w,h):
    g=math.gcd(max(1,w),max(1,h)); return f'{w//g}:{h//g}'

def parse_pct(s):
    if not s: return None
    m=re.match(r'\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$',s)
    return float(m.group(1))/100.0 if m else None

def top_colors(img):
    if np is None:
        q=img.convert('P',palette=Image.ADAPTIVE,colors=5); pal=q.getpalette(); out=[]
        for c,i in sorted(q.getcolors() or [], reverse=True)[:5]: out.append({'rgb':pal[i*3:i*3+3],'count':int(c)})
        return out
    a=np.array(img.resize((min(img.width,320),min(img.height,320)))).reshape(-1,3)
    q=(a//32)*32; u,c=np.unique(q,axis=0,return_counts=True); idx=np.argsort(c)[::-1][:5]
    return [{'rgb':u[i].astype(int).tolist(),'count':int(c[i])} for i in idx]

def detect_subject_bbox(im,use_alpha=False):
    rgba=im.convert('RGBA'); arr=np.array(rgba) if np is not None else None
    w,h=im.size
    conf='high'
    if arr is not None and (use_alpha or 'A' in im.getbands()) and arr[:,:,3].max()>5:
        m=arr[:,:,3]>10
    else:
        rgb=np.array(im.convert('RGB')) if np is not None else None
        if rgb is None:
            g=np.array(im.convert('L')); bg=np.median(np.concatenate([g[0,:],g[-1,:],g[:,0],g[:,-1]])); m=np.abs(g-bg)>18; conf='low'
        else:
            corners=np.vstack([rgb[0,0],rgb[0,-1],rgb[-1,0],rgb[-1,-1]]).astype(np.float32); bg=corners.mean(axis=0)
            d=np.linalg.norm(rgb.astype(np.float32)-bg,axis=2)
            m=d>22
            if cv2 is not None:
                m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))>0
                m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))>0
            if m.mean()<0.02 or m.mean()>0.95: conf='low'
    ys,xs=np.where(m)
    if len(xs)==0: return {'bbox':[0,0,w-1,h-1],'confidence':'low','method':'fallback_full'}
    x1,x2,y1,y2=int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())
    return {'bbox':[x1,y1,x2,y2],'confidence':conf,'method':'alpha' if ('A' in im.getbands()) else 'bg-edge'}

def geom_metrics(bbox,w,h):
    x1,y1,x2,y2=bbox; sw=max(1,x2-x1+1); sh=max(1,y2-y1+1)
    m={'subject_bbox':bbox,'subject_width_px':sw,'subject_height_px':sh,'subject_width_ratio':round(sw/w,4),'subject_height_ratio':round(sh/h,4),
       'margins':{'left':x1,'right':w-1-x2,'top':y1,'bottom':h-1-y2}}
    risks=[]
    if y1<=2: risks.append('顶部可能被切掉')
    if y2>=h-3: risks.append('底部可能被切掉')
    if m['subject_height_ratio']>0.9: risks.append('主体过大（>90%）')
    if m['subject_height_ratio']<0.35: risks.append('主体偏小（<35%）')
    if min(x1,y1,w-1-x2,h-1-y2)<8: risks.append('主体接近边缘，存在裁切风险')
    m['crop_risk']=risks or ['低']
    return m

def bottle_rules(subject):
    sw,sh=subject['subject_width_px'],subject['subject_height_px']; ar=sw/max(1,sh)
    cap=max(1,int(sh*0.16)); label=max(1,int(sh*0.42)); body=sh-cap
    style='接近 4oz/120mL Boston round' if 0.28<=ar<=0.45 else ('过高过瘦（serum感）' if ar<0.28 else '偏矮偏胖（jar感）')
    return {'product_aspect_ratio':round(ar,4),'cap_height_px':cap,'label_height_px':label,'cap_height_ratio':round(cap/sh,4),
            'label_height_ratio':round(label/sh,4),'bottle_body_ratio':round(body/sh,4),'bottle_shape_verdict':style}

def reference_compare(cur,ref,expected_change):
    if not ref: return {}
    ref_ratio=ref['subject_height_ratio']; cur_ratio=cur['subject_height_ratio']; actual=cur_ratio/max(1e-6,ref_ratio)
    expected=1.0+(expected_change or 0.0) if expected_change is not None else None
    diff=None if expected is None else actual-expected
    verdict='无预期变更，仅输出实际比例'
    if expected is not None:
        if abs(actual-0.75)<=0.08: verdict='只是矮 25%'
        elif actual<=0.6: verdict='接近砍半，不符合要求'
        elif actual>0.85: verdict='高度变化不足'
    return {'reference_height_px':ref['subject_height_px'],'current_height_px':cur['subject_height_px'],'expected_ratio':expected,
            'actual_ratio':round(actual,4),'difference':None if diff is None else round(diff,4),'verdict':verdict}

def text_layout(text):
    if not text: return {}
    parts=[p.strip() for p in re.split(r'[\n|;；]+',text) if p.strip()]
    title=parts[0] if parts else ''
    sub=parts[1] if len(parts)>1 else ''
    bullets=[p for p in parts[2:-1] if len(p)<40]
    cta=parts[-1] if parts and any(k in parts[-1].lower() for k in ['buy','shop','learn','contact','立即','了解']) else 'Contact Us'
    return {'title':title,'subtitle':sub,'bullets':bullets,'cta':cta,'font':'Title:现代衬线/Subtitle:无衬线','sizes':'H1 48-72px, H2 24-36px, Body 16-20px','spacing':'行距1.25-1.45，字距0-2%'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--image',required=True); p.add_argument('--brand',default='Generic'); p.add_argument('--industry',default='')
    p.add_argument('--use-case',default='product photo',dest='use_case')
    p.add_argument('--mode',default='full',choices=['basic','full','product-geometry','brand-design','graphic-design','style-consistency','qc','prompt'])
    p.add_argument('--object-type',default='generic',choices=['bottle','jar','box','garment','factory','poster','banner','generic'])
    p.add_argument('--reference'); p.add_argument('--reference-dir'); p.add_argument('--expected-height-change')
    p.add_argument('--text'); p.add_argument('--ratio'); p.add_argument('--use-alpha',action='store_true')
    p.add_argument('--use-vision',action='store_true'); p.add_argument('--vision-provider',default='none',choices=['none','gemini','qwen','openai'])
    a=p.parse_args()

    ip=Path(a.image)
    if not ip.exists(): print(f'错误：图片不存在：{ip}',file=sys.stderr); sys.exit(1)
    im=Image.open(ip); w,h=im.size; rgb=im.convert('RGB'); stat=ImageStat.Stat(rgb); mean=[round(x,2) for x in stat.mean]
    brightness=round(sum(mean)/3,2); contrast=round(sum(stat.stddev)/3,2)
    sat=None
    if np is not None:
        ar=np.array(rgb).astype(np.float32); mx=ar.max(axis=2); mn=ar.min(axis=2); sat=round(float(np.mean(np.where(mx==0,0,(mx-mn)/np.maximum(mx,1)))*100),2)
    color_bias='偏黄/偏红' if mean[0]-mean[2]>12 else ('偏冷' if mean[2]-mean[0]>12 else '中性')
    subj=detect_subject_bbox(im,a.use_alpha); subm=geom_metrics(subj['bbox'],w,h); subm['detection_confidence']=subj['confidence']; subm['method']=subj['method']

    product={}
    if a.object_type=='bottle' or a.brand.lower()=='veytis': product=bottle_rules(subm)
    brand_notes=[]
    if a.brand.lower()=='veytis':
        brand_notes += ['偏好 cool ivory / neutral white / pale stone / cool greige / light taupe / muted sage']
        if '偏黄/偏红' in color_bias: brand_notes += ['当前有 warm cast 风险，建议白平衡降暖并降红']
    if 'juese' in a.brand.lower() or a.object_type in ('factory','garment'):
        brand_notes += ['工厂图应 documentary realism、干净明亮、避免脏乱与假设备']
        if brightness<95: brand_notes += ['画面偏暗，建议提亮 8-15%']

    gd={
        'visual_center':'中部偏下', 'headline_zone':'上1/3留白区', 'subtitle_zone':'标题下方', 'cta_zone':'右下/下中', 'logo_zone':'左上或右上',
        'text_whitespace_score':round((1-subm['subject_width_ratio']*subm['subject_height_ratio'])*10,2),
        'text_contrast_score':round((contrast/64)*10,2), 'template_like_risk':'中', 'cheap_look_risk':'低' if contrast>30 else '中高',
        'ad_suitability':'适合' if brightness>85 else '一般', 'homepage_suitability':'适合' if subm['subject_height_ratio']<0.85 else '偏满'
    }
    gd['text_plan']=text_layout(a.text)

    style={'consistency_score':None,'differences':{},'suggestions':[]}
    if a.reference_dir:
        rd=Path(a.reference_dir)
        refs=[f for f in rd.iterdir() if f.suffix.lower() in IMG_EXT] if rd.exists() else []
        if refs:
            vals=[]
            for f in refs[:50]:
                ri=Image.open(f).convert('RGB'); rs=ImageStat.Stat(ri); rb=sum(rs.mean)/3; rc=sum(rs.stddev)/3
                rg=geom_metrics(detect_subject_bbox(ri,False)['bbox'],ri.width,ri.height)
                vals.append((rb,rc,rg['subject_height_ratio']))
            mb=sum(v[0] for v in vals)/len(vals); mc=sum(v[1] for v in vals)/len(vals); mh=sum(v[2] for v in vals)/len(vals)
            db,dc,dh=brightness-mb,contrast-mc,subm['subject_height_ratio']-mh
            score=max(0,10-(abs(db)/12+abs(dc)/10+abs(dh)*12))
            style={'consistency_score':round(score,2),'differences':{'亮度差异':round(db,2),'对比度差异':round(dc,2),'主体大小差异':round(dh,4),'色调差异':color_bias},
                   'suggestions':['统一白平衡到中性偏冷','统一主体高度占比在参考均值±8%','统一对比度曲线']}

    ref_cmp={}
    if a.reference and Path(a.reference).exists():
        rim=Image.open(a.reference); rsub=geom_metrics(detect_subject_bbox(rim,a.use_alpha)['bbox'],rim.width,rim.height)
        ref_cmp=reference_compare(subm,rsub,parse_pct(a.expected_height_change))

    ai_qc={
        'ai_feel':'中' if contrast<18 else '低到中', 'label_text_risk':'中', 'product_ratio_risk':'低' if product else '中',
        'bottle_deform_risk':'低' if product.get('product_aspect_ratio',0)>=0.25 else '中高','hand_anomaly_risk':'无法本地稳定检测',
        'perspective_risk':'中', 'background_unreal_risk':'中' if subm['detection_confidence']=='low' else '低',
        'over_smooth_risk':'中' if contrast<15 else '低', 'over_sharpen_risk':'中' if contrast>70 else '低',
        'color_cast_risk':color_bias, 'local_judgable':['主体bbox','主体占比','亮度','对比度','色偏','裁切风险'],
        'needs_vision_model':['手部异常','文字真假语义','设备语义真实性']
    }

    prompts={
        'regenerate_en':'realistic commercial image, clean composition, true-to-life texture, neutral-cool white balance',
        'retouch_en':'reduce warm cast, refine product proportion, preserve realistic details, improve background cleanliness',
        'negative_prompt':'fake text, warped bottle, distorted perspective, plastic skin, over-smooth, oversharpen, yellow cast, red cast',
        'zh_explain':'根据本地几何与色彩分析生成；优先修正比例、偏色、留白和商业可用性。'
    }
    if a.brand.lower()=='veytis': prompts['regenerate_en'] += ', 4oz/120mL amber boston round dropper bottle, premium essential oils wholesale style'
    if 'juese' in a.brand.lower(): prompts['regenerate_en'] += ', documentary garment factory, organized production floor, clean cool lighting'
    if a.mode=='graphic-design': prompts['regenerate_en'] += ', clear text-safe area, hierarchy for headline subtitle CTA logo'

    scores={'真实感':round(max(0,10-abs(contrast-35)/7),2),'品牌匹配度':round(8.5 if not brand_notes else 7.2,2),'独立站适配度':round(8.2 if brightness>90 else 6.8,2),
            '色彩高级感':round(8.0 if color_bias!='偏黄/偏红' else 6.2,2),'构图清晰度':round(8.0 if subm['subject_height_ratio']<0.88 else 6.5,2),
            'AI缺陷风险(高分=低风险)':6.5}
    scores['总分']=round(sum(scores.values())/len(scores),2)

    out={
      'image_info':{'file':str(ip),'filename':ip.name,'size':f'{w}x{h}','ratio':ratio_text(w,h),'mode':im.mode,'brand':a.brand,'use_case':a.use_case,'industry':a.industry},
      'color_analysis':{'top5':top_colors(rgb),'mean_rgb':mean,'brightness':brightness,'contrast':contrast,'saturation':sat,'color_bias':color_bias},
      'subject_geometry':subm,
      'product_geometry':product,
      'brand_design_analysis':{'brand_tone_match':'较匹配' if len(brand_notes)<=1 else '部分不匹配','notes':brand_notes or ['色彩与构图整体可用于通用品牌素材'],'premium_feel':'中高'},
      'graphic_design_analysis':gd,
      'style_consistency':style,
      'ai_qc':ai_qc,
      'reference_comparison':ref_cmp,
      'business_fit':{'homepage_hero':'可用' if subm['subject_height_ratio']<0.88 else '偏拥挤','product_page':'可用','ad_creative':gd['ad_suitability'],'short_video_cover':'可用','major_issues':subm['crop_risk'],'fixes':['修正偏色','统一主体占比','补充文字安全区']},
      'prompts':prompts,
      'scores':scores,
      'confidence':{'subject_detection':subj['confidence'],'style_consistency':'medium' if style['consistency_score'] is not None else 'n/a','local_only':True,'vision_used':False}
    }

    md=['# 统一视觉分析报告','', '## 1. 基础信息', f"- 文件名：{out['image_info']['filename']}", f"- 尺寸：{out['image_info']['size']}", f"- 比例：{out['image_info']['ratio']}",
        '## 2. 色彩分析', f"- 色偏：{color_bias}", f"- 亮度/对比度/饱和度：{brightness}/{contrast}/{sat}",
        '## 3. 主体几何分析', f"- BBox：{subm['subject_bbox']}", f"- 主体高占比：{subm['subject_height_ratio']}", f"- 裁切风险：{'；'.join(subm['crop_risk'])}",
        '## 4. 产品比例分析', f"- 结果：{product if product else '非瓶类或未启用瓶类分析'}",
        '## 5. 品牌设计分析', f"- {out['brand_design_analysis']}",
        '## 6. 平面设计 / 排版分析', f"- {gd}",
        '## 7. 风格统一分析', f"- {style}",
        '## 8. AI 质检', f"- {ai_qc}",
        '## 9. 商业适配度', f"- {out['business_fit']}",
        '## 10. 参考图对比', f"- {ref_cmp or '未提供参考图'}",
        '## 11. 需要人工确认的项目', f"- {', '.join(ai_qc['needs_vision_model'])}",
        '## 12. 可直接执行的修改建议', '- 校正白平衡到中性偏冷\n- 主体高度控制到画面 55%-82%\n- 确保标题区留白',
        '## 13. 重新生成/局部修图提示词', f"- {prompts}",
        '## 14. 评分', f"- {scores}"]

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
        print(f'运行失败：{e}',file=sys.stderr)
        print('请安装依赖：pip install pillow numpy （可选：pip install opencv-python）',file=sys.stderr)
        sys.exit(1)
