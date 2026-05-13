#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, re
from pathlib import Path

DEFAULT_OUTPUT_BASE = Path(r"D:\bot\outputs\business_tools")

BRAND_PROFILES = {
    "veytis": {
        "industries": ["essential oils wholesale", "hydrosol supplier", "fragrance oils", "carrier oils", "aroma diffuser oils"],
        "products": ["essential oils", "hydrosols", "fragrance oils", "carrier oils", "diffuser oils", "aroma diffuser machines"],
        "target_customers": ["importers", "distributors", "spa/wellness brands", "private label brands", "aromatherapy retailers"],
        "value_props": ["bulk supply", "private label", "OEM/ODM", "packaging customization", "quality document support"],
        "trust_elements": ["COA available upon request", "MSDS available upon request", "IFRA/SGS where applicable"],
        "visual_rules": ["neutral white", "cool ivory", "pale stone", "cool greige", "light taupe", "muted sage", "avoid yellow/red/orange cast", "realistic 4 fl oz / 120 mL amber Boston round dropper bottle", "no tall skinny serum bottle", "no squat bulky jar"],
        "copy_rules": ["premium natural B2B tone", "no fake health/medical claims", "no fake certification claims", "use available upon request for uncertain docs"],
    },
    "juese": {
        "industries": ["custom garment factory", "apparel OEM/ODM", "custom clothing manufacturer"],
        "products": ["custom hoodies", "custom t-shirts", "sportswear", "streetwear", "uniforms", "private label apparel"],
        "services": ["sampling", "fabric sourcing", "screen printing", "embroidery", "puff print", "washing", "QC", "packing"],
        "target_customers": ["streetwear brands", "ecommerce brands", "wholesale buyers", "merch brands", "apparel startups"],
        "production_process": ["tech pack review", "fabric/trims confirmation", "sampling", "bulk production", "inline QC", "final inspection", "packing/shipping"],
        "visual_rules": ["documentary realism", "clean Guangzhou garment factory", "correct sewing machine logic", "real sample room / QC / packing workflow", "no fake AI machinery", "no fake luxury showroom", "no dark dirty factory"],
        "copy_rules": ["process-first B2B tone", "avoid exaggerated promises", "avoid 100% defect-free claims", "lead time depending on order details"],
    },
    "generic": {"industries": ["B2B manufacturing"], "products": ["B2B product"], "target_customers": ["procurement buyers"], "value_props": ["structured process"], "trust_elements": ["documents available upon request"], "visual_rules": ["clean B2B realism"], "copy_rules": ["professional and factual"]},
}

def profile_key(brand: str | None, selected: str) -> str:
    if selected != "auto": return selected
    b = (brand or "").lower()
    if "veytis" in b: return "veytis"
    if "juese" in b: return "juese"
    return "generic"

def slugify(text: str | None) -> str:
    s = re.sub(r"[^a-z0-9\s-]", "", (text or "page").lower())
    return re.sub(r"\s+", "-", s).strip("-")

def kws(s: str | None): return [x.strip() for x in (s or "").split(",") if x.strip()]

def out_paths(command: str, output_dir: str | None = None):
    base = Path(output_dir) if output_dir else DEFAULT_OUTPUT_BASE
    d = base / dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{command}.md", d / f"{command}.json", d / f"{command}.txt"

def find_verify(obj):
    hits=[]
    if isinstance(obj, dict):
        for k,v in obj.items():
            if isinstance(v,(dict,list)): hits += find_verify(v)
            elif isinstance(v,str) and ("[verify]" in v or "available upon request" in v or "depending on order details" in v):
                hits.append(f"{k}: {v}")
    elif isinstance(obj,list):
        for v in obj: hits += find_verify(v)
    return hits

