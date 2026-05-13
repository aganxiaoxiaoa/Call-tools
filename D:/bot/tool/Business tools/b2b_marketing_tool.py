#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, re
from pathlib import Path

DEFAULT_OUTPUT_BASE = Path(r"D:\bot\outputs\business_tools")
BRAND_PROFILES = {
"veytis": {"industries":["essential oils wholesale","hydrosol supplier","fragrance oils","carrier oils","diffuser oils","aroma diffuser machines"],"products":["essential oils","hydrosols","fragrance oils","carrier oils","diffuser oils","aroma diffuser machines"],"target_customers":["importers","distributors","spa/wellness brands","private label brands","aromatherapy retailers"],"value_props":["bulk supply","private label","OEM/ODM","packaging customization","quality document support"],"trust_elements":["COA/MSDS/IFRA/SGS available upon request / where applicable"],"visual_rules":["neutral white","cool ivory","pale stone","cool greige","light taupe","muted sage","avoid yellow cast, red cast, orange cast","realistic 4 fl oz / 120 mL amber Boston round dropper bottle","no tall skinny serum bottle","no squat bulky jar","matte ivory label"],"copy_rules":["premium natural B2B tone","no fake medical claims","no fake certification claims","no guaranteed cure/treatment/heal language","use available upon request for uncertain documents"]},
"juese": {"industries":["custom garment factory","apparel OEM/ODM","custom clothing manufacturer"],"products":["custom hoodies","custom t-shirts","sportswear","streetwear","uniforms","private label apparel"],"services":["sampling","fabric sourcing","screen printing","embroidery","puff print","washing","QC","packing"],"target_customers":["streetwear brands","ecommerce brands","wholesale buyers","merch brands","apparel startups"],"production_process":["tech pack review","fabric/trims confirmation","sampling","bulk production","inline QC","final inspection","packing/shipping"],"trust_elements":["sample room workflow","QC checkpoints","communication cadence"],"visual_rules":["documentary realism","clean Guangzhou garment factory","correct sewing machine logic","real sample room / QC / packing workflow","no fake AI machinery","no fake luxury showroom","no dark dirty factory"],"copy_rules":["process-first B2B tone","avoid exaggerated promises","avoid 100% defect-free claims","lead time depending on order details"]},
"generic": {"industries":["B2B manufacturing"],"products":["B2B product"],"target_customers":["B2B buyers"],"value_props":["structured process"],"trust_elements":["available upon request"],"visual_rules":["clean B2B realism"],"copy_rules":["factual tone"]}}

def profile_key(b,s):
    if s!="auto": return s
    b=(b or "").lower();
    return "veytis" if "veytis" in b else "juese" if "juese" in b else "generic"
def slugify(t): return re.sub(r"\s+","-",re.sub(r"[^a-z0-9\s-]","",(t or "page").lower())).strip("-")
def kws(s): return [x.strip() for x in (s or "").split(",") if x.strip()]

def out_paths(c,o=None):
    d=(Path(o) if o else DEFAULT_OUTPUT_BASE)/dt.datetime.now().strftime("%Y%m%d_%H%M%S"); d.mkdir(parents=True,exist_ok=True)
    return d/f"{c}.md", d/f"{c}.json", d/f"{c}.txt"
def flatten(d,depth=0):
    out=[]; pad="  "*depth
    if isinstance(d,dict):
      for k,v in d.items():
        if isinstance(v,(dict,list)): out.append(f"{pad}- **{k}**"); out+=flatten(v,depth+1)
        else: out.append(f"{pad}- **{k}**: {v}")
    elif isinstance(d,list):
      for v in d: out += flatten(v,depth+1) if isinstance(v,(dict,list)) else [f"{pad}- {v}"]
    return out
def verify_notes(d):
    txt=json.dumps(d,ensure_ascii=False)
    return [x for x in ["[verify]","available upon request","depending on order details"] if x in txt]
