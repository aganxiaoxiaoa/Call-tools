#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, re
from pathlib import Path

DEFAULT_OUTPUT_BASE = Path(r"D:\bot\outputs\business_tools")

BRAND_PROFILES = {
"veytis": {
"industries":["essential oils wholesale","hydrosol supplier","private label aromatherapy"],
"products":["essential oils","hydrosols","fragrance oils","carrier oils"],
"target_customers":["importers","brand owners","distributors"],
"value_props":["bulk supply","private label","OEM/ODM support"],
"trust_elements":["COA/MSDS/IFRA/SGS can provide where applicable","batch consistency workflow [verify]"],
"visual_rules":["neutral white/cool ivory/pale stone/cool greige","no yellow/red/orange cast"],
"copy_rules":["premium natural B2B tone","use available upon request for uncertain docs"],
"avoid_claims":["guaranteed lowest price","fake certifications","fixed lead time without details"],
"common_cta":["Request bulk quote","Ask private label options"],
"common_faq":["MOQ?","Documents available?","Lead time depending on order details?"]},
"juese": {
"industries":["custom garment factory","apparel OEM/ODM"],
"services":["sampling","screen printing","embroidery","QC","packing"],
"target_customers":["streetwear brands","ecommerce labels","wholesale buyers"],
"production_process":["tech pack review","sample","bulk production","QC","packing/shipping"],
"trust_elements":["sample room workflow","QC checkpoints","communication cadence"],
"visual_rules":["documentary realism","clean factory","no fake luxury showroom","no AI machinery"],
"copy_rules":["process-first B2B tone","avoid exaggerated promises"],
"avoid_claims":["100% defect free","instant production"],
"common_cta":["Send tech pack","Request sampling plan"],
"common_faq":["Sample time?","MOQ for custom hoodies?","Printing vs embroidery options?"]},
"generic": {"common_cta":["Request quote"],"common_faq":["MOQ?","Lead time?","Payment terms?"]}
}

def detect_profile(brand, profile):
    if profile != "auto": return profile
    b = (brand or "").lower()
    if "veytis" in b: return "veytis"
    if "juese" in b: return "juese"
    return "generic"

def kws(s): return [x.strip() for x in (s or "").split(",") if x.strip()]

def build_out(command, outdir=None):
    base = Path(outdir) if outdir else DEFAULT_OUTPUT_BASE
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    d = base / ts
    d.mkdir(parents=True, exist_ok=True)
    return d, d / f"{command}.md", d / f"{command}.json", d / f"{command}.txt"

def write_result(command, data, fmt, outdir=None):
    d, mdp, jsp, txp = build_out(command, outdir)
    md = "# " + command + "\n\n```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```\n"
    if fmt in ("markdown","both"): mdp.write_text(md, encoding="utf-8"); txp.write_text(md, encoding="utf-8")
    else: mdp.write_text(md, encoding="utf-8"); txp.write_text(md, encoding="utf-8")
    jsp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    posix = str(mdp).replace("\\","/")
    print(f"FILE:file:///{posix}")

def geo_plan(a,p):
    kw = kws(a.keywords)
    return {"brand":a.brand,"profile":p,"geo_type":a.geo_type,
"generative_engine_optimization":{
"entity_signals":[a.brand,a.industry,a.product,"B2B wholesale","OEM/ODM"],
"topical_authority_clusters":["supplier qualification","MOQ and pricing framework","quality documents workflow"],
"buyer_questions":[f"Who is a reliable {a.product} supplier?","Can private label be supported?","What documents are available upon request?"],
"answer_ready_paragraphs":[f"{a.brand} supports {a.product} for {a.audience} with customization depending on order details.","Documentation can be provided where applicable; details require [verify]."],
"comparison_content":["private label vs white label","spot buy vs contract supply"],
"faqpage_suggestions":["MOQ","Lead time","Documents","Packaging"],
"schema_recommendations":["Organization","Product","FAQPage","HowTo"],
"citation_worthy_facts_to_verify":["regional import rules [verify]","shelf life by product [verify]"],
"content_hub_plan":["pillar page + 6 cluster blogs + FAQ page"]},
"geographic_seo":{
"country_localization":[a.country,a.language],"buyer_terminology":["bulk","wholesale","private label","custom manufacturing"],
"logistics_payment_concerns":["incoterms [verify]","payment methods available upon request"],
"unit_currency_notes":["unit system [verify]","currency display by market"],
"regional_keyword_variants":kw,
"landing_page_localization_modules":["regional trust notes","shipping/payment block","localized CTA"]}}

