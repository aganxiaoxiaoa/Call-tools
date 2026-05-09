#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2B 独立站运营工具（本地、无付费 API）。"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Dict, List

OUTPUT_BASE = Path(r"D:\bot\outputs\business_tools")


def now_dir() -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = OUTPUT_BASE / stamp
    out.mkdir(parents=True, exist_ok=True)
    return out


def slug(text: str) -> str:
    return "_".join(text.strip().lower().replace("/", " ").split())[:80] or "output"


def save_outputs(command: str, md_text: str, data: Dict) -> Path:
    out_dir = now_dir()
    md_path = out_dir / f"{command}.md"
    json_path = out_dir / f"{command}.json"
    txt_path = out_dir / f"{command}.txt"

    md_path.write_text(md_text, encoding="utf-8")
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    txt_path.write_text(md_text, encoding="utf-8")
    return out_dir


def kw_list(raw: str) -> List[str]:
    return [k.strip() for k in raw.split(",") if k.strip()]


def geo_plan(args):
    kws = kw_list(args.keywords)
    data = {
        "geo_optimization": [f"{args.country} 本地买家意图词覆盖", "B2B 采购决策链内容分层", "本地行业术语 + 商业合规词整合"],
        "search_intent": {"informational": kws[:3], "commercial": kws[3:6], "transactional": kws[6:] or kws[:2]},
        "keyword_clusters": [
            {"cluster": "supplier", "keywords": kws[:3]},
            {"cluster": "pricing", "keywords": [f"{args.product} price", f"{args.product} MOQ"]},
            {"cluster": "customization", "keywords": [f"custom {args.product}", "private label"]},
        ],
        "blog_topics": [f"How to choose {args.product} supplier in {args.country}", f"{args.product} MOQ and lead time guide"],
        "landing_modules": ["Hero", "Trust Badges", "B2B Service", "Process", "FAQ", "CTA"],
        "faq": ["What is your MOQ?", "Can you provide samples?", "What is lead time?", "Do you support OEM/ODM?"],
        "schema": ["Organization", "Product", "FAQPage", "BreadcrumbList"],
        "localization": [f"{args.language} 本地表达 + 度量单位本地化", "付款与物流条款本地习惯化"],
    }
    md = "# GEO + SEO 内容计划\n\n" + "\n".join([f"- **{k}**: {v}" for k, v in data.items()])
    return md, data


def blog_brief(args):
    kws = kw_list(args.keywords)
    data = {
        "title_options": [f"{args.topic}: Complete B2B Guide", f"How {args.brand} solves {args.topic}"],
        "meta_title": f"{args.topic} | {args.brand} {args.industry}",
        "meta_description": f"Practical B2B insights on {args.topic} for {args.country} buyers.",
        "outline": {"H1": args.topic, "H2": ["Market Context", "How to Choose Supplier", "Cost & MOQ", "FAQ"], "H3": ["Checklist", "Case Example"]},
        "angles": ["采购风控", "成本优化", "交期稳定性"],
        "conversion_points": ["询盘按钮", "样品申请", "报价下载"],
        "internal_links": ["About", "Product Category", "Case Study", "Contact"],
        "faq": ["MOQ?", "Lead time?", "Payment terms?"],
        "image_suggestions": [f"{args.industry} factory shot", f"{args.topic} process diagram"],
        "cta": "Request a B2B quote within 24 hours.",
        "keywords": kws,
    }
    md = "# 博客写作简报\n\n" + json.dumps(data, ensure_ascii=False, indent=2)
    return md, data


def blog_draft(args):
    brief_md, brief = blog_brief(args)
    checklist = ["主关键词在标题/H1/首段出现", "每300词一个小标题", "加入FAQ结构化问答", "添加内部链接和CTA"]
    data = {"brief": brief, "draft_template": "见 Markdown", "seo_checklist": checklist}
    md = f"# 博客初稿框架\n\n{brief_md}\n\n## 正文模板\n- 引言：说明痛点\n- 章节1：背景与趋势（写作提示：提供数据来源占位）\n- 章节2：解决方案（写作提示：对比3种方案）\n- 章节3：采购清单（写作提示：给出可执行步骤）\n- 结论与CTA（写作提示：引导询盘）\n\n## SEO检查清单\n" + "\n".join([f"- [ ] {c}" for c in checklist])
    return md, data