def build_markdown(command:str,data:dict)->str:
    title = data.get("title", command)
    summary = data.get("summary", "Structured B2B output generated.")
    strategy = data.get("strategy_notes", ["Target qualified B2B buyers", "Match content to commercial intent", "Drive RFQ-ready CTA"])
    checklist = data.get("action_checklist", ["Review [verify] fields", "Localize by country/language", "Publish and measure inquiries"])
    verification = data.get("verification_notes") or find_verify(data)
    rec = json.dumps({k:v for k,v in data.items() if k not in ["summary","strategy_notes","action_checklist","verification_notes","title"]}, ensure_ascii=False, indent=2)
    return f"# {title}\n\n## Executive Summary\n{summary}\n\n## Recommended Output\n```json\n{rec}\n```\n\n## Buyer Intent / Strategy Notes\n" + "\n".join(f"- {x}" for x in strategy) + "\n\n## Action Checklist\n" + "\n".join(f"- {x}" for x in checklist) + "\n\n## Verification Notes\n" + ("\n".join(f"- {x}" for x in verification) if verification else "- No explicit verification flags.") + "\n"

def write_result(command: str, data: dict, output_dir: str | None = None):
    mdp,jsp,txp = out_paths(command, output_dir)
    md = build_markdown(command,data)
    mdp.write_text(md,encoding="utf-8")
    txp.write_text(md,encoding="utf-8")
    jsp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"FILE:file:///{str(mdp).replace('\\','/')}")

def geo_plan(a,p):
    prof=BRAND_PROFILES[p]; kk=kws(a.keywords)
    return {"title":"GEO + SEO Strategic Plan","summary":f"{a.brand} {a.product or a.industry} plan for {a.country or '[verify]'} market across answer engines and local SEO.","geo_type":a.geo_type,
    "brand_entity_signals":[a.brand,a.industry,a.product,*prof.get("value_props",[])],"buyer_intent_questions":["Which supplier fits our spec and risk profile?","What documents are available upon request?","What is needed before quotation?"],
    "answer_engine_ready_paragraphs":["Provide concise, factual answers with qualification language such as available upon request and depending on order details.","Focus on process transparency: requirement intake, specification confirmation, production checkpoints, QC, and shipping handoff."],
    "topical_authority_clusters":["supplier qualification","quality documents","custom/private label workflow","logistics and lead-time planning"],
    "entity_relationships":["brand->industry","industry->product category","product->use case","service->buyer outcome"],
    "schema_recommendations":["FAQPage","Organization","Product","Service"],"comparison_content_plan":["manufacturer vs trader","private label vs standard","sample-first vs bulk-first"],
    "content_hub_plan":["pillar page","buyer guide articles","FAQ hub","service workflow page"],"internal_linking_plan":["/product-page -> /service-page","/blog -> /faq","/landing-page -> /contact"],
    "geographic_localization":{"country_terminology":a.country or "[verify]","language_notes":a.language or "English","shipping_payment_concerns":["incoterms [verify]","destination and customs","payment terms depending on order details"],"regional_keyword_variants":kk or [f"{a.product or 'product'} supplier"],"localized_faq":["Can you ship to our destination?","What docs are available where applicable?"]},
    "facts_to_verify":["lead time by order size","compliance scope by SKU","document availability by batch"],
    "30_day_execution_plan":["Days 1-7: publish pillar+FAQ","Days 8-14: comparison and use-case posts","Days 15-21: localized landing update","Days 22-30: optimize internal links and snippets"]}

def blog_brief(a,p):
    topic=a.topic or a.product or "B2B buying guide"; kw=kws(a.keywords)
    return {"title":"B2B SEO Blog Brief","summary":f"Commercial-intent brief for topic: {topic}.","search_intent":a.intent or "commercial","target_buyer_persona":["procurement manager","brand founder","import manager"],"pain_points":["supplier reliability","spec mismatch","unclear lead time"],
    "article_angle":"Practical buyer-side decision framework with verification checkpoints.","h1":topic,
    "h2_h3_outline":{"H2":["Supplier evaluation criteria","Specification and sample planning","MOQ/lead time/documents","Risk control before PO"],"H3":["Questions before RFQ","How to compare quotes","What to verify in documents"]},
    "key_talking_points":["Avoid single-variable price decisions","Ask for process visibility","Use [verify] for uncertain claims"],"faq":["What info is needed before quotation?","How to validate quality documents?"],"internal_links":["/product-page","/service-page","/faq","/contact"],
    "image_suggestions":BRAND_PROFILES[p]["visual_rules"][:4],"conversion_cta":"Send quantity, specifications, destination, and packaging requirements.","schema_suggestions":["Article","FAQPage","BreadcrumbList"],
    "anti_generic_writing_notes":["Use real procurement scenarios","No fake guarantees","No fabricated certifications"],"facts_needing_verification":["exact lead time","compliance details","regional shipping constraints"],
    "recommended_meta_title":f"{topic} | {a.brand}","recommended_meta_description":f"A B2B guide for choosing {a.industry or a.product} suppliers with quality, MOQ, and quote-readiness criteria."}

