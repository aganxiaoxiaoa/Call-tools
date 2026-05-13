#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

DEFAULT_OUTPUT_BASE = Path(r"D:\bot\outputs\business_tools")

BRAND_PROFILES = {
    "veytis": {
        "products": ["essential oils", "hydrosols", "fragrance oils", "carrier oils"],
        "use_cases": ["private label oil line", "spa sourcing", "aromatherapy distribution"],
        "docs": ["COA available upon request", "MSDS available upon request", "IFRA/SGS where applicable"],
        "visual": [
            "neutral cool white/ivory/greige background",
            "no yellow/red/orange cast",
            "premium clean B2B tabletop look",
            "real bottle proportion and legible label layout",
        ],
        "video": ["raw material", "mixing/lab", "filling", "packing", "warehouse dispatch"],
    },
    "juese": {
        "products": ["custom hoodies", "custom t-shirts", "sportswear", "apparel OEM"],
        "use_cases": ["brand launch", "bulk merch", "teamwear manufacturing"],
        "docs": ["QC checkpoint summary", "material confirmation upon request"],
        "visual": [
            "documentary factory realism",
            "real workstation and sewing logic",
            "clean industrial lighting",
            "no fake AI machinery or luxury showroom staging",
        ],
        "video": ["pattern/sample room", "cutting", "printing/embroidery", "QC", "packing/shipping"],
    },
    "generic": {
        "products": ["B2B product"],
        "use_cases": ["bulk sourcing"],
        "docs": ["documents available upon request"],
        "visual": ["clean B2B visual style"],
        "video": ["capability", "process", "quality", "delivery"],
    },
}


def profile_key(brand: str | None, selected: str) -> str:
    if selected != "auto":
        return selected
    b = (brand or "").lower()
    if "veytis" in b:
        return "veytis"
    if "juese" in b:
        return "juese"
    return "generic"


def slugify(text: str | None) -> str:
    s = (text or "page").strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"\s+", "-", s)


def kws(text: str | None) -> list[str]:
    return [x.strip() for x in (text or "").split(",") if x.strip()]


def out_paths(command: str, output_dir: str | None = None):
    base = Path(output_dir) if output_dir else DEFAULT_OUTPUT_BASE
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    d = base / ts
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{command}.md", d / f"{command}.json", d / f"{command}.txt"


def _lines(obj, depth=0):
    pad = "  " * depth
    if isinstance(obj, dict):
        res = []
        for k, v in obj.items():
            title = str(k).replace("_", " ").title()
            if isinstance(v, (dict, list)):
                res.append(f"{pad}- **{title}**")
                res.extend(_lines(v, depth + 1))
            else:
                res.append(f"{pad}- **{title}**: {v}")
        return res
    if isinstance(obj, list):
        res = []
        for v in obj:
            if isinstance(v, (dict, list)):
                res.extend(_lines(v, depth + 1))
            else:
                res.append(f"{pad}- {v}")
        return res
    return [f"{pad}- {obj}"]


def build_markdown(command: str, data: dict) -> str:
    summary = data.get("summary") or f"Generated {command} report."
    next_steps = data.get("next_steps") or ["Review with sales/SEO team", "Mark [verify] fields before publishing"]
    body = "\n".join(_lines({k: v for k, v in data.items() if k not in ["summary", "next_steps"]}))
    ns = "\n".join(f"- {x}" for x in next_steps)
    return f"# {command}\n\n## Summary\n{summary}\n\n## Sections\n{body}\n\n## Next Steps\n{ns}\n"


def write_result(command: str, data: dict, output_dir: str | None = None):
    mdp, jsp, txp = out_paths(command, output_dir)
    md = build_markdown(command, data)
    mdp.write_text(md, encoding="utf-8")
    txp.write_text(md, encoding="utf-8")
    jsp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"FILE:file:///{str(mdp).replace('\\', '/')}")


def _duration_scenes(duration: str):
    d = (duration or "30s").lower().replace(" ", "")
    if d.startswith("15"):
        return [("0-3s", "Hook"), ("3-8s", "Proof"), ("8-12s", "Process"), ("12-15s", "CTA")]
    if d.startswith("20"):
        return [("0-3s", "Hook"), ("3-8s", "Pain"), ("8-14s", "Process"), ("14-18s", "Trust"), ("18-20s", "CTA")]
    return [("0-3s", "Hook"), ("3-8s", "Pain"), ("8-15s", "Capability"), ("15-24s", "Process+QC"), ("24-30s", "CTA")]