def landing_page(args):
    data = {
        "hero_title": f"{args.brand} - Reliable {args.product} for {args.audience}",
        "subtitle": f"{args.country} focused {args.industry} solutions",
        "trust": ["Factory Direct", "Quality Control", "On-time Delivery"],
        "b2b_modules": ["Capabilities", "Customization", "Case Studies"],
        "custom_process": ["需求确认", "样品", "量产", "质检", "发货"],
        "advantages": ["稳定供应", "可定制", "响应快"],
        "cta": ["Get Quote", "Request Sample", "Talk on WhatsApp"],
        "faq": ["MOQ?", "Lead Time?", "Shipping Methods?"],
        "seo": ["标题含主关键词", "FAQ schema", "本地化货币/单位"],
    }
    return "# 落地页结构\n\n" + json.dumps(data, ensure_ascii=False, indent=2), data


def video_script(args):
    data = {
        "title": f"{args.topic} | {args.brand}",
        "hook_0_3s": "Stop wasting budget on unreliable suppliers.",
        "storyboard": ["0-3s Hook", "4-10s Pain", "11-22s Solution", "23-30s CTA"],
        "voiceover": ["Here is how we ensure quality...", "From sampling to shipping..."],
        "captions": ["Factory verified", "MOQ flexible", "Fast lead time"],
        "visuals": [args.style, "close-up process", "team communication"],
        "b_roll": ["machine run", "packing line", "QC inspection"],
        "cta": "DM us for full catalog.",
        "capcut_timeline": ["00:00 hook", "00:04 body", "00:23 CTA"],
    }
    return "# 短视频脚本\n\n" + json.dumps(data, ensure_ascii=False, indent=2), data


def image_prompt(args):
    brand = args.brand.lower()
    brand_hint = ""
    if "veytis" in brand:
        brand_hint = "essential oils, hydrosols, aromatherapy raw materials, B2B supplier setting"
    if "juese" in brand:
        brand_hint = "garment factory, sample room, custom clothing production, B2B apparel manufacturing"
    prompt_en = f"{args.scene}, {args.product}, {args.style}, {args.ratio}, commercial photography, ultra-detailed, {brand_hint}".strip(", ")
    data = {
        "prompt_en": prompt_en,
        "cn_explain": "用于生成B2B业务真实场景图，突出供应能力与专业度。",
        "negative_prompt": "low quality, blurry, extra fingers, watermark, text artifacts, unrealistic plastic texture",
        "composition": ["主体明确", "前中后景", "留白用于文案"],
        "material_light_lens": ["真实材质", "softbox主光+轮廓光", "35mm/50mm镜头感"],
        "realism_checklist": ["品牌和行业一致", "光影合理", "细节无畸形", "可用于官网/社媒"],
    }
    return "# 图片提示词\n\n" + json.dumps(data, ensure_ascii=False, indent=2), data


def inquiry_reply(args):
    data = {
        "reply_en": "Thanks for your inquiry. Could you share target quantity, specs, and delivery destination so we can prepare an accurate quote?",
        "cn_explain": "先感谢询盘，再索取报价关键参数。",
        "follow_up_questions": ["Target MOQ?", "Customization requirements?", "Destination port?", "Required certifications?"],
        "pre_quote_checklist": ["产品规格", "数量", "包装要求", "交期", "贸易条款", "付款方式"],
        "whatsapp_short": "Thanks! Please share qty + specs + destination, we’ll quote fast.",
    }
    return "# 客户询盘回复\n\n" + json.dumps(data, ensure_ascii=False, indent=2), data


def faq(args):
    cats = ["MOQ", "定制", "打样", "交期", "包装", "物流", "付款", "质量", "认证"]
    items = [{"category": c, "q": f"{c}相关常见问题？", "a": f"这里给出{args.brand}在{c}方面的标准答复模板。"} for c in cats]
    items += [{"category": "售后", "q": "How do you handle claims?", "a": "Standard claim workflow with evidence and resolution timeline."}]
    data = {"faq": items}
    return "# B2B FAQ\n\n" + json.dumps(data, ensure_ascii=False, indent=2), data


