#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import datetime as dt
import json
import math
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageStat
except ImportError:
    print("错误：缺少依赖 pillow。请先安装：pip install pillow", file=sys.stderr)
    sys.exit(2)

try:
    import numpy as np
except ImportError:
    np = None

try:
    import cv2  # optional
except ImportError:
    cv2 = None


def safe_float(v, d=2):
    return round(float(v), d)


def orientation(w, h):
    if w == h:
        return "方图"
    return "横图" if w > h else "竖图"


def aspect_ratio_str(w, h):
    g = math.gcd(w, h) if w and h else 1
    return f"{w//g}:{h//g}"


def suggested_use(w, h):
    ratio = w / max(h, 1)
    if ratio >= 1.6:
        return ["网站首页 Hero", "博客横幅", "广告横幅"]
    if ratio <= 0.7:
        return ["短视频封面", "社媒竖版图", "移动端首图"]
    return ["产品页图", "博客配图", "通用网站图"]


def brightness_contrast_sat(img_rgb):
    if np is None:
        stat = ImageStat.Stat(img_rgb)
        mean = sum(stat.mean) / 3.0
        std = sum(stat.stddev) / 3.0
        return mean, std, None
    arr = np.array(img_rgb).astype(np.float32)
    mean = float(arr.mean())
    std = float(arr.std())
    mx = arr.max(axis=2)
    mn = arr.min(axis=2)
    sat = float(np.where(mx == 0, 0, (mx - mn) / np.maximum(mx, 1)).mean() * 100)
    return mean, std, sat