def geo_plan(a, p):
    kk = kws(a.keywords)
    generative = {
        "entity_signals": [a.brand or "[brand]", a.product or "[product]", a.industry or "[industry]", a.country or "[country]"],
        "topical_authority_clusters": [
            "supplier qualification",
            "quality documents and testing workflow",
            "customization/private label process",
            "logistics and lead time planning",
        ],
        "buyer_questions": [
            f"How to evaluate {a.product or 'this product'} suppliers?",
            "What documents can be provided where applicable?",
            "What info is required before quotation?",
        ],
        "answer_ready_paragraphs": [
            "Use concise answers with terms like available upon request and depending on order details.",
            "Include process transparency: requirement intake, confirmation, production, QC, shipment.",
        ],
        "comparison_content": ["supplier vs trader", "private label vs ready-made", "sample-first vs bulk-first"],
        "faqpage_suggestions": ["MOQ", "samples", "lead time", "documents", "packaging"],
        "schema_recommendations": ["FAQPage", "Organization", "Product/Service", "BreadcrumbList"],
        "citation_worthy_facts_to_verify": ["capacity", "lead time ranges", "document scope by SKU", "country-specific compliance"],
        "content_hub_plan": ["pillar page", "supporting buyer-guide posts", "FAQ hub", "service workflow page"],
    }
    geographic = {
        "country_localization": [a.country or "target country", f"language: {a.language or 'English'}"],
        "buyer_terminology": ["wholesale", "OEM/ODM", "private label", "bulk supply"],
        "logistics_payment_concerns": ["incoterms [verify]", "destination port/zip", "payment terms depending on order details"],
        "unit_currency_notes": ["metric/imperial by market", "currency display and quote currency"],
        "regional_keyword_variants": kk or [f"{a.product or 'product'} supplier", f"{a.product or 'product'} wholesale"],
        "landing_page_localization_modules": ["market proof points", "shipping note", "payment note", "localized FAQ"],
    }
    out = {"summary": "Combined plan for Generative GEO and Geographic SEO.", "geo_type": a.geo_type}
    if a.geo_type in ["generative", "both"]:
        out["generative_geo"] = generative
    if a.geo_type in ["geographic", "both"]:
        out["geographic_seo"] = geographic
    return out


def blog_brief(a, p):
    topic = a.topic or a.product or "B2B buying guide"
    return {
        "summary": f"B2B SEO blog brief for: {topic}",
        "search_intent": a.intent or "commercial",
        "buyer_persona": ["sourcing manager", "brand owner", "importer"],
        "pain_points": ["supplier reliability", "spec mismatch risk", "lead time uncertainty"],
        "angle": "decision-grade guide with verification checkpoints, not generic listicle",
        "h1_h2_h3_outline": {
            "h1": topic,
            "h2": [
                "How buyers evaluate suppliers",
                "Specification and sampling checklist",
                "MOQ, lead time, packaging and documentation",
                "Common mistakes and risk controls",
            ],
            "h3_examples": ["What to verify before RFQ", "How to compare offers", "Questions to ask sales teams"],
        },
        "faq": ["What MOQ is realistic?", "Can documents be provided?", "How to reduce quality risk?"],
        "internal_links": ["/product-page", "/service-page", "/faq", "/contact"],
        "external_facts_needing_verification": ["regulatory claims", "shipping timelines", "market statistics"],
        "image_suggestions": BRAND_PROFILES[p]["visual"],
        "conversion_cta": "Request a tailored quotation with quantity/spec/destination/packaging details.",
        "schema_suggestions": ["Article", "FAQPage", "BreadcrumbList"],
        "anti_generic_writing_notes": ["Use concrete procurement scenarios", "Avoid fake guarantees", "Mark uncertain data as [verify]"],
    }