def blog_brief(a,p):
    kw=kws(a.keywords)
    return {"search_intent":a.intent,"buyer_persona":a.audience or "B2B procurement manager","pain_points":["supplier stability","quality consistency","lead time risk"],"angle":"risk-controlled sourcing","outline":{"H1":a.topic,"H2":["How buyers evaluate suppliers","MOQ/lead time/payment framework","Quality documents and compliance"],"H3":["Checklist","Common mistakes"]},"faq":BRAND_PROFILES[p].get("common_faq",[]),"internal_links":["/about","/services","/contact"],"external_facts_needing_verification":["market size [verify]","regulatory requirement [verify]"],"image_suggestions":["process photo","QC checkpoint","packaging line"],"conversion_cta":BRAND_PROFILES[p].get("common_cta",["Request quote"]),"schema_suggestions":["Article","FAQPage"],"anti_generic_notes":["include order scenario","avoid empty adjectives"],"keywords":kw}

def blog_draft(a,p):
    b=blog_brief(a,p)
    return {"title":a.topic,"meta_title":f"{a.topic} | {a.brand}","meta_description":f"A practical B2B guide for {a.country} buyers evaluating {a.product or a.industry} suppliers.","h1":a.topic,"introduction":f"Choosing a {a.product or a.industry} supplier is a risk decision, not only a price decision. This draft gives a practical framework for {a.audience or 'B2B buyers'}.","h2_sections":[{"h2":"1) Define specification and order scope","content":"List required specs, target quantity, destination, and packaging before requesting quotation."},{"h2":"2) Evaluate supplier capability","content":"Review sampling process, QC checkpoints, communication rhythm, and document availability upon request."},{"h2":"3) Compare commercial terms","content":"Compare MOQ, payment terms, lead time depending on order details, and after-sales handling."}],"faq":b["faq"],"cta":"Share your quantity, specification, destination, and packaging requirements for a tailored quote.","seo_checklist":["keyword in title/H1/intro","add internal links","FAQ schema"],"places_needing_verification":["lead time benchmark [verify]","compliance requirement [verify]"]}

def landing_page(a,p):
    return {"hero_headline":f"{a.brand}: {a.product or a.industry} for serious B2B buyers","subheadline":"Built for reliable wholesale and customization workflows.","trust_bar":BRAND_PROFILES[p].get("trust_elements",[]),"buyer_pain_points":["inconsistent quality","unclear lead time","slow communication"],"capability_section":BRAND_PROFILES[p].get("services",BRAND_PROFILES[p].get("products",[])),"customization_section":["OEM/ODM","private label","spec-based production"],"quality_control_section":["incoming checks","in-process QC","pre-shipment check"],"process_section":BRAND_PROFILES[p].get("production_process",["requirement","sample","production","QC","shipping"]),"moq_leadtime_sample_section":"MOQ, sample policy, and lead time depending on order details.","faq":BRAND_PROFILES[p].get("common_faq",[]),"cta":BRAND_PROFILES[p].get("common_cta",[]),"seo_title":f"{a.product or a.industry} Supplier | {a.brand}","meta_description":"B2B-focused supply and customization support. Documents can be provided where applicable.","schema":["Organization","Service","FAQPage"],"image_prompt_suggestions":BRAND_PROFILES[p].get("visual_rules",[])}

def video_script(a,p):
    dur=a.duration
    return {"total_duration":dur,"platform":a.platform,"no_subtitles":a.no_subtitles,"style":a.style,
"scene_timeline":[{"time":"0-3s","visual":"problem hook in real workflow","camera":"handheld push-in","text":"Need reliable B2B production?","voiceover":"If delays and quality issues hurt your margin, watch this."},{"time":"4-12s","visual":"process step 1-2","camera":"medium tracking","text":"Sampling + QC checkpoints","voiceover":"We align specs, sample first, then run controlled production."},{"time":"13-24s","visual":"printing/embroidery or filling/packaging","camera":"close-up cut sequence","text":"Real production workflow","voiceover":"Every batch follows documented checks; details available upon request."},{"time":"25-30s","visual":"packing + dispatch","camera":"static wide","text":"Send your requirements","voiceover":"Share quantity, specs, destination, and packaging for a tailored quote."}],"b_roll_suggestions":["QC tags","packing line","team communication"],"asset_requirements":kws(a.assets),"negative_prompt":"no fake luxury showroom, no dirty factory, no impossible machinery, no color cast","platform_adaptation":{"TikTok":"fast cuts + bold hook","LinkedIn":"slower explanatory cut"}}