def build_markdown(cmd,data):
    rec={k:v for k,v in data.items() if k not in ["title","summary","strategy_notes","action_checklist"]}
    return f"# {data.get('title',cmd)}\n\n## Executive Summary\n{data.get('summary','Generated output.')}\n\n## Recommended Output\n"+"\n".join(flatten(rec))+"\n\n## Buyer Intent / Strategy Notes\n"+"\n".join(f"- {x}" for x in data.get("strategy_notes",["Focus on B2B buyer intent and conversion clarity."]))+"\n\n## Action Checklist\n"+"\n".join(f"- {x}" for x in data.get("action_checklist",["Review and replace all [verify] markers."]))+"\n\n## Verification Notes\n"+"\n".join(f"- {x}" for x in verify_notes(data))+"\n"
def write_result(c,d,o=None,f="both"):
    mdp,jsp,txp=out_paths(c,o); md=build_markdown(c,d); mdp.write_text(md,encoding='utf-8')
    if f in ["both","json"]: jsp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    if f in ["both","text","markdown"]: txp.write_text(md,encoding='utf-8')
    print(f"FILE:file:///{str(mdp).replace('\\','/')}")

# generators

def geo_plan(a,p):
    k=kws(a.keywords); base={"geo_type":a.geo_type,"brand_entity_signals":[a.brand,a.industry,a.product,*BRAND_PROFILES[p].get("value_props",[])],"buyer_intent_questions":["How to choose the right supplier?","What docs are available where applicable?"],"answer_engine_ready_paragraphs":["Use concise, source-like answers with verification wording.","Focus on requirements, process, QC, and shipping transparency."],"topical_authority_clusters":["supplier qualification","document handling","customization workflow","logistics planning"],"entity_relationships":["brand->industry","industry->products","services->buyer outcomes"],"schema_recommendations":["FAQPage","Organization","Product","Service","BreadcrumbList"],"comparison_content_plan":["manufacturer vs trader","sample-first vs bulk-first"],"content_hub_plan":["pillar page","FAQ hub","service hub"],"internal_linking_plan":["blog->product","product->service","landing->contact"],"facts_to_verify":["lead time","spec compliance scope","incoterms"],"30_day_execution_plan":["week1 pillar","week2 clusters","week3 localization","week4 optimization"]}
    geo={"geographic_localization":{"country_terminology":a.country or "[verify]","language_notes":a.language or "English","shipping_payment_concerns":["destination constraints","payment terms depending on order details"],"regional_keyword_variants":k or [f"{a.product or 'product'} supplier"],"localized_faq":["Can you ship to our region?","Which documents can be provided?"]}}
    if a.geo_type=="generative": return {**base}
    if a.geo_type=="geographic": return {"geo_type":a.geo_type,**geo}
    return {**base,**geo,"title":"GEO Plan","summary":"Generative GEO + Geographic SEO strategy."}

def blog_brief(a,p):
    topic=a.topic or a.product
    return {"title":"Blog Brief","summary":"B2B SEO brief with buyer-intent structure.","search_intent":a.intent or "commercial","target_buyer_persona":["procurement manager","brand owner"],"pain_points":["spec mismatch","unclear lead time","weak communication"],"article_angle":"decision-grade supplier evaluation","H1":topic,"H2_H3_outline":{"H2":["Define requirement","Evaluate process","Compare quotes","Manage risk"],"H3":["RFQ checklist","Document checks","Communication cadence"]},"key_talking_points":["focus on process clarity","avoid exaggerated claims"],"FAQ":["What info is needed before quote?","How to verify documents?"],"internal_links":["/product-page","/service-page","/faq"],"image_suggestions":BRAND_PROFILES[p]["visual_rules"][:4],"conversion_CTA":"Share quantity, specs, destination, packaging.","schema_suggestions":["Article","FAQPage"],"anti_generic_writing_notes":["use buyer scenarios","no fabricated facts"],"facts_needing_verification":["lead time","doc scope"],"recommended_meta_title":f"{topic} | {a.brand}","recommended_meta_description":f"B2B guide for {topic} with verification checkpoints.","word_count_guidance":a.word_count or "1200-1600","target_keyword_usage_plan":a.target_keyword or "primary keyword in title/H1/intro"}