def blog_draft(a, p):
    topic = a.topic or a.product or "B2B Supplier Selection Guide"
    return {
        "summary": "Editable B2B SEO blog draft with practical procurement structure.",
        "title": topic,
        "meta_title": f"{topic} | {a.brand}",
        "meta_description": f"A practical B2B guide to evaluate {a.product or a.industry} suppliers with MOQ, QC, documentation, and quotation checkpoints.",
        "h1": topic,
        "introduction": "B2B buyers need repeatable evaluation criteria, not vague promises. This draft outlines how to assess supplier fit, reduce risk, and prepare a quote-ready brief.",
        "h2_sections": [
            {
                "heading": "1) Define business requirements before contacting suppliers",
                "paragraphs": [
                    "Clarify product specs, target quality level, destination market, packaging expectations, and forecast quantity.",
                    "If any critical variable is unknown, mark it as [verify] before requesting final pricing.",
                ],
            },
            {
                "heading": "2) Evaluate supplier process transparency",
                "paragraphs": [
                    "Ask for workflow visibility: requirement intake, sampling, production checkpoints, QC method, shipment handoff.",
                    "Prefer suppliers that state what can be provided where applicable rather than making absolute claims.",
                ],
            },
            {
                "heading": "3) Compare quotations the right way",
                "paragraphs": [
                    "Compare landed cost assumptions, document scope, packaging scope, and lead-time conditions.",
                    "Do not compare only unit price; compare risk exposure and communication responsiveness.",
                ],
            },
        ],
        "faq": ["What info is needed before quotation?", "How can I validate quality documents?", "How do I lower rework risk?"],
        "cta": "Send quantity, specifications, destination, and packaging requirements to get a structured quotation plan.",
        "seo_checklist": ["Primary keyword in H1 and intro", "Intent aligned to commercial research", "FAQ section included", "Internal links added"],
        "places_needing_verification": ["capacity numbers", "exact lead time", "compliance details by SKU"],
    }


def landing_page(a, p):
    product = a.product or a.industry or BRAND_PROFILES[p]["products"][0]
    return {
        "summary": f"B2B landing page structure for {product}.",
        "hero": {"headline": f"{product} for Serious B2B Buyers", "subheadline": "Stable process, clear communication, and scalable fulfillment."},
        "pain_points": ["inconsistent quality", "slow responses", "unclear lead times", "spec misunderstandings"],
        "capabilities": ["bulk supply", "customization/private label", "structured QC checkpoints", "documentation where applicable"],
        "process": ["Requirement intake", "Spec confirmation", "Sample/pre-production", "Production", "QC", "Shipment handoff"],
        "quality_control": ["pre-production confirmation", "in-process checks", "pre-shipment verification"],
        "faq": ["MOQ?", "Sample policy?", "Lead time?", "Documents available?"],
        "cta": "Share quantity, specs, destination, and packaging requirements.",
    }


def product_page(a, p):
    prof = BRAND_PROFILES[p]
    product = a.product or prof["products"][0]
    return {
        "summary": f"B2B product page for {product} targeting {a.country or 'target market'} buyers.",
        "seo_title": f"{product} Supplier | {a.brand}",
        "meta_description": f"{a.brand} supports {product} for B2B buyers with private label/custom options and quality docs available upon request.",
        "slug": slugify(product),
        "hero_headline": f"Reliable {product} Supply for B2B Programs",
        "subheadline": "Built for repeat orders, transparent communication, and quality consistency.",
        "product_overview": f"{a.brand} provides {product} for wholesale and customization workflows depending on order details.",
        "buyer_use_cases": prof["use_cases"],
        "specifications_table": [{"field": "Product", "value": product}, {"field": "Grade/Spec", "value": "[verify]"}, {"field": "Application", "value": a.industry or "B2B use"}],
        "packaging_moq_lead_time_notes": "MOQ, packaging, and lead time depend on quantity, specification, destination, and seasonality.",
        "private_label_or_custom_options": ["OEM/ODM", "private label", "label/artwork adjustment", "packaging customization"],
        "quality_documents_section": prof["docs"],
        "faq": ["What is MOQ?", "Can samples be arranged?", "What documents can you provide where applicable?"],
        "cta": "Request quotation with quantity, specs, destination, and packaging requirements.",
        "image_prompt_suggestions": prof["visual"],
        "internal_link_suggestions": ["/service-page", "/faq", "/about", "/contact"],
    }


