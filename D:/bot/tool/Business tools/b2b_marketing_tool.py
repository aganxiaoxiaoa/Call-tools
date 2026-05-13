#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, re
from pathlib import Path

DEFAULT_OUTPUT_BASE = Path(r"D:\bot\outputs\business_tools")

BRAND_PROFILES = {
    "veytis": {
        "products": ["essential oils", "hydrosols", "fragrance oils", "carrier oils"],
        "use_cases": ["private label oil line", "spa and wellness bulk sourcing", "aromatherapy retail chain supply"],
        "docs": ["COA available upon request", "MSDS available upon request", "IFRA/SGS where applicable"],
        "visual": ["neutral cool background", "no yellow/red/orange cast", "clean premium B2B style"],
    },
    "juese": {
        "products": ["custom hoodies", "custom t-shirts", "sportswear", "apparel OEM"],
        "use_cases": ["streetwear brand launch", "ecommerce merch line", "teamwear bulk production"],
        "docs": ["QC report process overview", "material confirmations upon request"],
        "visual": ["documentary factory realism", "real workstation", "no fake AI machinery"],
    },
    "generic": {"products": ["B2B product"], "use_cases": ["bulk sourcing"], "docs": ["documents upon request"], "visual": ["clean B2B"]},
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

def kws(s: str | None):
    return [x.strip() for x in (s or "").split(",") if x.strip()]

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

# --- Generators ---
def product_page(a, p):
    prof = BRAND_PROFILES[p]
    product = a.product or (prof["products"][0])
    return {
        "summary": f"B2B product page for {product} targeting {a.country or 'target market'} buyers.",
        "seo_title": f"{product} Supplier | {a.brand}",
        "meta_description": f"{a.brand} provides {product} for B2B buyers with private label/custom options and quality docs available upon request.",
        "slug": slugify(product),
        "hero_headline": f"Reliable {product} Supply for B2B Buyers",
        "subheadline": "Built for stable quality, clear communication, and scalable orders.",
        "product_overview": f"{a.brand} supports wholesale/custom programs for {product}. Terms depend on order details.",
        "buyer_use_cases": prof["use_cases"],
        "specifications_table": [
            {"field": "Product", "value": product},
            {"field": "Grade/Spec", "value": "[verify]"},
            {"field": "Application", "value": a.industry or "B2B manufacturing/use"},
        ],
        "packaging_moq_lead_time_notes": "MOQ, packaging, and lead time depend on quantity/spec/destination.",
        "private_label_or_custom_options": ["OEM/ODM", "private label", "custom packaging/branding"],
        "quality_documents": prof["docs"],
        "faq": ["MOQ for first order?", "Can you provide samples?", "What quality documents are available?"],
        "cta": "Share quantity, specs, destination, and packaging requirements for quotation.",
        "image_prompt_suggestions": prof["visual"],
        "internal_link_suggestions": ["/services", "/faq", "/contact", "/about"],
    }

def service_page(a, p):
    return {
        "summary": f"Service page for {a.product or a.industry}.",
        "service_positioning": f"{a.brand} provides B2B {a.product or 'service'} with process visibility and risk control.",
        "who_this_service_is_for": ["Brand owners", "Importers/wholesale buyers", "Procurement teams"],
        "workflow_steps": ["Requirement intake", "Specification confirmation", "Sampling/prep", "Production/fulfillment", "QC + shipment handoff"],
        "what_buyer_needs_to_provide": ["Quantity", "Specs/material", "Destination", "Packaging requirements", "Target timeline"],
        "qc_communication_checkpoints": ["Pre-production confirmation", "In-process update", "Pre-shipment check"],
        "deliverables": ["Sample or pre-production result", "Production output", "QC summary", "Shipment coordination notes"],
        "common_risks_and_how_to_avoid_them": [
            "Unclear specs -> use structured spec sheet",
            "Timeline mismatch -> align milestones early",
            "Packaging errors -> approve packaging details before production",
        ],
        "faq": ["What is typical MOQ?", "How long does sampling take?", "How are issues handled?"],
        "cta": "Send your project brief and we will map scope, timeline, and next step.",
    }

def negative_keywords(a, p):
    base_exclude = ["free", "cheap", "template", "pattern", "used", "second hand", "job", "jobs", "salary", "course", "training"]
    return {
        "summary": "Google Ads negative keyword framework with risk tiers.",
        "must_exclude": base_exclude + ["near me", "dropshipping", "blank hoodies", "ready made"],
        "review_before_excluding": ["dubai", "uae", "wholesale clothes", "manufacturer", "oem", "private label", "bulk custom"],
        "keep_or_monitor": ["custom clothing manufacturer", "custom hoodies bulk", "private label apparel"],
        "b2c_low_intent": ["one piece", "personal use", "small order"],
        "jobs_education": ["job", "hiring", "internship", "course", "how to sew"],
        "free_diy_template": ["free design", "diy", "template", "pattern pdf"],
        "ready_made_or_retail_risk": ["ready made", "retail", "mall", "fashion store"],
        "competitor_or_marketplace_risk": ["amazon", "alibaba", "temu", "shein"],
        "notes_by_country": {a.country or "default": "Review language variants and local slang before hard negatives."},
        "warning": "do not blindly exclude converted search terms",
    }

def ad_keyword_plan(a, p):
    product = a.product or a.industry or "product"
    return {
        "summary": f"Account structure plan for {product}.",
        "campaign_goal": "qualified B2B leads",
        "recommended_match_types": ["exact", "phrase", "limited broad"],
        "ad_groups": ["supplier intent", "manufacturer intent", "customization intent", "wholesale intent"],
        "exact_keywords": [f"[{product} manufacturer]", f"[{product} supplier]", f"[custom {product}]"],
        "phrase_keywords": [f'"{product} manufacturer"', f'"{product} supplier"', '"private label"'],
        "cautious_broad_keywords": [f"{product} bulk", f"{product} oem"],
        "landing_page_mapping": {"supplier intent": "/product-page", "customization intent": "/service-page", "wholesale intent": "/contact"},
        "ad_copy_angles": ["process reliability", "QC & communication", "private label/custom options"],
        "conversion_tracking_notes": ["Track form submit", "Track WhatsApp click", "Track qualified lead stage"],
        "budget_and_bid_notes": ["Start with exact/phrase majority budget", "Use cautious broad with strict search-term review"],
        "search_term_review_rules": ["Promote converters to exact", "Exclude repeated low-intent terms", "Keep regional wholesale terms under review"],
    }

def inquiry_reply(a, p):
    msg = (a.customer_message or "").lower()
    qty = re.search(r"\b(\d{2,6})\b", msg)
    detected_product = "custom hoodies" if "hoodie" in msg else (a.product or "[verify]")
    detected_customization = []
    for term in ["puff print", "screen print", "embroidery", "heat transfer"]:
        if term in msg:
            detected_customization.append(term)
    material = re.findall(r"\b(cotton|polyester|fleece|gsm\s*\d+)\b", msg)
    destination = re.search(r"\b(to|ship to)\s+([a-zA-Z\s]+)", msg)
    deadline = re.search(r"\b(by|before)\s+([a-zA-Z0-9\-/ ]{3,20})", msg)
    doc_req = [x for x in ["coa", "msds", "ifra", "sgs", "certificate"] if x in msg]
    packaging = "custom packaging" if "pack" in msg else "[verify]"
    return {
        "summary": "Inquiry parsing + safe B2B reply draft.",
        "detected_quantity": qty.group(1) if qty else "[verify]",
        "detected_product": detected_product,
        "detected_customization": detected_customization or ["[verify]"],
        "detected_material_or_spec": material or ["[verify]"],
        "detected_destination": destination.group(2).strip() if destination else "[verify]",
        "detected_packaging": packaging,
        "detected_deadline": deadline.group(2).strip() if deadline else "[verify]",
        "detected_document_request": doc_req or ["none mentioned"],
        "missing_info": ["spec details", "destination", "packaging", "target lead time"],
        "reply_en": "Thanks for your message. Yes, we can review this request. Could you share quantity, specifications, destination, and packaging requirements? Then we can provide an accurate quotation and sampling plan.",
        "whatsapp_short": "Thanks! Please share qty, specs, destination, and packaging needs for quote.",
        "follow_up_questions": ["Preferred fabric/material and GSM?", "Logo method and size?", "Target delivery window?"],
        "next_step": "Collect missing info -> evaluate feasibility -> send quotation.",
    }

def geo_plan(a, p): return {"summary":"GEO/SEO plan","brand":a.brand,"geo_type":a.geo_type}
def blog_brief(a, p): return {"summary":"Blog brief","topic":a.topic,"intent":a.intent}
def blog_draft(a, p): return {"summary":"Blog draft","title":a.topic,"sections":["Intro","H2-1","H2-2","FAQ"]}
def landing_page(a, p): return {"summary":"Landing page","headline":f"{a.brand} {a.product or a.industry}"}
def video_script(a, p): return {"summary":"Video script","platform":a.platform,"duration":a.duration,"style":a.style}
def image_prompt(a, p): return {"summary":"Image prompt","scene":a.scene,"ratio":a.ratio,"style":a.style}
def faq(a, p): return {"summary":"FAQ","items":["MOQ?","Lead time?","Samples?"]}
def content_calendar(a, p): return {"summary":"30-day calendar","days":30}
def seo_meta(a, p): return {"summary":"SEO metadata","title":f"{a.product or a.topic or a.industry} | {a.brand}","slug":slugify(a.product or a.topic or a.industry)}
def prompt_pack(a, p):
    return {
        "summary": "Combined asset pack.",
        "blog_brief": blog_brief(a, p),
        "blog_draft": blog_draft(a, p),
        "landing_page_sections": landing_page(a, p),
        "video_script": video_script(a, p),
        "image_prompt": image_prompt(a, p),
        "faq": faq(a, p),
        "seo_meta": seo_meta(a, p),
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

def parser():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="command", required=True)
    def add_common(s):
        for n in ["brand","industry","country","language","product","audience","keywords","tone","market","funnel_stage"]:
            s.add_argument(f"--{n.replace('_','-')}", dest=n)
        s.add_argument("--brand-profile", choices=["auto","veytis","juese","generic"], default="auto")
        s.add_argument("--output-dir")
    for c in CMDS:
        s = sp.add_parser(c)
        add_common(s)
        if c in ["blog-brief","blog-draft","video-script","prompt-pack","seo-meta","ad-keyword-plan"]:
            s.add_argument("--topic")
        if c in ["blog-brief","blog-draft","prompt-pack"]:
            s.add_argument("--intent", default="commercial")
        if c == "geo-plan":
            s.add_argument("--geo-type", choices=["generative","geographic","both"], default="both")
        if c in ["video-script","prompt-pack"]:
            s.add_argument("--platform", default="TikTok")
            s.add_argument("--duration", default="30s")
            s.add_argument("--style", default="realistic")
            s.add_argument("--no-subtitles", dest="no_subtitles", default="false")
            s.add_argument("--assets", default="")
        if c in ["image-prompt","prompt-pack"]:
            s.add_argument("--scene", default="product photo")
            s.add_argument("--ratio", default="1:1")
            if c == "image-prompt":
                s.add_argument("--style", default="realistic")
        if c == "inquiry-reply":
            s.add_argument("--customer-message", required=True)
    return p

def main():
    a = parser().parse_args()
    pkey = profile_key(a.brand, a.brand_profile)
    result = CMDS[a.command](a, pkey)
    write_result(a.command, result, a.output_dir)

if __name__ == "__main__":
    main()