def blog_draft(a,p):
    topic=a.topic or "B2B Supplier Guide"
    return {"title":"B2B SEO Blog Draft","summary":"Editable English draft from procurement perspective with non-fabricated wording.","article":
f"""Title: {topic}\n\nMeta Title: {topic} | {a.brand}\nMeta Description: A practical B2B guide to evaluate suppliers, reduce sourcing risk, and prepare quote-ready requirements.\n\n# {topic}\n\n## Introduction\nIn B2B sourcing, a low headline price is not enough. Buyers need reliable process visibility, realistic lead-time communication, and documentation clarity. This draft explains how to evaluate suppliers using commercial criteria and verification checkpoints.\n\n## 1) Define your sourcing requirement before RFQ\nBefore contacting suppliers, confirm product scope, specification tolerance, destination market, and packaging requirements. If any variable is uncertain, keep it marked as [verify] so your quote comparison remains accurate.\n\n## 2) Evaluate process transparency, not just sales language\nAsk suppliers to describe requirement intake, sampling, bulk execution, QC checkpoints, and shipping handoff. Suppliers that provide structured workflows and factual boundaries usually reduce rework risk.\n\n## 3) Compare quotations with risk context\nCompare what is included in the offer: sample scope, packaging scope, documentation scope, and lead-time assumptions depending on order details. A quotation without scope clarity may look cheaper but cost more later.\n\n## 4) Document and compliance communication\nRequest documents such as COA/MSDS/IFRA/SGS only where applicable and available upon request. Avoid assuming every SKU has identical documentation status.\n\n## FAQ\nQ1: What should we submit before quotation?\nA1: Quantity, specifications, destination, packaging requirements, and target timeline.\nQ2: Can lead time be fixed before details are confirmed?\nA2: Lead time is usually depending on order details and current production loading.\n\n## CTA\nShare your quantity, specifications, destination, and packaging requirements to receive a structured B2B quotation plan.\n\n## SEO Checklist\n- Primary keyword in title/H1/introduction\n- Commercial intent preserved\n- Internal links to product/service/FAQ pages\n- FAQ section included\n\n## places_needing_verification\n- Exact lead time by quantity\n- Documentation scope per SKU\n- Regional shipping/compliance constraints\n"""}

def landing_page(a,p):
    prof=BRAND_PROFILES[p]
    return {"title":"Landing Page Blueprint","summary":"Full B2B landing structure for conversion-ready independent site page.","seo_title":f"{a.product or a.industry} | {a.brand}","meta_description":f"{a.brand} supports B2B buyers with structured process, QC checkpoints, and customization options.",
    "hero_headline":f"{a.product or a.industry} for Serious B2B Buyers","hero_subheadline":"Clear process, realistic timelines, and quote-ready communication.","trust_bar":prof.get("trust_elements",["documents available upon request"]),
    "buyer_pain_points":["unclear specs","communication delays","quality inconsistency","timeline uncertainty"],"capabilities_section":prof.get("value_props", prof.get("services",[])),
    "process_section":BRAND_PROFILES.get("juese",{}).get("production_process",["intake","confirm","execute","qc","ship"]) if p=="juese" else ["requirement intake","spec confirmation","sample/bulk","QC","shipping"],
    "quality_control_section":["pre-production confirmation","in-process checks","pre-shipment verification"],"customization_private_label_section":["OEM/ODM","private label","packaging customization"],
    "moq_sample_lead_time_notes":"MOQ/sample/lead time depending on order details.","faq":["What is MOQ?","Can samples be arranged?","What documents are available where applicable?"],"cta":"Send quantity, specs, destination, and packaging requirements.",
    "image_prompt_suggestions":prof["visual_rules"][:6],"layout_block_suggestions":["Hero","Trust Bar","Pain Points","Capabilities","Process","QC","FAQ","CTA"],"internal_link_suggestions":["/product-page","/service-page","/faq","/contact"]}