def blog_draft(a,p):
    h2s=(a.outline.split(',') if a.outline else ["Define Requirement","Supplier Evaluation","Quote Comparison","Quality & Documentation","Logistics Planning","Risk Control","Final Decision"])
    sec="\n\n".join([f"## {x.strip()}\nFrom a B2B procurement perspective, clarify assumptions, documentation, and milestone ownership. Use [verify] for unknown values and avoid fixed promises on MOQ/lead time/price." for x in h2s[:7]])
    return {"title":"Blog Draft","summary":"Long-form editable English B2B draft.","draft":f"# {a.topic}\n\nIntroduction: Buyers should compare suppliers by process reliability, not only by initial unit price.\n\n{sec}\n\n## FAQ\nQ: What should be shared before quotation?\nA: Quantity, specification, destination, and packaging requirements.\n\n## CTA\nSend your RFQ details for a structured proposal depending on order details.\n\n## SEO checklist\n- Keyword in title/H1/intro\n- Internal links\n- FAQ block\n\n## places_needing_verification\n- MOQ\n- Lead time\n- Document coverage\n","word_count":a.word_count or "1500"}

def landing_page(a,p):
    return {"title":"Landing Page","summary":"Complete independent-site landing structure.","seo_title":f"{a.product} | {a.brand}","meta_description":f"{a.brand} supports B2B buyers with process clarity and quality controls.","hero_headline":f"{a.product} for B2B buyers","hero_subheadline":"Process-first execution and clear communication.","trust_bar":BRAND_PROFILES[p].get("trust_elements",[]),"buyer_pain_points":["quality inconsistency","communication gaps","timeline uncertainty"],"capability_section":BRAND_PROFILES[p].get("value_props",BRAND_PROFILES[p].get("services",[])),"process_section":BRAND_PROFILES[p].get("production_process",["intake","confirm","execute","QC","ship"]),"quality_control_section":["pre-production alignment","in-process checks","pre-shipment review"],"customization_private_label_section":["private label","OEM/ODM","packaging customization"],"MOQ_sample_lead_time_notes":"MOQ/sample/lead time depending on order details.","FAQ":["MOQ?","Sample policy?","Documents availability?"],"CTA":a.cta or "Share RFQ details for quotation.","image_prompt_suggestions":BRAND_PROFILES[p]["visual_rules"][:5],"layout_block_suggestions":["hero","trust","pain","capability","process","QC","FAQ","CTA"],"internal_link_suggestions":["/product-page","/service-page","/contact"],"target_audience_adaptation":a.target_audience or "importers and procurement teams"}

def product_page(a,p):
    base={"seo_title":f"{a.product} Supplier | {a.brand}","meta_description":f"B2B {a.product} with customization and documentation support.","slug":slugify(a.product),"hero":f"Reliable {a.product} for B2B procurement","features":kws(a.features),"specs":a.specs or "[verify]","moq":a.moq or "[verify]","price_tier":a.price_tier or "depending on order details","CTA":"Request quotation with full requirement details.","internal_links":["/service-page","/faq","/contact"]}
    if p=="veytis":
        base.update({"product_overview":"Designed for wholesale and private label workflows.","applications":["private label lines","spa/wellness use"],"specification_table":[{"item":"Bottle","value":"4 fl oz / 120 mL [verify]"},{"item":"Type","value":a.product}],"packaging_options":["bulk drum","small bottle line"],"bulk_private_label_options":["bulk supply","private label","OEM/ODM"],"quality_documents_section":BRAND_PROFILES[p]["trust_elements"],"compliance_wording_safety":"No medical claims; documents available upon request where applicable.","MOQ_sample_lead_time_notes":"depending on order details","FAQ":["MOQ?","Sample?","COA/MSDS availability?"],"image_prompts":BRAND_PROFILES[p]["visual_rules"][:6]})
    else:
        base.update({"product_overview":"Suitable for custom garment development and bulk manufacturing.","fabric_material_options":["cotton","polyester","fleece","spandex"],"customization_options":["screen print","embroidery","puff print","private label"],"size_color_sample_notes":"sample approval required before bulk","production_workflow":BRAND_PROFILES[p]["production_process"],"QC_checkpoints":["inline QC","final inspection"],"MOQ_sample_lead_time_notes":"depending on order details","FAQ":["MOQ?","Sample timeline?","QC process?"],"image_prompts":BRAND_PROFILES[p]["visual_rules"][:6]})
    return {"title":"Product Page","summary":"Brand-specific deep product-page output.",**base}