def image_prompt(a,p):
    if p=="veytis":
        main="Premium essential oil product photography, amber dropper bottle with clear label hierarchy, neutral cool background, clean B2B wholesale aesthetic, accurate bottle proportion, soft industrial daylight, no warm cast"
        neg="yellow cast, red cast, orange cast, oversaturated, fake luxury props, unrealistic glass distortions"
    elif p=="juese":
        main="Documentary-style garment factory scene, real sewing workstation, logical machine layout, clean industrial lighting, sampling and QC workflow visible, authentic B2B production"
        neg="fake AI machinery, staged luxury showroom, dark dirty factory, impossible hand positions"
    else:
        main=f"{a.scene}, {a.product}, {a.style}, realistic commercial B2B"
        neg="low quality, blurry, fake details"
    return {"main_prompt_english":main,"negative_prompt":neg,"local_edit_prompt":"Keep brand tone and workflow realism; adjust only composition and lighting.","realism_checklist":["industry-correct objects","logical workflow","clean lighting","no fake claims visuals"],"composition_notes":["hero object clear","left/right space for copy"],"brand_consistency_notes":BRAND_PROFILES[p].get("visual_rules",[])}

def inquiry_reply(a,p):
    msg=a.customer_message.lower()
    qty = re.search(r"\b(\d{2,6})\b", msg)
    product = "hoodies" if "hoodie" in msg else (a.product if hasattr(a,'product') else "product [verify]")
    intents=[x for x in ["price" if "price" in msg else "","moq" if "moq" in msg else "","sample" if "sample" in msg else "","lead time" if "lead" in msg else "","customization" if any(k in msg for k in ["custom","print","embroidery","puff"]) else "","packaging" if "pack" in msg else "","certification" if any(k in msg for k in ["cert","coa","msds","ifra","sgs"]) else ""] if x]
    missing=["specifications","destination","packaging requirements"]
    return {"customer_intent":intents or ["general inquiry"],"detected_product":product,"detected_quantity":qty.group(1) if qty else "[verify]","missing_info":missing,"risk_notes":["Do not quote price before specs/qty/destination","Lead time depending on order details"],"reply_en":"Thanks for your message. Yes, we can review this custom request. Could you share quantity, specifications, destination, and packaging requirements? Once we have these details, we can provide an accurate quotation and sample plan.","whatsapp_short":"Thanks! Could you share quantity, specs, destination, and packaging requirements?","follow_up_questions":["Any fabric/GSM/color requirements?","Logo method (print/embroidery/puff)?","Target delivery window?"],"quotation_info_needed":["tech specs","quantity","destination","packaging","target incoterm [verify]"],"next_step":"Collect missing info -> evaluate feasibility -> send quotation draft."}

def faq(a,p):
    groups=["MOQ","Samples","Customization","Private label / OEM","Lead time","Packaging","Quality documents","Shipping","Payment","After-sales"]
    items=[]
    for g in groups:
        for i in range(2 if p=="generic" else 3):
            items.append({"group":g,"q":f"{g} question {i+1} for {a.brand}?","a":"Answer depends on product specs and order details; documents available upon request where applicable."})
    return {"count":len(items),"faq":items[:30]}

def content_calendar(a,p):
    ch=["Google SEO blog","LinkedIn","TikTok/Reels/Shorts","Pinterest","Email","Website page update"]
    cal=[]
    for d in range(1,31):
        c=ch[(d-1)%len(ch)]
        cal.append({"day":d,"channel":c,"content_type":"blog" if "blog" in c.lower() else "post/video/update","topic":f"{a.brand} {a.industry} topic {d}","keyword":f"{a.industry} keyword {d}","hook":"Start from buyer pain point.","visual_idea":"real process image/video","cta":"Request quote","funnel_stage":a.funnel_stage or "MOFU","reuse_idea":"repurpose to LinkedIn + email"})
    return {"calendar":cal}