def product_page(a,p):
    prof=BRAND_PROFILES[p]; prod=a.product or prof["products"][0]
    common={"seo_title":f"{prod} Supplier | {a.brand}","meta_description":f"B2B {prod} supply with structured communication and customization options.","slug":slugify(prod),"hero":f"Reliable {prod} for B2B Procurement","product_overview":f"{a.brand} supports {prod} programs for importers and brand buyers.","moq_sample_lead_time_notes":"MOQ/sample/lead time depending on order details.","faq":["MOQ?","Sample policy?","Can documentation be provided where applicable?"],"cta":"Request a quote with quantity, specifications, destination, and packaging requirements.","image_prompts":prof["visual_rules"][:6],"internal_links":["/service-page","/faq","/contact"]}
    if p=="veytis":
        common.update({"applications":["private label lines","spa/wellness formulations","diffuser product lines"],"specification_table":[{"item":"Bottle","value":"4 fl oz / 120 mL amber Boston round [verify]"},{"item":"Oil type","value":prod},{"item":"Grade","value":"[verify]"}],"packaging_options":["bulk drums","small bottle lines","label customization"],"bulk_private_label_options":["bulk supply","private label","OEM/ODM"],"quality_documents_section":prof["trust_elements"],"compliance_wording_safety":"No medical claims. Documentation available upon request / where applicable."})
    else:
        common.update({"fabric_material_options":["cotton","polyester","fleece","spandex","GSM [verify]"],"customization_options":["screen print","embroidery","puff print","private label"],"size_color_sample_notes":"Size set, color standards, and sample approval required before bulk.","production_workflow":prof["production_process"],"qc_checkpoints":["inline QC","measurement check","final inspection"]})
    return common

def service_page(a,p):
    prof=BRAND_PROFILES[p]
    return {"title":"Service Page Blueprint","summary":"Independent B2B service page output (not mapped to landing-page).","service_positioning":f"{a.brand} provides {a.product or a.industry} with process-first risk control.","who_this_service_is_for":prof["target_customers"],
    "buyer_input_checklist":["quantity","spec/material","customization detail","destination","timeline"],"workflow_steps":prof.get("production_process",["intake","confirmation","execution","QC","shipping"]),"deliverables":["scope confirmation","sample/pre-production output","QC summary","handoff notes"],
    "qc_communication_checkpoints":["pre-production alignment","in-process update","pre-shipment confirmation"],"risk_controls":["spec sheet approval","milestone gating","packaging sign-off"],"what_we_need_before_quote":["quantity","specs","destination","packaging requirements"],
    "faq":["How long does sampling take?","How to handle spec changes?","How is QC communicated?"],"cta":"Share your brief and we will return an execution roadmap.","recommended_page_sections":["Positioning","Workflow","QC","Deliverables","FAQ","CTA"],"image_prompt_suggestions":prof["visual_rules"][:5]}

def _duration_scenes(d):
    d=(d or "30s").lower().replace(" ","")
    mapping={"15":[("0-3s","Hook"),("3-8s","Process"),("8-12s","Proof"),("12-15s","CTA")],"20":[("0-4s","Hook"),("4-10s","Process"),("10-16s","QC"),("16-20s","CTA")],"30":[("0-5s","Hook"),("5-12s","Process"),("12-22s","Proof"),("22-30s","CTA")],"45":[("0-6s","Hook"),("6-18s","Process"),("18-32s","Proof"),("32-40s","Trust"),("40-45s","CTA")],"60":[("0-8s","Hook"),("8-22s","Process"),("22-38s","Proof"),("38-52s","Trust"),("52-60s","CTA")]}
    for k,v in mapping.items():
        if d.startswith(k): return v
    return mapping["30"]

