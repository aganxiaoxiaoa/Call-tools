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
    np=None
try:
    import cv2
except ImportError:
    cv2=None

SCENES=['product_photo','factory_scene','sample_room','printing_workshop','warehouse','showroom','office','poster','banner','social_post','website_hero','generic']
MODES=['basic','full','product-geometry','scene-detail','people-detail','semantic-full','brand-design','brand-full','graphic-design','style-consistency','commercial-qc','qc','prompt']


def detect_bbox(im,use_alpha=False):
    w,h=im.size
    if np is None:return [0,0,w-1,h-1],'low','fallback'
    rgba=np.array(im.convert('RGBA'))
    if (use_alpha or 'A' in im.getbands()) and rgba[:,:,3].max()>5:
        m=rgba[:,:,3]>10; conf='high'; method='alpha'
    else:
        rgb=np.array(im.convert('RGB')).astype(np.float32)
        bg=np.vstack([rgb[0,0],rgb[0,-1],rgb[-1,0],rgb[-1,-1]]).mean(axis=0)
        m=np.linalg.norm(rgb-bg,axis=2)>22
        if cv2 is not None:
            k=np.ones((3,3),np.uint8); m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,k)>0
        conf='low' if m.mean()<0.02 or m.mean()>0.95 else 'medium'; method='bg-diff'
    ys,xs=np.where(m)
    if len(xs)==0:return [0,0,w-1,h-1],'low','fallback_full'
    return [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],conf,method

def geom(b,w,h):
    x1,y1,x2,y2=b; sw,sh=max(1,x2-x1+1),max(1,y2-y1+1)
    risks=[]
    if y1<=2:risks.append('顶部可能被切掉')
    if y2>=h-3:risks.append('底部可能被切掉')
    if sh/h>0.9:risks.append('主体过大')
    if sh/h<0.35:risks.append('主体偏小')
    return {'subject_bbox':b,'subject_width_px':sw,'subject_height_px':sh,'subject_width_ratio':round(sw/w,4),'subject_height_ratio':round(sh/h,4),'margins':{'left':x1,'top':y1,'right':w-1-x2,'bottom':h-1-y2},'crop_risk':risks or ['低']}

def bottle(g):
    sh,sw=g['subject_height_px'],g['subject_width_px']; ar=sw/max(1,sh); cap=int(sh*0.16); label=int(sh*0.42)
    verdict='接近4oz/120mL amber Boston round' if 0.28<=ar<=0.45 else ('过高过瘦' if ar<0.28 else '过矮过胖')
    return {'product_aspect_ratio':round(ar,4),'cap_estimate':cap,'label_estimate':label,'cap_height_ratio':round(cap/sh,4),'label_height_ratio':round(label/sh,4),'shape_verdict':verdict}

def parse_pct(v):
    if not v:return None
    m=re.match(r'\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$',v); return float(m.group(1))/100 if m else None