def service_page(a,p):
    return {"title":"Service Page","summary":"Deep service-page structure.","service_positioning":f"{a.service_type or a.product} with process-driven execution.","who_this_service_is_for":BRAND_PROFILES[p]["target_customers"],"buyer_input_checklist":["quantity","spec/material","destination","packaging","timeline"],"workflow_steps":(a.process_steps.split(',') if a.process_steps else BRAND_PROFILES[p].get("production_process",["intake","confirm","execute","QC","ship"])),"deliverables":["scope confirmation","milestone updates","QC summary"],"QC_communication_checkpoints":["pre-production","in-process","pre-shipment"],"risk_controls":["spec sign-off","milestone gating","change control"],"what_we_need_before_quote":["quantity","specs","destination","packaging"],"FAQ":["How long for sampling?","How are changes handled?"],"CTA":"Share project brief for roadmap.","recommended_page_sections":["positioning","workflow","QC","deliverables","FAQ"],"image_prompt_suggestions":BRAND_PROFILES[p]["visual_rules"][:5]}

def _dur(d):
    m={"15":[("0-3s","Hook"),("3-8s","Process"),("8-12s","Proof"),("12-15s","CTA")],"20":[("0-4s","Hook"),("4-10s","Process"),("10-16s","Proof"),("16-20s","CTA")],"30":[("0-5s","Hook"),("5-12s","Process"),("12-22s","Proof"),("22-30s","CTA")],"45":[("0-8s","Hook"),("8-20s","Process"),("20-35s","Proof"),("35-45s","CTA")],"60":[("0-10s","Hook"),("10-25s","Process"),("25-45s","Proof"),("45-60s","CTA")]}
    d=(d or "30s").lower().replace(" ","")
    return next((v for k,v in m.items() if d.startswith(k)),m["30"])

def video_script(a,p):
    bank={"veytis":["premium natural product","filling","labeling","packaging","showroom"],"juese":["sample room","cutting","sewing","printing/embroidery","QC/packing"],"generic":["process","quality","shipping"]}
    s=[]
    for i,(t,b) in enumerate(_dur(a.duration)):
        s.append({"timecode":t,"camera_movement":"slow push" if i%2==0 else "handheld documentary","visual_description":bank[p][i%len(bank[p])],"action":b,"on_screen_text":"" if str(a.no_subtitles).lower()=="true" else f"{b}: {a.topic}","voiceover":f"{b}: process-first B2B narrative."})
    return {"title":"Video Script","summary":"Duration-aware brand-specific storyboard.","total_duration":a.duration,"platform":a.platform,"style":a.style,"no_subtitles":a.no_subtitles,"scene_timeline":s,"b_roll_suggestions":bank[p],"asset_requirements":["logo","workflow clips","end-card"],"negative_prompt":"no fake machinery, no exaggerated claims","platform_adaptation":{"TikTok":"strong first 3s","LinkedIn":"informative tone"}}

def image_prompt(a,p):
    bn=BRAND_PROFILES[p]["visual_rules"]
    return {"title":"Image Prompt","summary":"Deep brand-aware prompt package.","main_prompt_english":f"{a.scene}, {a.product}, {a.style}, {', '.join(bn[:6])}","negative_prompt":"yellow/red/orange cast, fake machinery, warped text","local_edit_prompt":"improve realism and label readability","realism_checklist":["proportion accuracy","natural lighting","material realism"],"composition_notes":["clear hero subject","clean background"],"lighting_notes":["soft neutral key light"],"material_accuracy_notes":["accurate bottle/fabric textures"],"brand_consistency_notes":bn,"text_label_rules":["no medical claims","no fake certifications"],"common_ai_artifacts_to_avoid":["warped logos","floating labels"],"product_type":a.product_type,"style_reference":a.style_reference,"color_palette":a.color_palette}