def video_script(a,p):
    style_bank={"veytis":["premium natural product","filling","labeling","packaging","showroom","diffuser oil","calm B2B"],"juese":["real garment factory","sample room","cutting","sewing","printing","embroidery","QC","packing","documentary realism"],"generic":["real workflow","process visibility"]}
    scenes=[]
    for t,beat in _duration_scenes(a.duration):
        scenes.append({"timecode":t,"camera_movement":"slow push" if beat in ["Hook","Proof"] else "handheld documentary","visual_description":style_bank[p][min(len(style_bank[p])-1,0)] + f" - {beat}","action":f"Show {beat.lower()} sequence for {a.topic or a.product or a.industry}","on_screen_text":"" if str(a.no_subtitles).lower()=="true" else f"{beat}: {a.topic or a.product or a.industry}","voiceover":f"{beat}: structured B2B process, transparent communication, and realistic delivery expectations."})
    return {"title":"Video Script Plan","summary":f"{a.duration} script for {a.platform} with {p} visual rule set.","total_duration":a.duration,"platform":a.platform,"style":a.style,"no_subtitles":a.no_subtitles,"scene_timeline":scenes,"b_roll_suggestions":style_bank[p],"asset_requirements":[x.strip() for x in (a.assets or "").split(",") if x.strip()] or ["logo","facility/product clips","contact end card"],"negative_prompt":"no fake machinery, no fake luxury, no exaggerated claims","platform_adaptation":{"TikTok":"strong first 3 seconds","Reels":"clean subtitles rhythm","Shorts":"fast transitions + clear CTA"}}

def image_prompt(a,p):
    if p=="veytis":
        brand_notes=["amber Boston round bottle","matte ivory label","4 fl oz / 120 mL","cool neutral background","no yellow/red/orange cast"]
    elif p=="juese":
        brand_notes=["real factory workflow","correct industrial sewing machine logic","realistic worktable","documentary lighting","no AI machine hallucination"]
    else:
        brand_notes=["clean realistic B2B scene"]
    return {"title":"Image Prompt Pack","summary":"Brand-locked prompt set for production-ready visuals.","main_prompt_english":f"{a.scene}, {a.product or ''}, {a.style}, {', '.join(brand_notes)}","negative_prompt":"over-saturated color cast, impossible machinery, fake text labels, distorted hands/tools","local_edit_prompt":"preserve layout; correct white balance; improve label readability; keep material realism","realism_checklist":["proportions accurate","lighting physically plausible","surface texture realistic","workflow tools consistent"],"composition_notes":["clear hero subject","clean background","space for headline text"],"lighting_notes":["soft neutral key light","avoid warm cast"],"material_accuracy_notes":["fabric weave/oil bottle glass details should look real"],"brand_consistency_notes":brand_notes,"text_label_rules":["simple readable English","no medical claims","no fake certificates"],"common_ai_artifacts_to_avoid":["warped logo","broken machine geometry","floating labels","nonsensical text"]}