def content_calendar(args):
    platforms = kw_list(args.platforms)
    days = []
    for i in range(1, 31):
        days.append({"day": i, "theme": f"Day {i} topic", "channels": platforms, "keywords": [f"{args.industry} keyword {i}"], "cta": "Contact for quote", "assets": "factory photo / short clip / chart"})
    data = {"calendar": days}
    return "# 30天内容日历\n\n" + json.dumps(data, ensure_ascii=False, indent=2), data


def prompt_pack(args):
    class A: pass
    a = A(); a.__dict__.update(args.__dict__)
    a.keywords = f"{args.topic}, {args.product}, {args.industry}"
    a.intent = "commercial"
    b_md, b = blog_brief(a)
    v_md, v = video_script(a)
    i = A(); i.brand=args.brand; i.industry=args.industry; i.scene=args.topic; i.product=args.product; i.style="commercial realistic"; i.ratio="16:9"; i.language=args.language
    i_md, i_data = image_prompt(i)
    f = A(); f.brand=args.brand; f.industry=args.industry; f.product=args.product; f.country=args.country; f.language=args.language
    f_md, f_data = faq(f)
    data = {"blog_brief": b, "video_script": v, "image_prompt": i_data, "faq": f_data}
    md = "# Prompt Pack\n\n" + "\n\n".join([b_md, v_md, i_md, f_md])
    return md, data


CMDS = {
    "geo-plan": geo_plan,
    "blog-brief": blog_brief,
    "blog-draft": blog_draft,
    "landing-page": landing_page,
    "video-script": video_script,
    "image-prompt": image_prompt,
    "inquiry-reply": inquiry_reply,
    "faq": faq,
    "content-calendar": content_calendar,
    "prompt-pack": prompt_pack,
}


def add_common(sub):
    sub.add_argument("--brand", required=True)
    sub.add_argument("--industry", required=True)


def build_parser():
    p = argparse.ArgumentParser(description="B2B marketing local tool")
    sp = p.add_subparsers(dest="command", required=True)

    s = sp.add_parser("geo-plan"); add_common(s); s.add_argument("--country", required=True); s.add_argument("--language", required=True); s.add_argument("--product", required=True); s.add_argument("--audience", required=True); s.add_argument("--keywords", required=True)
    s = sp.add_parser("blog-brief"); add_common(s); s.add_argument("--topic", required=True); s.add_argument("--country", required=True); s.add_argument("--language", required=True); s.add_argument("--keywords", required=True); s.add_argument("--intent", required=True)
    s = sp.add_parser("blog-draft"); add_common(s); s.add_argument("--topic", required=True); s.add_argument("--country", required=True); s.add_argument("--language", required=True); s.add_argument("--keywords", required=True); s.add_argument("--intent", required=True)
    s = sp.add_parser("landing-page"); add_common(s); s.add_argument("--product", required=True); s.add_argument("--country", required=True); s.add_argument("--language", required=True); s.add_argument("--audience", required=True); s.add_argument("--keywords", required=True)
    s = sp.add_parser("video-script"); add_common(s); s.add_argument("--topic", required=True); s.add_argument("--platform", required=True); s.add_argument("--duration", required=True); s.add_argument("--language", required=True); s.add_argument("--style", required=True)
    s = sp.add_parser("image-prompt"); add_common(s); s.add_argument("--scene", required=True); s.add_argument("--product", required=True); s.add_argument("--style", required=True); s.add_argument("--ratio", required=True); s.add_argument("--language", required=True)
    s = sp.add_parser("inquiry-reply"); add_common(s); s.add_argument("--customer-message", required=True); s.add_argument("--tone", required=True); s.add_argument("--language", required=True)
    s = sp.add_parser("faq"); add_common(s); s.add_argument("--product", required=True); s.add_argument("--country", required=True); s.add_argument("--language", required=True)
    s = sp.add_parser("content-calendar"); add_common(s); s.add_argument("--country", required=True); s.add_argument("--language", required=True); s.add_argument("--platforms", required=True)
    s = sp.add_parser("prompt-pack"); add_common(s); s.add_argument("--topic", required=True); s.add_argument("--country", required=True); s.add_argument("--language", required=True); s.add_argument("--product", required=True)
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        md, data = CMDS[args.command](args)
        out_dir = save_outputs(args.command, md, data)
        print(f"[OK] Output saved to: {out_dir}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