def inquiry_reply(a,p):
    m=(a.customer_message or "").lower()
    prod_terms=["lavender essential oil","tea tree oil","hydrosol","fragrance oil","diffuser oil","essential oil","hoodies","t-shirts","sportswear"]
    prod=next((x for x in prod_terms if x in m),"[verify]")
    q=re.search(r"(\d+(?:\.\d+)?)\s*(pcs|pieces|kg|ton|bottles|sets)?",m); qty=(q.group(1)+" "+(q.group(2) or "")).strip() if q else "[verify]"
    dest=(re.search(r"ship to\s+([a-zA-Z]+)",m) or re.search(r"destination\s+([a-zA-Z]+)",m))
    ddl="urgent/rush order" if any(x in m for x in ["urgent","rush order"]) else ((re.search(r"before\s+([a-zA-Z]+\s*\d{0,2})",m) or re.search(r"by\s+([a-zA-Z]+\s*\d{0,2})",m)).group(1) if (re.search(r"before\s+([a-zA-Z]+\s*\d{0,2})",m) or re.search(r"by\s+([a-zA-Z]+\s*\d{0,2})",m)) else "[verify]")
    docs=[x.upper() for x in ["coa","msds","ifra","sgs","certificate"] if x in m] or ["none mentioned"]
    cust=[x for x in ["private label","custom label","custom packaging","oem","odm","embroidery","puff print","screen print"] if x in m] or ["[verify]"]
    reply=f"Thanks for your message. We can review your {qty} {prod} request. Please share detailed specification/material, destination, and packaging requirements so we can provide an accurate quotation depending on order details."
    return {"title":"Inquiry Reply","summary":"Dynamic parsed inquiry response.","customer_intent":"quotation request","detected_quantity":qty,"detected_product":prod,"detected_customization":cust,"detected_material_or_spec":re.findall(r"cotton|fleece|polyester|spandex|gsm\s*\d+|4\s*oz|120\s*ml|25\s*kg",m) or ["[verify]"],"detected_destination":dest.group(1) if dest else "[verify]","detected_packaging":"custom packaging" if "pack" in m else "[verify]","detected_deadline":ddl,"detected_document_request":docs,"missing_info":["full specs","destination","packaging","timeline"],"risk_notes":["avoid fixed lead-time promise","avoid fabricated documentation claims"],"reply_en":reply,"whatsapp_short":f"Thanks! Please share specs/destination/packaging for your {qty} {prod} quotation.","follow_up_questions":["Any specific material/grade?","Any label/packaging requirement?"],"quotation_info_needed":["quantity","spec","destination","packaging"],"next_step":"collect details -> feasibility check -> quote"}

def faq(a,p):
    c=int(a.count or 24)
    g={"MOQ":["What MOQ applies to first order?","Can MOQ vary by SKU?"],"Samples":["Do you provide samples?","How long for sample turnaround?"],"Customization / Private Label":["Do you support private label?","Can packaging be customized?"],"Quality Documents":["Are COA/MSDS/IFRA/SGS available where applicable?"],"Lead Time":["How is lead time estimated?"],"Packaging":["What packaging formats are available?"],"Shipping":["Which shipping terms can be discussed?"],"Payment":["What payment terms are typical?"],"After-sales":["How are quality concerns handled?"],"Compliance wording":["No medical claims policy?"]}
    return {"title":"FAQ Library","summary":"Brand-aware FAQ groups.","count":c,"faq_groups":g}

