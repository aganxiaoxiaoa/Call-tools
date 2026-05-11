#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import math
import os
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageStat

try:
    import cv2  # type: ignore
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False


def clamp(v, a=0.0, b=10.0):
    return max(a, min(b, v))


def rgb_to_hex(rgb):
    return '#{:02X}{:02X}{:02X}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def orientation(w, h):
    if abs(w - h) / max(w, h) < 0.05:
        return '方图'
    return '横图' if w > h else '竖图'


def platform_fit(w, h):
    r = w / h
    fits = []
    if r > 1.5:
        fits += ['网站首页 Hero/Banner', '博客封面', '广告横幅']
    if 0.95 <= r <= 1.05:
        fits += ['社媒帖子', '产品图卡片']
    if r < 0.8:
        fits += ['短视频封面', '故事封面']
    fits += ['产品详情页', '落地页视觉']
    return list(dict.fromkeys(fits))


def analyze_image(path):
    img = Image.open(path).convert('RGB')
    arr = np.array(img)
    h, w = arr.shape[:2]
    pixels = arr.reshape(-1, 3).astype(np.float32)

    sample_idx = np.random.choice(len(pixels), min(25000, len(pixels)), replace=False)
    sample = pixels[sample_idx]

    # dominant colors by coarse quantization
    q = (sample // 16).astype(int)
    bins, counts = np.unique(q, axis=0, return_counts=True)
    top = bins[np.argsort(counts)[::-1][:5]]
    top_colors = [rgb_to_hex(np.clip((b * 16 + 8), 0, 255)) for b in top]

    gray = np.dot(sample[:, :3], [0.299, 0.587, 0.114])
    brightness = float(np.mean(gray) / 255.0)
    contrast = float(np.std(gray) / 128.0)

    maxc = sample.max(axis=1)
    minc = sample.min(axis=1)
    saturation = float(np.mean((maxc - minc) / (maxc + 1e-6)) )

    means = sample.mean(axis=0)
    cast = []
    if means[0] > means[2] + 10:
        cast.append('偏红')
    if means[0] + means[1] > means[2] * 2.2:
        cast.append('偏黄/暖')
    if abs(means[0]-means[1]) < 8 and abs(means[1]-means[2]) < 8:
        cast.append('偏灰')
    if brightness > 0.82:
        cast.append('可能过曝')
    if brightness < 0.25:
        cast.append('可能过暗')

    # blur detection
    clarity = '中等'
    if HAS_CV2:
        g = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        lap_var = cv2.Laplacian(g, cv2.CV_64F).var()
        if lap_var < 80:
            clarity = '偏模糊'
        elif lap_var > 250:
            clarity = '清晰'
    else:
        std = ImageStat.Stat(img.convert('L')).stddev[0]
        clarity = '清晰' if std > 45 else '中等'

    # layout heuristic
    gray2 = np.dot(arr[:, :, :3], [0.299, 0.587, 0.114])
    m = gray2.mean()
    yy, xx = np.indices((h, w))
    weight = np.abs(gray2 - m) + 1e-3
    cx = float((xx * weight).sum() / weight.sum()) / w
    cy = float((yy * weight).sum() / weight.sum()) / h

    thirds = (abs(cx - 1/3) < 0.12 or abs(cx - 2/3) < 0.12) and (abs(cy - 1/3) < 0.12 or abs(cy - 2/3) < 0.12)
    visual_center = '接近三分法焦点' if thirds else '重心偏中央/边缘'

    edge_density = np.mean(np.abs(np.diff(gray2, axis=1)) > 18)
    whitespace = float(np.mean(np.abs(gray2 - m) < 10))

    return {
        'width': w, 'height': h, 'top_colors': top_colors,
        'brightness': brightness, 'contrast': contrast, 'saturation': saturation,
        'casts': cast or ['中性'], 'clarity': clarity,
        'center_x': cx, 'center_y': cy, 'visual_center': visual_center,
        'edge_density': float(edge_density), 'whitespace': whitespace,
    }


def build_report(args, data):
    w, h = data['width'], data['height']
    ratio = f"{w}:{h} (~{w/h:.2f})"
    ori = orientation(w, h)
    fit = '、'.join(platform_fit(w, h))
    brand = args.brand or 'Generic'

    brand_note = ''
    if brand.lower() == 'veytis':
        brand_note = '建议偏冷中性：cool ivory / neutral white / cool greige / muted sage；避免黄红橙偏色。'
    elif 'juese' in brand.lower() or 'clothing' in brand.lower():
        brand_note = '建议真实工厂感：干净明亮冷白自然光，避免过暗过黄与“假工厂棚拍感”。'

    text_input = args.text.strip() if args.text else ''
    text_block = '未提供 --text，以下为基于 use-case 的通用排版建议。'
    if text_input:
        parts = [p.strip() for p in text_input.replace('\n', ' ').split('。') if p.strip()]
        main = parts[0] if parts else text_input[:24]
        sub = parts[1] if len(parts) > 1 else '补充品牌价值与交付能力'
        bullets = parts[2:5] if len(parts) > 2 else ['MOQ/交期透明', '支持打样与质检', '支持 OEM/ODM']
        cta = 'Get Quote / 立即询盘'
        text_block = f"主标题：{main}\n副标题：{sub}\n卖点：- " + "\n- ".join(bullets) + f"\nCTA：{cta}"

    score_color = clamp(6 + (0.55 - abs(data['brightness'] - 0.55)) * 5 + (0.35 - abs(data['saturation'] - 0.35)) * 4)
    score_layout = clamp(7 - data['edge_density'] * 6 + data['whitespace'] * 3)
    score_typo = clamp(7 + data['whitespace'] * 2)
    score_conv = clamp((score_layout + score_typo) / 2)
    score_brand = clamp(7 if brand_note else 6.5)
    score_site = clamp(7 if w >= 1400 else 5.8)
    score_ad = clamp(6.8 if data['contrast'] > 0.25 else 5.5)
    score_ai = clamp(8 - data['saturation'] * 4)
    total = round(float(np.mean([score_color, score_layout, score_typo, score_conv, score_brand, score_site, score_ad, score_ai])), 2)

    md = f"""# 平面设计分析报告

## 1) 图片基础信息
- 文件名：{Path(args.image).name}
- 图片尺寸：{w} x {h}
- 文件大小：{Path(args.image).stat().st_size / 1024:.1f} KB
- 宽高比：{ratio}
- 方向：{ori}
- 适合平台：{fit}
- 清晰度判断：{data['clarity']}
- 分辨率建议：{'可直接商用' if w*h >= 1200*1200 else '建议提升分辨率后再用于主视觉'}

## 2) 色彩与品牌视觉
- 主色 Top5：{', '.join(data['top_colors'])}
- 亮度：{data['brightness']:.2f}（0-1）
- 对比度：{data['contrast']:.2f}
- 饱和度：{data['saturation']:.2f}
- 色温/偏色：{'、'.join(data['casts'])}
- 高级感判断：{'较高级' if 0.35 <= data['saturation'] <= 0.55 and 0.42 <= data['brightness'] <= 0.72 else '有优化空间'}
- B2B 适配：{'较适合' if data['contrast'] > 0.18 else '建议增强层次'}
- 品牌规则建议：{brand_note or 'Generic：保持中性、干净、可信赖的商用视觉。'}

## 3) 构图与版式
- 主体/视觉重心：x={data['center_x']:.2f}, y={data['center_y']:.2f}（{data['visual_center']}）
- 留白估计：{data['whitespace']:.2f}（越高越利于排版）
- 拥挤度：{'偏拥挤' if data['edge_density'] > 0.25 else '可控'}
- 标题承载区：建议优先使用{'左上/上中' if data['center_x']>0.5 else '右上/上中'}留白区域
- CTA 放置：建议靠近标题块下方，保持高对比色按钮
- 裁剪适配：16:9={'好' if w/h>1.25 else '一般'}，1:1={'好' if 0.85<w/h<1.15 else '一般'}，9:16={'好' if w/h<0.75 else '一般'}
- Banner/Hero 适配：{'适合' if w/h>1.35 else '可用但建议重构'}
- 短视频封面适配：{'适合' if w/h<1.0 else '建议二次裁切'}

## 4) 文字排版分析
- 标题建议：8-14字，强调“能力+结果”，例如“B2B 定制供应链，一站式交付”
- 副标题建议：20-40字，补充工厂实力、MOQ、交期、质检
- CTA 建议：Get Quote / Start Your Project / 获取报价
- 字体风格：无衬线（思源黑体/Inter/Helvetica）
- 字重层级：标题 700-800，副标题 400-500，CTA 600-700
- 字号层级（1920 宽参考）：标题 56-72，副标题 24-32，正文 16-20，按钮 18-22
- 字间距/行距：标题字距 0~2%，正文行距 130%~155%
- 中英文排版：英文单词不强制换行；中文每行 14-22 字更稳
- 输入文案拆解：
{text_block}
- 信息层级清晰度：{'较清晰' if data['whitespace']>0.2 else '建议减少元素并增强分组'}

## 5) 质量检查
- 模板感：{'中等' if data['saturation']>0.6 else '较低'}
- 廉价感风险：{'偏高' if data['casts'] and ('偏黄/暖' in data['casts'] or data['saturation']>0.65) else '可控'}
- 过花风险：{'偏高' if data['edge_density']>0.3 else '可控'}
- 文字过多风险：需结合最终文案控制在 3 层信息内
- 按钮可见性：建议使用品牌对比色并加安全边距
- Logo 位置：建议顶角固定并远离主体高细节区域
- 可读性风险：如背景复杂，务必加 20-40% 遮罩
- AI 假感风险：避免过饱和、过度锐化、假文字纹理

## 6) 设计修改建议（可立即执行）
1. 统一白平衡到中性偏冷，移除黄红偏色。
2. 给标题区域增加净空（至少画布宽度的 12%）。
3. CTA 按钮改为高对比纯色，最小高度 44px（移动端）。
4. 背景加轻微暗角或蒙层，提升文字可读性。
5. 减少非关键信息元素，强化“主体-标题-CTA”主路径。

**给设计师指令（示例）**
- “请产出 3 版：极简高级、转化优先、社媒抓眼；统一中性冷白；标题区留白 >= 15%。”

**AI 修图提示词（示例）**
- “clean premium B2B visual, neutral cool white balance, realistic texture, clear focal subject, generous negative space for headline, high contrast CTA area, no yellow cast, no fake text”

**重生成提示词（示例）**
- “professional B2B website hero image, realistic product/factory context, muted palette, balanced composition, typography-safe layout, commercial photography style, high detail, clean background”

## 7) 设计方案（A/B/C）
### 方案 A：极简高级 B2B
- 画布比例：16:9
- 背景：中性浅灰/冷白渐变
- 主图：右侧 55%
- 标题/副标题/CTA：左侧纵向编排
- Logo：左上
- 色彩：低饱和中性色 + 品牌点缀色
- 平台：官网首页、落地页

### 方案 B：商业转化型
- 画布比例：4:3 或 1:1
- 背景：真实场景 + 半透明遮罩
- 主图：中偏右
- 标题：左上；CTA：标题下方首屏可见
- Logo：右上或左上固定
- 平台：广告图、产品页

### 方案 C：社媒吸引型
- 画布比例：9:16
- 背景：高对比但不过饱和
- 主图：中心偏下
- 标题：上三分之一
- CTA：底部安全区
- Logo：顶部角落
- 平台：短视频封面、社媒图

## 8) 评分（0-10）
- 色彩高级感：{score_color:.1f}
- 构图清晰度：{score_layout:.1f}
- 文字排版潜力：{score_typo:.1f}
- 商业转化潜力：{score_conv:.1f}
- 品牌匹配度：{score_brand:.1f}
- 独立站适配度：{score_site:.1f}
- 广告适配度：{score_ad:.1f}
- AI 缺陷风险（高分=低风险）：{score_ai:.1f}
- **总分：{total:.2f}/10**
"""
    return md, total


def main():
    parser = argparse.ArgumentParser(description='Graphic design analyzer (local-only)')
    parser.add_argument('--image', required=True)
    parser.add_argument('--brand', default='Generic')
    parser.add_argument('--use-case', default='website image')
    parser.add_argument('--industry', default='')
    parser.add_argument('--mode', default='full', choices=['design-review', 'typography', 'layout', 'ad-review', 'website-banner', 'social-cover', 'full'])
    parser.add_argument('--language', default='Chinese')
    parser.add_argument('--text', default='')
    parser.add_argument('--ratio', default='')
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f'图片不存在: {image_path}')

    data = analyze_image(image_path)
    md, total = build_report(args, data)

    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    out_dir = Path('D:/bot/outputs/graphic_design_analyzer') / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / 'graphic_design_report.md'
    json_path = out_dir / 'graphic_design_report.json'

    md_path.write_text(md, encoding='utf-8')
    json_path.write_text(json.dumps({'args': vars(args), 'analysis': data, 'total_score': total}, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'分析完成：{image_path.name} | 总分 {total}/10 | 模式 {args.mode}')
    print(f'报告已保存：{md_path.resolve()}')
    print(f'JSON已保存：{json_path.resolve()}')
    print('FILE:file:///' + str(md_path.resolve()).replace('\\', '/'))


if __name__ == '__main__':
    main()