def inquiry_reply(a,p):
    m=(a.customer_message or ""); ml=m.lower()
    q=re.search(r"\b(\d+(?:\.\d+)?)\s*(pcs|pieces|kg|ton|tons|bottles|sets)?\b",ml)
    qty = f"{q.group(1)} {q.group(2) or ''}".strip() if q else "[verify]"
    products=["hoodies","t-shirts","sportswear","essential oil","lavender oil","tea tree oil","hydrosol","fragrance oil","diffuser oil"]
    detected_product=next((x for x in products if x in ml), a.product or "[verify]")
    customs=[x for x in ["puff print","screen print","embroidery","private label","custom label","custom packaging","oem","odm"] if x in ml] or ["[verify]"]
    mats=re.findall(r"\b(cotton|fleece|polyester|spandex|gsm\s*\d+|4\s*oz|120\s*ml|1\s*kg|25\s*kg)\b",ml) or ["[verify]"]
    dest=re.search(r"(?:ship to|to|destination)\s+([a-zA-Z\s]+)",ml)
    shipping_term=next((x.upper() for x in ["fob","cif","ddp"] if x in ml),"[verify]")
    docs=[x.upper() for x in ["coa","msds","ifra","sgs","certificate"] if x in ml] or ["none mentioned"]
    dl = "urgent/rush order" if any(x in ml for x in ["urgent","rush order"]) else (re.search(r"(?:by|before)\s+([a-zA-Z0-9\s]+)",ml).group(1).strip() if re.search(r"(?:by|before)\s+([a-zA-Z0-9\s]+)",ml) else "[verify]")
    pack="custom packaging" if "pack" in ml else "[verify]"
    intent="quotation request" if any(x in ml for x in ["need","can you make","quote","price"]) else "information request"
    reply=(f"Thanks for your message. We can review your {qty} {detected_product} request"
           f" with {', '.join(customs) if customs[0] != '[verify]' else 'customization'}"
           f". Could you share full specifications/material, destination, and packaging requirements? "
           f"Once confirmed, we can provide a quotation and suggested timeline depending on order details.")
    return {"title":"Inquiry Reply Analysis","summary":"Parsed customer message and generated professional reply without fabricated commitments.","customer_intent":intent,"detected_quantity":qty,"detected_product":detected_product,"detected_customization":customs,"detected_material_or_spec":mats,"detected_destination":dest.group(1).strip() if dest else "[verify]","detected_shipping_term":shipping_term,"detected_packaging":pack,"detected_deadline":dl,"detected_document_request":docs,
    "missing_info":["complete spec/material","destination and incoterm","packaging details","target delivery window"],"risk_notes":["Do not commit fixed lead time before spec confirmation","Do not claim unavailable certifications"],"reply_en":reply,"whatsapp_short":f"Thanks! We can review your {qty} {detected_product} request. Please share specs, destination, and packaging for quotation.","follow_up_questions":["Any required material/GSM or purity specification?","Any label/artwork/packaging requirement?","Destination and incoterm (FOB/CIF/DDP)?"],"quotation_info_needed":["quantity","specification","destination","packaging","deadline"],"next_step":"Collect missing details -> feasibility check -> quotation proposal."}

def faq(a,p):
    groups={"MOQ":["What is your MOQ for first order?","Can MOQ differ by SKU?","Is trial MOQ possible depending on order details?"],"Samples":["Do you provide samples?","How long does sampling take?","Can sample cost be adjusted in bulk order?"],"Customization / Private Label":["Do you support private label?","Can packaging be customized?","Do you support OEM/ODM?"],"Quality Documents":["Can you provide COA/MSDS/IFRA/SGS where applicable?","When are documents shared?","Are docs batch-specific?"],"Lead Time":["How is lead time estimated?","Can lead time change with season?","Do you support urgent orders depending on capacity?"],"Packaging":["What packaging formats are available?","Can cartons be customized?","Do you support compliance labeling?"],"Shipping":["Which shipment modes are supported?","Can you ship to our destination country?","Do you support FOB/CIF/DDP depending on order details?"],"Payment":["What payment terms are commonly used?","Is split payment available?","How are bank charges handled?"],"After-sales":["How are quality issues handled?","What evidence is required for claims?","How quickly do you respond to after-sales tickets?"],"Compliance wording":["Can you guarantee certifications?","Can you provide medical claims?","How should uncertain compliance be stated?"]}
    return {"title":"B2B FAQ Library","summary":"20-30 brand-aware FAQs for independent-site content blocks.","brand":a.brand,"faq_groups":groups}