def content_calendar(a,p):
    n=int(a.count or 30); ch=["Google SEO blog","LinkedIn","TikTok/Reels/Shorts","Pinterest/image content","Email","Website page update"]; rows=[]
    for i in range(1,n+1):
        rows.append({"day":i,"channel":ch[(i-1)%len(ch)],"content_type":"post" if i%2 else "guide","topic":f"Day {i}: {a.product} buyer question","keyword":kws(a.keywords)[0] if kws(a.keywords) else (a.product or "b2b supplier"),"buyer_intent":"commercial","hook":"reduce procurement risk","visual_idea":BRAND_PROFILES[p]["visual_rules"][0],"CTA":"Request quote with full RFQ details","funnel_stage":["TOFU","MOFU","BOFU"][i%3],"reuse_idea":"repurpose into short/video/email"})
    return {"title":"Content Calendar","summary":f"{n}-day multichannel plan.","calendar":rows}

def ad_keyword_plan(a,p):
    keep=["custom clothing manufacturer","custom hoodie manufacturer","custom t shirt manufacturer","apparel OEM","private label clothing manufacturer","bulk custom hoodies"] if p=="juese" else ["bulk essential oils supplier","private label essential oils","essential oil manufacturer","hydrosol supplier","fragrance oil wholesale","diffuser oil supplier"]
    risk=["ready made","blank","retail","cheap","free","jobs","pattern","near me","dropshipping","used","second hand"] if p=="juese" else ["DIY","recipe","therapeutic cure","medical treatment","free","retail near me","small personal use","jobs","course"]
    return {"title":"Ad Keyword Plan","summary":"Deep Google Ads structure.","campaign_goal":a.campaign_goal or "qualified B2B leads","target_market":a.target_market or a.country or "[verify]","conversion_actions":["form submit","WhatsApp click"],"recommended_match_types":["exact","phrase","cautious broad"],"campaign_structure":["core","service","private label"],"ad_groups":["manufacturer","supplier","customization"],"exact_keywords":keep[:4],"phrase_keywords":keep[1:5],"cautious_broad_keywords":keep[3:],"landing_page_mapping":{"core":"/product-page","custom":"/service-page"},"ad_copy_angles":["process transparency","QC checkpoints"],"sample_headlines":[f"{a.product} Manufacturer for B2B","Private Label Support"],"sample_descriptions":["Structured process and realistic timeline communication."],"bid_budget_notes":a.budget or "start controlled and scale by conversion quality","search_term_review_rules":["promote converters to exact","exclude repeated low intent"],"negative_keyword_seed":risk,"risk_notes":["Do not over-exclude converting terms"]}

def negative_keywords(a,p):
    return {"title":"Negative Keywords","summary":"Tiered exclusion framework.","must_exclude":["free","cheap","jobs","used"],"review_before_excluding":["Dubai","UAE","wholesale clothes","manufacturer","OEM","private label","bulk custom"],"keep_or_monitor":["private label","manufacturer","bulk custom"],"b2c_low_intent":["for myself","one piece"],"jobs_education":["jobs","course"],"free_diy_template":["free template","DIY recipe"],"ready_made_or_retail_risk":["ready made","blank","retail","near me"],"competitor_or_marketplace_risk":["amazon","temu","alibaba"],"medical_or_claim_risk":["therapeutic cure","medical treatment"] if p=="veytis" else [],"country_specific_notes":{a.country or "default":"review country terms if converting"},"do_not_exclude_warning":"If term converts, do not exclude blindly.","review_rules":["weekly review","move winners to exact"]}

def seo_meta(a,p):
    seed=a.target_keyword or a.product or a.topic
    return {"title":"SEO Meta","summary":"SEO metadata pack.","seo_title":f"{seed} | {a.brand}","meta_description":f"B2B {seed} page with process clarity and quote CTA.","slug":slugify(seed),"h1":seed,"open_graph_title":f"{seed} - {a.brand}","open_graph_description":"B2B supplier page","canonical_slug":"/"+slugify(seed),"keyword_focus":seed,"buyer_intent":"commercial","CTA_line":"Send RFQ details for quotation.","page_type":a.page_type}