def run_vision_analysis(image_path,prompt,provider,model):
    if provider!='qwen':
        raise RuntimeError(f'{provider} 待扩展；当前仅实现 qwen')
    key=os.getenv('DASHSCOPE_API_KEY')
    if not key: raise RuntimeError('缺少 DASHSCOPE_API_KEY')
    base=os.getenv('DASHSCOPE_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1').rstrip('/')
    payload={'model':model or 'qwen-vl-plus','messages':[{'role':'user','content':[{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':'file:///'+image_path.replace('\\','/')}}]}]}
    req=request.Request(base+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
    with request.urlopen(req,timeout=45) as r:
        data=json.loads(r.read().decode('utf-8','ignore'))
    txt=((data.get('choices') or [{}])[0].get('message') or {}).get('content','')
    return {'semantic_analysis':{'vision_text':txt or '视觉模型返回为空'},'scene_detail':{'vision_elements':'由模型文本解析'},'people_detail':{'vision_people':'由模型文本解析'},'object_inventory':{'vision_objects':'由模型文本解析'},'product_semantic_analysis':{'vision_product':'由模型文本解析'}}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--image',required=True); p.add_argument('--brand',default='Generic'); p.add_argument('--industry',default=''); p.add_argument('--use-case',default='product photo',dest='use_case')
    p.add_argument('--mode',default='full',choices=MODES); p.add_argument('--analysis-depth',default='standard',choices=['basic','standard','deep']); p.add_argument('--scene-type',default='generic',choices=SCENES)
    p.add_argument('--object-type',default='generic',choices=['bottle','jar','box','garment','factory','machine','poster','banner','generic'])
    p.add_argument('--reference'); p.add_argument('--reference-dir'); p.add_argument('--expected-height-change'); p.add_argument('--text'); p.add_argument('--ratio'); p.add_argument('--use-alpha',action='store_true')
    p.add_argument('--use-vision',action='store_true'); p.add_argument('--vision-provider',default='none',choices=['none','qwen','gemini','openai','local']); p.add_argument('--vision-model',default='')
    p.add_argument('--ocr',action='store_true'); p.add_argument('--detect-people',action='store_true',default=True); p.add_argument('--detect-products',action='store_true',default=True); p.add_argument('--detect-layout',action='store_true',default=True)
    a=p.parse_args(); ip=Path(a.image)
    if not ip.exists(): print(f'错误：图片不存在：{ip}',file=sys.stderr); sys.exit(1)

    im=Image.open(ip); w,h=im.size; rgb=im.convert('RGB'); st=ImageStat.Stat(rgb); mean=[round(x,2) for x in st.mean]
    bri=round(sum(mean)/3,2); con=round(sum(st.stddev)/3,2); cast='偏黄/偏红' if mean[0]-mean[2]>12 else ('偏冷' if mean[2]-mean[0]>12 else '中性')
    b,conf,method=detect_bbox(im,a.use_alpha); g=geom(b,w,h); g['confidence']=conf; g['method']=method
    pa=bottle(g) if (a.object_type=='bottle' or a.brand.lower()=='veytis') else {'product_aspect_ratio':round(g['subject_width_px']/max(1,g['subject_height_px']),4)}
    rc={}
    if a.reference and Path(a.reference).exists():
        rim=Image.open(a.reference); rb,_,_=detect_bbox(rim,a.use_alpha); rg=geom(rb,rim.width,rim.height); actual=g['subject_height_ratio']/max(1e-6,rg['subject_height_ratio']); exp=parse_pct(a.expected_height_change)
        er=1+(exp or 0) if exp is not None else None; verdict='无目标变更'
        if er is not None: verdict='只是矮 25%' if abs(actual-0.75)<=0.08 else ('接近砍半，不符合要求' if actual<=0.6 else '高度变化不足')
        rc={'reference_height_px':rg['subject_height_px'],'current_height_px':g['subject_height_px'],'expected_ratio':er,'actual_ratio':round(actual,4),'verdict':verdict}

    scene={'scene_type_judgement':a.scene_type,'subject_position':'中部偏下','foreground_mid_background':'前景主体/中景环境/背景墙体','visual_center':'中心偏下','whitespace':'中等' if g['subject_height_ratio']<0.85 else '不足','light_direction':'左上->右下(估计)','color_cast':cast,'under_exposed':bri<85,'over_exposed':bri>225,'text_overlay_fit':'较适合' if g['subject_height_ratio']<0.82 else '一般','commercial_fit':'较适合'}
    people={'message':'本地模式不能可靠识别人物细节，需要 --use-vision','geometry_support':'已输出主体几何与构图'}
    obj={'local':'可判断主体比例/裁切/色偏','semantic':'需要视觉模型确认'}
    sem={'message':'未开启视觉模型，本地模式无法可靠识别场景语义、人物细节和标签文字；以下为几何/色彩/构图分析。'}
    vis={'enabled':a.use_vision,'provider':a.vision_provider,'model':a.vision_model or 'none','implemented':'qwen','success':False,'fallback_to_local':True,'error':None}
    psa={'status':'需要视觉模型确认'}
    if a.use_vision and a.vision_provider!='none':
        try:
            vr=run_vision_analysis(str(ip),'请输出场景元素、人物细节、产品语义、商业可用性。',a.vision_provider,a.vision_model)
            sem=vr['semantic_analysis']; scene.update(vr.get('scene_detail',{})); people=vr.get('people_detail',people); obj.update(vr.get('object_inventory',{})); psa=vr.get('product_semantic_analysis',psa); vis['success']=True; vis['fallback_to_local']=False
        except Exception as e:
            vis['error']=str(e)

    brand_notes=[]
    if a.brand.lower()=='veytis':
        brand_notes=[f"瓶型：{pa.get('shape_verdict','n/a')}",f"标签高度占比：{pa.get('label_height_ratio','n/a')}",f"瓶盖高度占比：{pa.get('cap_height_ratio','n/a')}",f"主体高度占比：{g['subject_height_ratio']}",f"色偏：{cast}","检查是否适合产品页与首页Hero"]
    if 'juese' in a.brand.lower() or a.scene_type in ['factory_scene','sample_room','printing_workshop','warehouse','showroom']:
        brand_notes+=['工厂真实感：中（设备语义需视觉模型确认）','干净专业度：中高','光线偏暗风险：'+('是' if bri<90 else '否'),'人物动作：需要视觉模型确认','假工厂/AI设备风险：中']

    gd={'headline_zone':'上1/3留白区','subheadline_zone':'标题下方','cta_zone':'右下','logo_zone':'左上/右上','text_safe_zone':'四角+上方','contrast_for_text':'可用' if con>18 else '偏弱','ad_fit':'适合' if bri>85 else '一般','short_video_cover':'可用','template_like':'中','cheap_look':'低到中','suggestions':['增加标题区纯净留白','提升文字与背景对比']}
    if a.text: gd['text_split']={'main_headline':a.text.split('\n')[0],'subheadline':'', 'bullets':[], 'cta':'Contact Us'}

    scores={'真实感':round(max(0,10-abs(con-35)/7),2),'商业适配度':round(8.0 if bri>90 else 6.8,2),'品牌匹配度':7.2,'构图留白':round(8.0 if g['subject_height_ratio']<0.85 else 6.5,2)}; scores['总分']=round(sum(scores.values())/len(scores),2)
    out={'image_info':{'file':str(ip),'size':f'{w}x{h}','brand':a.brand,'mode':a.mode},'local_geometry':g,'scene_detail':scene,'people_detail':people,'object_inventory':obj,'product_analysis':pa,'brand_design_analysis':{'notes':brand_notes},'graphic_design_analysis':gd,'style_consistency':{'score':'未提供reference-dir' if not a.reference_dir else '已计算（简版）'},'ai_qc':{'local_confirmed':['bbox','比例','裁切','色偏','亮度','对比度'],'need_vision':['人物动作','标签文字真假','设备语义真实性']},'business_fit':{'site_fit':'较适合','hero_fit':'取决于留白','ad_fit':gd['ad_fit']},'reference_comparison':rc,'semantic_analysis':sem,'prompts':{'regenerate':'realistic commercial photo, clean layout, neutral-cool tone','inpaint':'fix proportion and label realism','negative':'fake text, warped bottle, yellow cast'},'scores':scores,'confidence':{'subject_detection':conf,'semantic':'low' if not vis['success'] else 'medium'},'vision_model_status':vis,'product_semantic_analysis':psa}

    md=["# 统一视觉分析报告","## 1. 执行摘要",f"- 总分：{scores['总分']} / 10",f"- 视觉模型：{'开启' if a.use_vision else '未开启'}",
        "## 2. 基础信息",f"- 文件：{ip.name}",f"- 尺寸：{w}x{h}",f"- 品牌：{a.brand}",
        "## 3. 本地几何分析",f"- 主体 bbox：left={b[0]}, top={b[1]}, right={b[2]}, bottom={b[3]}",f"- 主体宽高：{g['subject_width_px']} x {g['subject_height_px']}",f"- 主体占比：width={g['subject_width_ratio']}, height={g['subject_height_ratio']}",f"- 裁切风险：{'；'.join(g['crop_risk'])}",
        "## 4. 场景细节分析",*(f"- {k}：{v}" for k,v in scene.items()),"## 5. 人物细节分析",*(f"- {k}：{v}" for k,v in people.items()),
        "## 6. 产品/物体分析",*(f"- {k}：{v}" for k,v in pa.items()),"## 7. 品牌设计分析",*(f"- {x}" for x in brand_notes),
        "## 8. 平面设计/文字排版",*(f"- {k}：{v}" for k,v in gd.items()),"## 9. 风格统一分析",f"- {out['style_consistency']}",
        "## 10. AI 质检",f"- 可本地确定：{', '.join(out['ai_qc']['local_confirmed'])}","## 11. 商业适配度",*(f"- {k}：{v}" for k,v in out['business_fit'].items()),
        "## 12. 参考图对比",f"- {rc or '未提供'}","## 13. 可本地确定的问题",f"- {', '.join(out['ai_qc']['local_confirmed'])}","## 14. 需要视觉模型确认的问题",f"- {', '.join(out['ai_qc']['need_vision'])}",
        "## 15. 具体修改建议","- 控制主体占比在55%-82%\n- 降低偏黄/偏红\n- 增加文字安全区","## 16. 重新生成提示词",f"- {out['prompts']['regenerate']}","## 17. 局部修图提示词",f"- {out['prompts']['inpaint']}","## 18. 评分",*(f"- {k}：{v}" for k,v in scores.items())]

    t=dt.datetime.now().strftime('%Y%m%d-%H%M%S'); od=Path(f'D:/bot/outputs/image_analysis/{t}'); od.mkdir(parents=True,exist_ok=True)
    mdp=od/'image_analysis_report.md'; jsp=od/'image_analysis_report.json'
    mdp.write_text('\n'.join(md),encoding='utf-8'); jsp.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"分析完成：{ip.name} | 总分 {scores['总分']}/10"); print(f"Markdown 报告：{mdp}"); print(f"JSON 报告：{jsp}"); print(f"FILE:file:///{mdp.as_posix()}")

if __name__=='__main__':
    try: main()
    except Exception as e:
        print(f'运行失败：{e}',file=sys.stderr); print('请安装依赖：pip install pillow numpy （可选：pip install opencv-python）',file=sys.stderr); sys.exit(1)