def content_calendar(a,p):
    channels=["Google SEO blog","LinkedIn","TikTok/Reels/Shorts","Pinterest image content","Email","Website page update"]
    out=[]
    for d in range(1,31):
        ch=channels[(d-1)%len(channels)]
        out.append({"day":d,"channel":ch,"content_type":"blog" if "blog" in ch.lower() else "post/update","topic":f"Day {d}: {(a.product or a.industry)} buyer question","keyword":kws(a.keywords)[0] if kws(a.keywords) else (a.product or "b2b supplier"),"buyer_intent":"commercial research","hook":"Solve one purchase-risk concern clearly","visual_idea":BRAND_PROFILES[p]["visual_rules"][0],"CTA":"Request quotation with specs and destination","funnel_stage":["TOFU","MOFU","BOFU"][d%3],"reuse_idea":"Repurpose as short video + LinkedIn post + email snippet"})
    return {"title":"30-Day Content Calendar","summary":"Cross-channel 30-day plan aligned to B2B funnel stages.","calendar":out}

def ad_keyword_plan(a,p):
    if p=="juese":
        keep=["custom clothing manufacturer","custom hoodie manufacturer","custom t shirt manufacturer","apparel OEM","private label clothing manufacturer","bulk custom hoodies"]
        risk=["ready made","blank","retail","cheap","free","jobs","pattern","near me","dropshipping","used","second hand"]
    elif p=="veytis":
        keep=["bulk essential oils supplier","private label essential oils","essential oil manufacturer","hydrosol supplier","fragrance oil wholesale","diffuser oil supplier"]
        risk=["DIY","recipe","therapeutic cure","medical treatment","free","retail near me","small personal use","jobs","course"]
    else:
        keep=[f"{a.product or 'product'} supplier"]; risk=["free","cheap","jobs"]
    return {"title":"Google Ads Keyword Plan","summary":"Campaign structure for qualified B2B lead generation.","campaign_goal":"qualified B2B RFQs","target_market":a.country or "[verify]","conversion_actions":["form submit","WhatsApp click","email inquiry"],"recommended_match_types":["exact","phrase","cautious broad"],"campaign_structure":["core intent","service intent","private label intent"],"ad_groups":["manufacturer","supplier","customization","wholesale"],"exact_keywords":[f"[{x}]" for x in keep[:4]],"phrase_keywords":[f'"{x}"' for x in keep[:4]],"cautious_broad_keywords":keep[2:],"landing_page_mapping":{"manufacturer":"/product-page","customization":"/service-page","wholesale":"/contact"},"ad_copy_angles":["process transparency","QC checkpoints","customization flexibility"],"sample_headlines":[f"{a.product or 'Product'} Manufacturer for B2B", "Private Label Support Available", "Get Quote with Specs"],"sample_descriptions":["Structured workflow from requirement to shipment.","Documentation available upon request where applicable."],"bid_budget_notes":["Prioritize exact+phrase first","Scale broad only with search-term controls"],"search_term_review_rules":["Promote converters to exact","Pause low-intent drains","Review regional terms before excluding"],"negative_keyword_seed":risk,"risk_notes":["Avoid over-excluding high-intent OEM/private-label terms","No exaggerated guarantee claims"]}

def negative_keywords(a,p):
    medical=["therapeutic cure","medical treatment","disease"] if p=="veytis" else []
    return {"title":"Negative Keyword Strategy","summary":"Tiered exclusion logic to protect B2B intent while avoiding overblocking.","must_exclude":["free","cheap","jobs","used","second hand","dropshipping","pattern"],"review_before_excluding":["Dubai","UAE","wholesale clothes","manufacturer","OEM","private label","bulk custom"],"keep_or_monitor":["custom clothing manufacturer","private label","bulk supplier"],"b2c_low_intent":["for myself","one piece","personal use"],"jobs_education":["job","hiring","course","training"],"free_diy_template":["free template","DIY recipe","pattern pdf"],"ready_made_or_retail_risk":["ready made","blank","retail","near me"],"competitor_or_marketplace_risk":["amazon","temu","alibaba"],"medical_or_claim_risk":medical,"country_specific_notes":{a.country or "default":"Keep market/geography terms under review if they convert."},"do_not_exclude_warning":"Do not exclude any term with verified conversion history.","review_rules":["Weekly search-term review","Move good terms to exact","Exclude only repeated low-intent patterns"]}