def product_description(a,p):
    return {"title":"Product Description","summary":"Short B2B card/listing description.","short_description":f"{a.product} designed for B2B sourcing with process transparency.","bullet_points":[*kws(a.features),a.specs or "[verify]"],"seo_snippet":a.target_keyword or a.product,"card_title":a.product,"compliance_notes":"available upon request / depending on order details","CTA":"Request a spec-based quote","feature_spec_integration":{"features":kws(a.features),"specs":a.specs},"buyer_angle":"focus on RFQ-readiness and supply reliability"}

def category_page(a,p):
    return {"title":"Category Page","summary":"Deep category/collection page copy.","SEO_title":f"{a.category} Supplier | {a.brand}","meta_description":f"Explore {a.category} options for B2B procurement.","slug":slugify(a.category),"category_hero":f"{a.category} for B2B buyers","category_overview":"Group by use case/specification for faster sourcing decisions.","product_grouping_suggestions":["by application","by format","by customization"],"buyer_guide":["define requirement","compare options","send RFQ"],"comparison_blocks":["standard vs private label","sample-first vs bulk-first"],"FAQ":["MOQ by group?","Sample options?"],"CTA":"Submit category RFQ list.","internal_links":["/product-page","/service-page","/contact"],"image_prompt_ideas":BRAND_PROFILES[p]["visual_rules"][:4]}

def about_us(a,p):
    return {"title":"About Us","summary":"Trust-focused About page without fabricated business facts.","brand_positioning":f"{a.brand} is a process-first B2B partner in {a.industry}.","what_we_do":a.mission or "support sourcing from requirement to delivery","who_we_serve":BRAND_PROFILES[p]["target_customers"],"workflow_process_credibility":"clear intake, milestone checks, and communication cadence","quality_philosophy":"consistency and transparent commitments","why_buyers_choose_us":["clear process","responsive communication","verification-safe claims"],"verification_placeholders":{"history":a.history or "[verify]","team_size":a.team_size or "[verify]","factory_area":"[verify]","capacity":"[verify]"},"CTA":"Share your project brief for workflow planning."}

def email_template(a,p):
    sc=(a.scenario or "first outreach").lower(); prod=a.product or "product"
    return {"title":"Email Template","summary":f"Scenario-based email: {sc}.","subject_options":[f"{prod} sourcing support",f"Follow-up on {prod} inquiry",f"{a.brand} B2B quote info request"],"email_body":f"Hello,\n\nThanks for your interest in {prod}. To prepare an accurate quotation, please share quantity, specifications, destination, and packaging requirements. We will reply with options depending on order details.\n\nBest regards,\n{a.brand}","short_follow_up":"Just following up—please share RFQ details so we can proceed.","WhatsApp_version":"Thanks! Please share qty/specs/destination/packaging for quote.","required_info_checklist":["quantity","specification","destination","packaging","timeline"],"tone_adaptation":a.tone or "professional"}

def social_post(a,p):
    return {"title":"Social Post","summary":"Platform-specific B2B post.","platform":a.platform,"hook":"Reduce sourcing risk before your next PO.","post_text":f"For {a.topic}, compare suppliers on process clarity, QC checkpoints, and documentation scope—not only unit price.","CTA":"Message us with RFQ details.","hashtag_suggestions":["#B2B","#Sourcing","#OEM","#PrivateLabel"],"visual_idea":BRAND_PROFILES[p]["visual_rules"][0],"short_version":f"{a.topic}: process + QC + documentation first.","buyer_intent_angle":"commercial research"}

def prompt_pack(a,p):
    for k,v in {"intent":"commercial","platform":"TikTok","duration":"30s","style":"realistic","no_subtitles":"false","assets":"","scene":"product photo","ratio":"1:1"}.items():
        if not hasattr(a,k) or getattr(a,k) is None: setattr(a,k,v)
    return {"title":"Prompt Pack","summary":"Integrated all-in-one output.","blog_brief":blog_brief(a,p),"blog_draft":blog_draft(a,p),"landing_page":landing_page(a,p),"product_page":product_page(a,p),"service_page":service_page(a,p),"video_script":video_script(a,p),"image_prompt":image_prompt(a,p),"faq":faq(a,p),"content_calendar_preview":content_calendar(a,p)["calendar"][:3],"ad_keyword_plan":ad_keyword_plan(a,p),"negative_keywords":negative_keywords(a,p),"seo_meta":seo_meta(a,p)}