def service_page(a, p):
    service = a.product or a.industry or "B2B service"
    return {
        "summary": f"B2B service page for {service}.",
        "service_positioning": f"{a.brand} delivers {service} with milestone-based communication and quality checkpoints.",
        "who_this_service_is_for": ["brand owners", "importers", "procurement managers", "private label teams"],
        "workflow_steps": ["Project intake", "Technical alignment", "Sample/pre-production", "Bulk execution", "QC + dispatch coordination"],
        "what_buyer_needs_to_provide": ["quantity", "spec/material", "branding/custom details", "destination", "timeline"],
        "qc_communication_checkpoints": ["pre-production approval", "in-process updates", "pre-shipment confirmation"],
        "deliverables": ["scope confirmation", "sample/pre-production outcome", "QC summary", "handoff notes"],
        "common_risks_and_how_to_avoid_them": ["spec ambiguity -> use written spec sheet", "timeline mismatch -> define milestones", "branding errors -> approve artwork and placement"],
        "faq": ["How long does sampling take?", "What happens if specs change?", "How are QC issues handled?"],
        "cta": "Share your brief and we will return a step-by-step execution plan.",
    }


def _video_scene_pack(pkey: str, beat: str):
    if pkey == "veytis":
        mapping = {
            "Hook": "Close-up bottle + clean label reveal",
            "Pain": "Buyer concern text over inconsistent supplier visuals",
            "Proof": "Raw material + neat lab bench",
            "Capability": "Filling, capping, labeling workflow",
            "Process": "Procurement checklist overlay",
            "Process+QC": "Batch coding and QC sample check",
            "Trust": "Docs available upon request message",
            "CTA": "Contact panel with RFQ requirements",
        }
    else:
        mapping = {
            "Hook": "Factory floor opening shot",
            "Pain": "Miscommunication/quality risk text",
            "Proof": "Sample room and stitched sample close-up",
            "Capability": "Printing/embroidery/sewing line",
            "Process": "Step cards: sample->bulk->QC",
            "Process+QC": "Inline QC and packing station",
            "Trust": "Team communication board",
            "CTA": "RFQ checklist on screen",
        }
    return mapping.get(beat, "Process shot")


def video_script(a, p):
    scenes = []
    for slot, beat in _duration_scenes(a.duration):
        scenes.append({
            "time": slot,
            "beat": beat,
            "visual_description": _video_scene_pack(p, beat),
            "camera_movement": "slow push-in" if beat in ["Hook", "Proof"] else "handheld documentary",
            "on_screen_text": "" if str(a.no_subtitles).lower() == "true" else f"{beat}: {a.topic or a.product or a.industry}",
            "voiceover": f"{beat}: {a.brand} supports B2B buyers with clear process and realistic expectations.",
        })
    return {
        "summary": f"{a.duration} video script for {a.platform} using {p} visual rules.",
        "total_duration": a.duration,
        "scene_by_scene_timeline": scenes,
        "b_roll_suggestions": BRAND_PROFILES[p]["video"],
        "asset_requirements": [x for x in (a.assets or "").split(",") if x.strip()] or ["logo", "product/factory clips", "contact end card"],
        "negative_prompt": "no fake machinery, no exaggerated claims, no unrealistic luxury staging",
        "platform_adaptation": {"TikTok": "fast hook + bold text", "Reels": "clean caption rhythm", "Shorts": "quick scene transitions"},
    }


def image_prompt(a, p):
    base = BRAND_PROFILES[p]["visual"]
    main = f"{a.scene}, {a.product or ''}, {a.style}, {', '.join(base)}, ratio {a.ratio}, commercial product realism"
    return {
        "summary": "Brand-aligned image prompt package.",
        "main_prompt_english": main.strip(),
        "negative_prompt": "yellow cast, red cast, orange cast, fake AI machinery, over-saturated colors, unreal proportions",
        "local_edit_prompt": "keep composition; refine label readability, white balance to cool neutral, maintain realistic material texture",
        "realism_checklist": ["accurate proportions", "natural shadows", "legible packaging/garment details", "physically plausible workstation/tools"],
        "composition_notes": ["clear foreground subject", "clean background", "space for text overlay"],
        "brand_consistency_notes": base,
    }