def seo_meta(a,p): return {"title":f"{a.product or a.topic or a.industry} | {a.brand}","meta_description":"B2B-focused sourcing and customization support. Details available upon request.","slug":(a.product or a.topic or a.industry).lower().replace(' ','-')}

def ad_keyword_plan(a,p):
    base=a.product or a.industry
    return {"exact_match_keywords":[f"[{base} supplier]",f"[{base} manufacturer]"],"phrase_match_keywords":[f'"{base} wholesale"',f'"private label {base}"'],"broad_match_cautious_keywords":[f"{base} bulk",f"{base} oem"],"ad_group_structure":{"supplier_intent":["supplier","manufacturer"],"customization_intent":["OEM","private label"]},"landing_page_mapping":{"supplier_intent":"/supplier-page","customization_intent":"/service-page"},"buyer_intent_score":78,"risk_score":32}

def negative_keywords(a,p):
    common=["free","cheap","retail","ready made","jobs","pattern","second hand","used"]
    extra=["DIY","personal use"] if p=="veytis" else ["ready stock retail hoodies","dropshipping"]
    return {"negative_keywords":common+extra,"notes":"Exclude low-intent B2C and non-wholesale traffic."}

def product_page(a,p): return landing_page(a,p)
def service_page(a,p): return landing_page(a,p)
def prompt_pack(a,p): return {"blog_brief":blog_brief(a,p),"blog_draft":blog_draft(a,p),"landing_page_sections":landing_page(a,p),"video_script":video_script(a,p),"image_prompt":image_prompt(a,p),"faq":faq(a,p),"social_post_ideas":["pain point post","case workflow post"],"email_whatsapp_follow_up":["email follow-up template","whatsapp short"],"seo_meta":seo_meta(a,p)}

CMDS={"geo-plan":geo_plan,"blog-brief":blog_brief,"blog-draft":blog_draft,"landing-page":landing_page,"video-script":video_script,"image-prompt":image_prompt,"inquiry-reply":inquiry_reply,"faq":faq,"content-calendar":content_calendar,"prompt-pack":prompt_pack,"product-page":product_page,"service-page":service_page,"ad-keyword-plan":ad_keyword_plan,"negative-keywords":negative_keywords,"seo-meta":seo_meta}

def parser():
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest="command",required=True)
    def add_common(s):
        for n in ["brand","industry","country","language","product","audience","keywords","tone","market","funnel_stage"]: s.add_argument(f"--{n.replace('_','-')}",dest=n)
        s.add_argument("--brand-profile",choices=["auto","veytis","juese","generic"],default="auto")
        s.add_argument("--output-dir"); s.add_argument("--format",choices=["markdown","json","both"],default="both")
    for c in CMDS:
        s=sp.add_parser(c); add_common(s)
        if c in ["blog-brief","blog-draft","video-script","prompt-pack","seo-meta"]: s.add_argument("--topic")
        if c in ["blog-brief","blog-draft","prompt-pack"]: s.add_argument("--intent",default="commercial")
        if c=="geo-plan": s.add_argument("--geo-type",choices=["generative","geographic","both"],default="both")
        if c=="video-script": s.add_argument("--platform",default="TikTok"); s.add_argument("--duration",default="30s"); s.add_argument("--style",default="realistic"); s.add_argument("--no-subtitles",default="false"); s.add_argument("--assets",default="")
        if c=="image-prompt": s.add_argument("--scene",default="product photo"); s.add_argument("--style",default="realistic"); s.add_argument("--ratio",default="1:1")
        if c=="prompt-pack": s.add_argument("--platform",default="TikTok"); s.add_argument("--duration",default="30s"); s.add_argument("--style",default="realistic"); s.add_argument("--no-subtitles",dest="no_subtitles",default="false"); s.add_argument("--assets",default=""); s.add_argument("--scene",default="product photo"); s.add_argument("--ratio",default="1:1")
        if c=="inquiry-reply": s.add_argument("--customer-message",required=True)
    return p

def main():
    a=parser().parse_args()
    p=detect_profile(a.brand,a.brand_profile)
    data=CMDS[a.command](a,p)
    write_result(a.command,data,a.format,a.output_dir)

if __name__=="__main__": main()