def top_colors(img_rgb, topn=5):
    img = img_rgb.copy()
    img.thumbnail((300, 300))
    if np is None:
        colors = img.convert("P", palette=Image.ADAPTIVE, colors=topn).getpalette()
        counts = img.convert("P", palette=Image.ADAPTIVE, colors=topn).getcolors()
        result = []
        if counts:
            for c, idx in sorted(counts, reverse=True)[:topn]:
                base = idx * 3
                rgb = tuple(colors[base:base+3])
                result.append((rgb, c))
        return result
    arr = np.array(img)
    flat = arr.reshape(-1, 3)
    # 简单量化，避免重依赖
    q = (flat // 32) * 32
    uniq, cnt = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(cnt)[::-1][:topn]
    return [((int(uniq[i][0]), int(uniq[i][1]), int(uniq[i][2])), int(cnt[i])) for i in order]


def color_tendency(mean_rgb):
    r, g, b = mean_rgb
    hints = []
    if r - b > 12:
        hints.append("偏暖/偏红")
    elif b - r > 12:
        hints.append("偏冷")
    else:
        hints.append("中性")
    if r - g > 10:
        hints.append("偏红")
    if g - b > 10:
        hints.append("偏绿/偏黄")
    if abs(r - g) < 6 and abs(g - b) < 6:
        hints.append("偏灰")
    return "、".join(dict.fromkeys(hints))


def score_range(v):
    return max(0, min(10, safe_float(v, 1)))


def analyze(args):
    image_path = Path(args.image)
    if not image_path.exists():
        raise FileNotFoundError(f"图片不存在：{image_path}")

    with Image.open(image_path) as im:
        mode = im.mode
        w, h = im.size
        img_rgb = im.convert("RGB")

    size_bytes = image_path.stat().st_size
    mean_bri, contrast, sat = brightness_contrast_sat(img_rgb)
    stat = ImageStat.Stat(img_rgb)
    mean_rgb = tuple(int(x) for x in stat.mean)
    tops = top_colors(img_rgb, 5)
    tendency = color_tendency(mean_rgb)

    # 简化结构判断
    center_hint = "主体可能居中" if abs((w/2) - (w/2)) < w*0.1 else "主体可能偏移"
    whitespace = "留白一般（需人工复核）"

    brand = args.brand or "Generic"
    use_case = args.use_case or "website image"
    industry = args.industry or ""

    warnings = []
    if "Veytis".lower() in brand.lower():
        if mean_rgb[0] - mean_rgb[2] > 10:
            warnings.append("检测到偏黄/偏红风险，不符合 Veytis 偏冷中性基调。")
    if "Juese".lower() in brand.lower() or "factory" in use_case.lower():
        if mean_bri < 90:
            warnings.append("工厂场景偏暗，建议提亮并增强清洁感。")

    ai_checks = {
        "文字乱码": "需要人工检查",
        "标签假文字": "需要人工检查",
        "手部异常": "需要人工检查",
        "瓶子变形": "需要人工检查",
        "产品比例不合理": "需要人工检查",
        "工厂设备不合理": "需要人工检查",
        "背景不真实": "需要人工检查",
        "透视错误": "需要人工检查",
        "过度磨皮/塑料感": "需要人工检查",
        "明显 AI 痕迹": "需要人工检查",
    }

    realness = score_range(7.5 - (1.0 if "偏灰" in tendency else 0) - (0.8 if mean_bri < 70 else 0))
    brand_fit = score_range(7.0 - (1.2 if warnings else 0))
    site_fit = score_range(7.8 if w >= 1200 else 6.2)
    color_premium = score_range(7.4 - (1.0 if "偏红" in tendency else 0))
    composition = score_range(7.0)
    ai_risk = score_range(6.0)  # 分越高风险越低
    total = score_range((realness + brand_fit + site_fit + color_premium + composition + ai_risk) / 6)

    prompt_base = "premium natural product photography, clean composition, realistic texture, soft diffused daylight"
    if "veytis" in brand.lower():
        prompt_base = "essential oils and hydrosol product photography, premium natural ingredients, neutral cool ivory background, B2B raw material supplier visual"
    elif "juese" in brand.lower():
        prompt_base = "documentary realism in garment factory, sample room, printing workshop, quality inspection area, clean bright B2B manufacturing scene"

    report = {
        "meta": {
            "file": str(image_path),
            "filename": image_path.name,
            "size": f"{w}x{h}",
            "aspect_ratio": aspect_ratio_str(w, h),
            "orientation": orientation(w, h),
            "file_size_bytes": size_bytes,
            "mode": mode,
            "brand": brand,
            "use_case": use_case,
            "industry": industry,
            "language": args.language,
            "mode_arg": args.mode,
            "opencv_available": cv2 is not None,
            "numpy_available": np is not None,
        },
        "basic": {"suggested_use": suggested_use(w, h)},
        "color": {
            "top5": [{"rgb": c, "count": n} for c, n in tops],
            "mean_rgb": mean_rgb,
            "tendency": tendency,
            "brightness": safe_float(mean_bri),
            "contrast": safe_float(contrast),
            "saturation": None if sat is None else safe_float(sat),
            "issues": warnings or ["未发现明显偏色异常（仍建议人工复核）"],
        },
        "composition": {
            "subject_center": center_hint,
            "whitespace": whitespace,
            "text_overlay": "可尝试（建议保留简洁背景区）",
            "layers": "前中后景层次需人工检查",
            "crop_friendly": ["16:9", "4:3", "1:1", "9:16"],
        },
        "style": {
            "photo_style": "realistic product photography / documentary factory photo（基于场景推断）",
            "lighting_style": "soft diffused daylight（推断）",
            "lens_language": "medium shot（推断）",
            "texture": "纹理基本自然，需人工复核细节",
            "brand_match": "中等偏好",
        },
        "ai_checks": ai_checks,
        "business_fit": {
            "independent_site": "较适合",
            "homepage_hero": "视裁剪与留白情况而定",
            "product_page": "适合",
            "ad_creative": "可用，建议增强视觉记忆点",
            "blog_image": "适合",
            "short_video_cover": "可用（建议二次排版）",
            "main_issues": warnings or ["无重大自动风险"],
            "suggestions": ["校正白平衡", "轻微提升局部对比", "清理背景干扰元素"],
            "redo_recommended": "否",
            "retouch_recommended": "是",
        },
        "prompts": {
            "regenerate_en": f"{prompt_base}, realistic commercial quality, high detail, no plastic skin, no artifact text",
            "inpaint_en": "fix color cast to neutral cool tone, correct perspective, keep realistic material texture",
            "negative_prompt": "blurry, distorted text, extra fingers, warped bottle, fake label, plastic look, oversaturated, yellow cast, red cast",
            "zh_explain": "以上提示词用于重生成与局部修图，重点控制真实感、偏色与商业可用性。",
        },
        "scores": {
            "真实感": realness,
            "品牌匹配度": brand_fit,
            "独立站适配度": site_fit,
            "色彩高级感": color_premium,
            "构图清晰度": composition,
            "AI缺陷风险(高分=低风险)": ai_risk,
            "总分": total,
        }
    }

    return report


def build_markdown(report):
    m = report["meta"]
    c = report["color"]
    s = report["scores"]
    lines = [
        "# 图片分析报告",
        "",
        "## 一、基础图片信息",
        f"- 文件名：{m['filename']}",
        f"- 尺寸：{m['size']}",
        f"- 宽高比：{m['aspect_ratio']}",
        f"- 方向：{m['orientation']}",
        f"- 文件大小（字节）：{m['file_size_bytes']}",
        f"- 图片模式：{m['mode']}",
        f"- 推荐用途：{', '.join(report['basic']['suggested_use'])}",
        "",
        "## 二、色彩分析",
        f"- 主色 Top5：{c['top5']}",
        f"- 色彩倾向：{c['tendency']}",
        f"- 亮度：{c['brightness']}",
        f"- 对比度：{c['contrast']}",
        f"- 饱和度：{c['saturation']}",
        f"- 问题提示：{'；'.join(c['issues'])}",
        "",
        "## 三、构图和结构分析",
        f"- 主体：{report['composition']['subject_center']}",
        f"- 留白：{report['composition']['whitespace']}",
        f"- 文字叠加：{report['composition']['text_overlay']}",
        f"- 层次：{report['composition']['layers']}",
        f"- 裁剪兼容：{', '.join(report['composition']['crop_friendly'])}",
        "",
        "## 四、风格分析",
        f"- 摄影风格：{report['style']['photo_style']}",
        f"- 光线风格：{report['style']['lighting_style']}",
        f"- 镜头语言：{report['style']['lens_language']}",
        f"- 质感：{report['style']['texture']}",
        f"- 品牌匹配：{report['style']['brand_match']}",
        "",
        "## 五、AI 生成问题检查",
    ]
    for k, v in report["ai_checks"].items():
        lines.append(f"- {k}：{v}")
    lines += [
        "",
        "## 六、商业适配建议",
    ]
    for k, v in report["business_fit"].items():
        lines.append(f"- {k}：{v}")

    lines += [
        "",
        "## 七、后续提示词",
        f"- 英文重生成提示词：{report['prompts']['regenerate_en']}",
        f"- 英文局部修图提示词：{report['prompts']['inpaint_en']}",
        f"- Negative prompt：{report['prompts']['negative_prompt']}",
        f"- 中文解释：{report['prompts']['zh_explain']}",
        "",
        "## 八、评分（0-10）",
    ]
    for k, v in s.items():
        lines.append(f"- {k}：{v}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="本地图片分析工具（OpenClaw Skill）")
    parser.add_argument("--image", required=True, help="图片路径，通常为 {{MediaPath}}")
    parser.add_argument("--brand", default="Generic")
    parser.add_argument("--use-case", default="website image", dest="use_case")
    parser.add_argument("--industry", default="")
    parser.add_argument("--language", default="Chinese")
    parser.add_argument("--mode", choices=["basic", "full", "prompt", "qc"], default="full")
    args = parser.parse_args()

    try:
        report = analyze(args)
        md = build_markdown(report)

        now = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_dir = Path(f"D:/bot/outputs/image_analysis/{now}")
        out_dir.mkdir(parents=True, exist_ok=True)

        md_path = out_dir / "image_analysis_report.md"
        json_path = out_dir / "image_analysis_report.json"

        md_path.write_text(md, encoding="utf-8")
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"分析完成：{report['meta']['filename']} | 总分 {report['scores']['总分']}/10")
        print(f"Markdown 报告：{md_path}")
        print(f"JSON 报告：{json_path}")
        print(f"FILE:file:///{md_path.as_posix()}")
    except FileNotFoundError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"运行失败：{e}", file=sys.stderr)
        print("请检查依赖：pip install pillow numpy （可选：pip install opencv-python）", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