def inquiry_reply(a, p):
    msg = (a.customer_message or "")
    lower = msg.lower()
    qty = re.search(r"\b(\d{2,7})\b", lower)
    product = "custom hoodies" if "hoodie" in lower else ("t-shirts" if "t-shirt" in lower else (a.product or "[verify]"))
    custom = [t for t in ["puff print", "screen print", "embroidery", "heat transfer", "private label"] if t in lower] or ["[verify]"]
    mat = re.findall(r"\b(cotton|polyester|fleece|spandex|gsm\s*\d+)\b", lower) or ["[verify]"]
    destination = re.search(r"(?:ship to|to)\s+([a-zA-Z\s]{2,40})", lower)
    packaging = "custom packaging" if "pack" in lower else "[verify]"
    deadline = re.search(r"(?:by|before)\s+([a-zA-Z0-9\-/ ]{2,25})", lower)
    docs = [t for t in ["coa", "msds", "ifra", "sgs", "certificate"] if t in lower] or ["none mentioned"]
    return {
        "summary": "Inquiry analysis + conversion-safe reply.",
        "detected_quantity": qty.group(1) if qty else "[verify]",
        "detected_product": product,
        "detected_customization": custom,
        "detected_material_or_spec": mat,
        "detected_destination": destination.group(1).strip() if destination else "[verify]",
        "detected_packaging": packaging,
        "detected_deadline": deadline.group(1).strip() if deadline else "[verify]",
        "detected_document_request": docs,
        "missing_info": ["exact specs/material", "destination", "packaging detail", "required delivery window"],
        "reply_en": "Thanks for your inquiry. Yes, we can review a 500 pcs custom hoodie project with puff print. Could you share quantity, specifications, destination, and packaging requirements? We will then provide a quotation and suggested sampling workflow.",
        "whatsapp_short": "Thanks! We can review 500 custom hoodies with puff print. Please share specs, destination, and packaging for quote.",
        "follow_up_questions": ["Preferred fabric and GSM?", "Logo size/placement and color count?", "Destination country/zip and target delivery date?"],
        "next_step": "Collect missing details -> technical feasibility check -> quote + sample plan.",
    }


def faq(a, p):
    return {"summary": "B2B FAQ set", "items": ["MOQ?", "Sample policy?", "Lead time?", "Documents available where applicable?"]}


def content_calendar(a, p):
    channels = ["Google SEO blog", "LinkedIn", "TikTok/Reels/Shorts", "Email", "Website page update"]
    rows = []
    for day in range(1, 31):
        ch = channels[(day - 1) % len(channels)]
        rows.append({
            "day": day,
            "channel": ch,
            "content_type": "guide" if "blog" in ch.lower() else "post",
            "topic": f"Day {day} - {(a.product or a.industry or 'B2B topic')}",
            "keyword": (kws(a.keywords)[0] if kws(a.keywords) else (a.product or "b2b supplier")),
            "hook": "Solve one buyer risk in one clear takeaway",
            "visual_idea": BRAND_PROFILES[p]["visual"][0],
            "cta": "Request quotation with specs + destination",
            "funnel_stage": ["TOFU", "MOFU", "BOFU"][day % 3],
            "reuse_idea": "Repurpose to short video + LinkedIn carousel + email snippet",
        })
    return {"summary": "30-day cross-channel B2B content calendar.", "calendar": rows}


def seo_meta(a, p):
    seed = a.product or a.topic or a.industry or "b2b-page"
    return {"summary": "SEO metadata", "title": f"{seed} | {a.brand}", "meta_description": f"{a.brand} supports {seed} for B2B buyers. Contact us with your requirement details.", "slug": slugify(seed)}


def prompt_pack(a, p):
    if not getattr(a, "intent", None):
        a.intent = "commercial"
    if not getattr(a, "platform", None):
        a.platform = "TikTok"
    if not getattr(a, "duration", None):
        a.duration = "30s"
    if not getattr(a, "style", None):
        a.style = "realistic"
    if not getattr(a, "no_subtitles", None):
        a.no_subtitles = "false"
    if not hasattr(a, "assets") or a.assets is None:
        a.assets = ""
    if not getattr(a, "scene", None):
        a.scene = "product photo"
    if not getattr(a, "ratio", None):
        a.ratio = "1:1"
    return {
        "summary": "Combined asset pack.",
        "blog_brief": blog_brief(a, p),
        "blog_draft": blog_draft(a, p),
        "landing_page": landing_page(a, p),
        "video_script": video_script(a, p),
        "image_prompt": image_prompt(a, p),
        "faq": faq(a, p),
        "content_calendar_preview": content_calendar(a, p)["calendar"][:3],
        "seo_meta": seo_meta(a, p),
    }