CMDS={"geo-plan":geo_plan,"blog-brief":blog_brief,"blog-draft":blog_draft,"landing-page":landing_page,"product-page":product_page,"service-page":service_page,"video-script":video_script,"image-prompt":image_prompt,"inquiry-reply":inquiry_reply,"faq":faq,"content-calendar":content_calendar,"prompt-pack":prompt_pack,"ad-keyword-plan":ad_keyword_plan,"negative-keywords":negative_keywords,"seo-meta":seo_meta,"product-description":product_description,"category-page":category_page,"about-us":about_us,"email-template":email_template,"social-post":social_post}

def parser():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest='command',required=True)
    def common(s):
        for n in ["brand","industry","country","language","product","audience","keywords","tone","market","funnel_stage","target_market","buyer_level","brief","verify_mark"]: s.add_argument(f"--{n.replace('_','-')}",dest=n)
        s.add_argument('--brand-profile',choices=['auto','veytis','juese','generic'],default='auto'); s.add_argument('--output-dir'); s.add_argument('--format',choices=['markdown','json','text','both'],default='both')
    for c in CMDS:
        s=sp.add_parser(c); common(s)
        if c in ["blog-brief","blog-draft","video-script","prompt-pack","seo-meta","ad-keyword-plan","social-post"]: s.add_argument('--topic')
        if c in ["blog-brief","blog-draft","prompt-pack"]: s.add_argument('--intent',default='commercial')
        if c=='geo-plan': s.add_argument('--geo-type',choices=['generative','geographic','both'],default='both')
        if c in ['video-script','prompt-pack']:
            s.add_argument('--platform',default='TikTok'); s.add_argument('--duration',default='30s'); s.add_argument('--style',default='realistic'); s.add_argument('--no-subtitles',dest='no_subtitles',default='false'); s.add_argument('--assets',default='')
        if c in ['image-prompt','prompt-pack']:
            s.add_argument('--scene',default='product photo'); s.add_argument('--ratio',default='1:1'); s.add_argument('--product-type'); s.add_argument('--style-reference'); s.add_argument('--color-palette')
            if c=='image-prompt': s.add_argument('--style',default='realistic')
        if c=='inquiry-reply': s.add_argument('--customer-message',required=True); s.add_argument('--scenario'); s.add_argument('--price-range')
        if c in ['blog-brief','blog-draft','seo-meta','product-description','category-page']: s.add_argument('--target-keyword')
        if c in ['blog-brief','blog-draft']: s.add_argument('--word-count')
        if c=='blog-draft': s.add_argument('--outline')
        if c=='seo-meta': s.add_argument('--page-type')
        if c=='ad-keyword-plan': s.add_argument('--budget'); s.add_argument('--campaign-goal')
        if c=='negative-keywords': s.add_argument('--product-type')
        if c in ['product-page','product-description']: s.add_argument('--features'); s.add_argument('--specs'); s.add_argument('--moq'); s.add_argument('--price-tier'); s.add_argument('--style')
        if c=='service-page': s.add_argument('--service-type'); s.add_argument('--process-steps')
        if c=='landing-page': s.add_argument('--cta'); s.add_argument('--target-audience')
        if c in ['faq','content-calendar']: s.add_argument('--count')
        if c=='category-page': s.add_argument('--category'); s.add_argument('--product-count')
        if c=='about-us': s.add_argument('--mission'); s.add_argument('--history'); s.add_argument('--team-size')
        if c=='email-template': s.add_argument('--scenario')
        if c=='social-post': s.add_argument('--platform')
    return p

def main():
    a=parser().parse_args(); p=profile_key(a.brand,a.brand_profile); write_result(a.command,CMDS[a.command](a,p),a.output_dir,a.format)
if __name__=='__main__': main()