def seo_meta(a,p):
    seed=a.product or a.topic or a.industry or "b2b page"; slug=slugify(seed)
    return {"title":"SEO Meta Pack","summary":"SEO metadata set for page deployment.","seo_title":f"{seed} | {a.brand}","meta_description":f"{a.brand} supports {seed} with B2B process clarity and documentation available upon request.","slug":slug,"h1":seed,"open_graph_title":f"{seed} - {a.brand}","open_graph_description":f"B2B-focused {seed} page with clear process and CTA.","canonical_slug":f"/{slug}","keyword_focus":seed,"buyer_intent":"commercial","cta_line":"Request a quote with quantity, specifications, destination, and packaging requirements."}

def prompt_pack(a,p):
    defaults={"intent":"commercial","platform":"TikTok","duration":"30s","style":"realistic","no_subtitles":"false","assets":"","scene":"product photo","ratio":"1:1"}
    for k,v in defaults.items():
        if not hasattr(a,k) or getattr(a,k) is None: setattr(a,k,v)
    return {"title":"All-in-One Prompt Pack","summary":"Integrated Stage 3 pack for B2B growth workflows.","blog_brief":blog_brief(a,p),"blog_draft":blog_draft(a,p),"landing_page":landing_page(a,p),"product_page":product_page(a,p),"service_page":service_page(a,p),"video_script":video_script(a,p),"image_prompt":image_prompt(a,p),"faq":faq(a,p),"content_calendar_preview":content_calendar(a,p)["calendar"][:5],"ad_keyword_plan":ad_keyword_plan(a,p),"negative_keywords":negative_keywords(a,p),"seo_meta":seo_meta(a,p)}

CMDS={"geo-plan":geo_plan,"blog-brief":blog_brief,"blog-draft":blog_draft,"landing-page":landing_page,"product-page":product_page,"service-page":service_page,"video-script":video_script,"image-prompt":image_prompt,"inquiry-reply":inquiry_reply,"faq":faq,"content-calendar":content_calendar,"prompt-pack":prompt_pack,"ad-keyword-plan":ad_keyword_plan,"negative-keywords":negative_keywords,"seo-meta":seo_meta}

def parser():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest="command",required=True)
    def add_common(s):
        for n in ["brand","industry","country","language","product","audience","keywords","tone","market","funnel_stage"]: s.add_argument(f"--{n.replace('_','-')}",dest=n)
        s.add_argument("--brand-profile",choices=["auto","veytis","juese","generic"],default="auto")
        s.add_argument("--output-dir")
    for c in CMDS:
        s=sp.add_parser(c); add_common(s)
        if c in ["blog-brief","blog-draft","video-script","prompt-pack","seo-meta","ad-keyword-plan"]: s.add_argument("--topic")
        if c in ["blog-brief","blog-draft","prompt-pack"]: s.add_argument("--intent",default="commercial")
        if c=="geo-plan": s.add_argument("--geo-type",choices=["generative","geographic","both"],default="both")
        if c in ["video-script","prompt-pack"]:
            s.add_argument("--platform",default="TikTok"); s.add_argument("--duration",default="30s"); s.add_argument("--style",default="realistic"); s.add_argument("--no-subtitles",dest="no_subtitles",default="false"); s.add_argument("--assets",default="")
        if c in ["image-prompt","prompt-pack"]:
            s.add_argument("--scene",default="product photo"); s.add_argument("--ratio",default="1:1")
            if c=="image-prompt": s.add_argument("--style",default="realistic")
        if c=="inquiry-reply": s.add_argument("--customer-message",required=True)
    return p

def main():
    a=parser().parse_args(); pkey=profile_key(a.brand,a.brand_profile); result=CMDS[a.command](a,pkey); write_result(a.command,result,a.output_dir)

if __name__=="__main__": main()