def negative_keywords(a, p):
    base_exclude = ["free", "cheap", "template", "pattern", "used", "second hand", "job", "jobs", "salary", "course", "training"]
    return {
        "summary": "Google Ads negative keyword framework with risk tiers.",
        "must_exclude": base_exclude + ["near me", "dropshipping", "blank", "ready made"],
        "review_before_excluding": ["dubai", "uae", "wholesale clothes", "manufacturer", "oem", "private label", "bulk custom"],
        "keep_or_monitor": ["custom clothing manufacturer", "custom hoodies bulk", "private label apparel"],
        "b2c_low_intent": ["one piece", "for myself", "small order"],
        "jobs_education": ["job", "hiring", "internship", "course", "how to sew"],
        "free_diy_template": ["free design", "diy", "template", "pattern pdf"],
        "ready_made_or_retail_risk": ["ready made", "retail", "fashion store", "mall"],
        "competitor_or_marketplace_risk": ["amazon", "alibaba", "temu", "shein"],
        "notes_by_country": {a.country or "default": "Review local language variants before hard exclusions."},
        "warning": "do not blindly exclude converted search terms",
    }


def ad_keyword_plan(a, p):
    product = a.product or a.industry or "product"
    return {
        "summary": f"Account structure plan for {product}.",
        "campaign_goal": "qualified B2B leads",
        "recommended_match_types": ["exact", "phrase", "cautious broad"],
        "ad_groups": ["supplier intent", "manufacturer intent", "customization intent", "wholesale intent"],
        "exact_keywords": [f"[{product} manufacturer]", f"[{product} supplier]", f"[custom {product}]"],
        "phrase_keywords": [f'"{product} manufacturer"', f'"{product} supplier"', '"private label"'],
        "cautious_broad_keywords": [f"{product} bulk", f"{product} oem"],
        "landing_page_mapping": {"supplier intent": "/product-page", "customization intent": "/service-page", "wholesale intent": "/contact"},
        "ad_copy_angles": ["process visibility", "QC checkpoints", "customization support"],
        "conversion_tracking_notes": ["Track form submit", "Track WhatsApp click", "Track qualified lead stage"],
        "budget_and_bid_notes": ["Prioritize exact/phrase initially", "Use broad only with weekly search-term controls"],
        "search_term_review_rules": ["Promote converters to exact", "Exclude repeated low-intent", "Review regional wholesale terms before excluding"],
    }


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
    "product-page": product_page,
    "service-page": service_page,
    "ad-keyword-plan": ad_keyword_plan,
    "negative-keywords": negative_keywords,
    "seo-meta": seo_meta,
}


def add_common(s):
    for n in ["brand", "industry", "country", "language", "product", "audience", "keywords", "tone", "market", "funnel_stage"]:
        s.add_argument(f"--{n.replace('_', '-')}", dest=n)
    s.add_argument("--brand-profile", choices=["auto", "veytis", "juese", "generic"], default="auto")
    s.add_argument("--output-dir")


def parser():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="command", required=True)
    for c in CMDS:
        s = sp.add_parser(c)
        add_common(s)
        if c in ["blog-brief", "blog-draft", "video-script", "prompt-pack", "seo-meta", "ad-keyword-plan"]:
            s.add_argument("--topic")
        if c in ["blog-brief", "blog-draft", "prompt-pack"]:
            s.add_argument("--intent", default="commercial")
        if c == "geo-plan":
            s.add_argument("--geo-type", choices=["generative", "geographic", "both"], default="both")
        if c in ["video-script", "prompt-pack"]:
            s.add_argument("--platform", default="TikTok")
            s.add_argument("--duration", default="30s")
            s.add_argument("--style", default="realistic")
            s.add_argument("--no-subtitles", dest="no_subtitles", default="false")
            s.add_argument("--assets", default="")
        if c in ["image-prompt", "prompt-pack"]:
            s.add_argument("--scene", default="product photo")
            s.add_argument("--ratio", default="1:1")
            if c == "image-prompt":
                s.add_argument("--style", default="realistic")
        if c == "inquiry-reply":
            s.add_argument("--customer-message", required=True)
    return p


def main():
    args = parser().parse_args()
    pkey = profile_key(args.brand, args.brand_profile)
    result = CMDS[args.command](args, pkey)
    write_result(args.command, result, args.output_dir)


if __name__ == "__main__":
    main()
