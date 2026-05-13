#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, re
from pathlib import Path
DEFAULT_OUTPUT_BASE=Path(r"D:\bot\outputs\business_tools")
BRAND_PROFILES={"veytis":{"target_customers":["importers"],"visual_rules":["cool neutral background"]},"juese":{"target_customers":["streetwear brands"],"visual_rules":["documentary realism"]},"generic":{"target_customers":["B2B buyers"],"visual_rules":["clean B2B realism"]}}

def profile_key(b,s):
    if s!="auto":return s
    b=(b or "").lower();
    return "veytis" if "veytis" in b else "juese" if "juese" in b else "generic"
def slugify(t): return re.sub(r"\s+","-",re.sub(r"[^a-z0-9\s-]","",(t or "page").lower())).strip("-")
def kws(s): return [x.strip() for x in (s or "").split(",") if x.strip()]
def out_paths(c,o=None): d=(Path(o) if o else DEFAULT_OUTPUT_BASE)/dt.datetime.now().strftime("%Y%m%d_%H%M%S"); d.mkdir(parents=True,exist_ok=True); return d/f"{c}.md",d/f"{c}.json",d/f"{c}.txt"
def find_verify(o):
    r=[]
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,(dict,list)): r+=find_verify(v)
            elif isinstance(v,str) and ("[verify]" in v or "available upon request" in v or "depending on order details" in v): r.append(f"{k}: {v}")
    elif isinstance(o,list):
        for v in o:r+=find_verify(v)
    return r
def build_markdown(c,d):
    rec=json.dumps({k:v for k,v in d.items() if k not in ["summary","strategy_notes","action_checklist","verification_notes","title"]},ensure_ascii=False,indent=2)
    return f"# {d.get('title',c)}\n\n## Executive Summary\n{d.get('summary','Generated.')}\n\n## Recommended Output\n```json\n{rec}\n```\n\n## Buyer Intent / Strategy Notes\n"+"\n".join(f"- {x}" for x in d.get("strategy_notes",["Target qualified B2B buyers"]))+"\n\n## Action Checklist\n"+"\n".join(f"- {x}" for x in d.get("action_checklist",["Review [verify] fields"]))+"\n\n## Verification Notes\n"+"\n".join(f"- {x}" for x in (d.get("verification_notes") or find_verify(d) or ["No explicit verification flags."]))+"\n"
def write_result(c,d,o=None,f="both"):
    mdp,jsp,txp=out_paths(c,o); md=build_markdown(c,d); mdp.write_text(md,encoding='utf-8')
    if f in ["both","json"]: jsp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    if f in ["both","text","markdown"]: txp.write_text(md,encoding='utf-8')
    print(f"FILE:file:///{str(mdp).replace('\\','/')}")

def geo_plan(a,p): return {"title":"GEO Plan","summary":"Generative + Geographic plan.","geo_type":a.geo_type}
def blog_brief(a,p): return {"title":"Blog Brief","summary":"B2B brief","search_intent":a.intent,"target_keyword":a.target_keyword,"word_count":a.word_count}
def blog_draft(a,p): return {"title":"Blog Draft","summary":"English draft","article":f"# {a.topic}\n\nB2B procurement draft with FAQ/CTA and [verify] placeholders.","target_keyword":a.target_keyword,"word_count":a.word_count,"outline":a.outline}
def landing_page(a,p): return {"title":"Landing Page","summary":"Landing structure","cta":a.cta or "Send quantity/spec/destination for quote.","target_audience":a.target_audience or "B2B buyers"}
def product_page(a,p): return {"title":"Product Page","summary":"Independent product page","product":a.product,"features":kws(a.features),"specs":a.specs,"moq":a.moq or "[verify]","price_tier":a.price_tier or "depending on order details"}
def service_page(a,p): return {"title":"Service Page","summary":"Independent service page","service_type":a.service_type or a.product,"process_steps":a.process_steps or "[verify]"}
def _duration_scenes(d):
    m={"15":[("0-3s","Hook"),("3-8s","Process"),("8-12s","Proof"),("12-15s","CTA")],"20":[("0-4s","Hook"),("4-10s","Process"),("10-16s","QC"),("16-20s","CTA")],"30":[("0-5s","Hook"),("5-12s","Process"),("12-22s","Proof"),("22-30s","CTA")],"45":[("0-8s","Hook"),("8-20s","Process"),("20-34s","Proof"),("34-45s","CTA")],"60":[("0-10s","Hook"),("10-25s","Process"),("25-45s","Proof"),("45-60s","CTA")]}
    ds=(d or '30s').replace(' ','').lower()
    for k,v in m.items():
        if ds.startswith(k): return v
    return m['30']
def video_script(a,p):
    bank={"veytis":["premium natural product","filling","labeling","packaging","showroom"],"juese":["sample room","cutting","sewing","embroidery","QC"],"generic":["workflow","quality","shipping"]}
    scenes=[]
    for i,(t,b) in enumerate(_duration_scenes(a.duration)):
        scenes.append({"timecode":t,"camera_movement":"slow push" if i%2==0 else "handheld","visual_description":bank[p][i%len(bank[p])]+f" - {b}","action":b,"on_screen_text":"" if str(a.no_subtitles).lower()=="true" else f"{b}: {a.topic}","voiceover":f"{b}: process-first B2B message."})
    return {"title":"Video Script","summary":"Duration-aware storyboard","total_duration":a.duration,"platform":a.platform,"style":a.style,"no_subtitles":a.no_subtitles,"scene_timeline":scenes}
def image_prompt(a,p): return {"title":"Image Prompt","summary":"Brand prompt","product_type":a.product_type,"style_reference":a.style_reference,"color_palette":a.color_palette,"main_prompt_english":f"{a.scene}, {a.product}, {a.style}"}
def inquiry_reply(a,p):
    ml=(a.customer_message or '').lower(); q=re.search(r"\b(\d+(?:\.\d+)?)\s*(kg|pcs|pieces|ton|bottles|sets)?\b",ml); qty=f"{q.group(1)} {q.group(2) or ''}".strip() if q else "[verify]"
    products=["lavender essential oil","tea tree oil","essential oil","hoodies","t-shirts","sportswear","hydrosol","fragrance oil","diffuser oil"]; prod=next((x for x in products if x in ml),"[verify]")
    cust=[x for x in ["puff print","screen print","embroidery","private label","custom label","custom packaging","oem","odm"] if x in ml] or ["[verify]"]
    docs=[x.upper() for x in ["coa","msds","ifra","sgs","certificate"] if x in ml] or ["none mentioned"]
    dest=(re.search(r"ship to\s+([a-zA-Z]+)",ml) or re.search(r"destination\s+([a-zA-Z]+)",ml) or re.search(r"\bto\s+(uk|usa|germany)\b",ml))
    dline=(re.search(r"before\s+([a-zA-Z]+\s*\d{0,2})",ml) or re.search(r"by\s+([a-zA-Z]+\s*\d{0,2})",ml))
    reply=f"Thanks for your message. We can review your {qty} {prod} request. Please share full specifications, destination, and packaging requirements so we can provide an accurate quotation depending on order details."
    return {"title":"Inquiry Reply","summary":"Dynamic parsing and response","scenario":a.scenario,"price_range":a.price_range,"customer_intent":"quotation request","detected_quantity":qty,"detected_product":prod,"detected_customization":cust,"detected_material_or_spec":[x for x in re.findall(r"(cotton|fleece|polyester|spandex|gsm\s*\d+|4\s*oz|120\s*ml|25\s*kg)",ml)] or ["[verify]"],"detected_destination":dest.group(1).upper() if dest else "[verify]","detected_packaging":"custom packaging" if "pack" in ml else "[verify]","detected_deadline":dline.group(1) if dline else "[verify]","detected_document_request":docs,"reply_en":reply,"whatsapp_short":f"Thanks! We can review your {qty} {prod} request. Please share specs/destination/packaging for quote."}
def faq(a,p): return {"title":"FAQ","summary":"Grouped FAQs","count":a.count or "20"}
def content_calendar(a,p): return {"title":"30-day Calendar","summary":"Cross-channel plan"}
def ad_keyword_plan(a,p): return {"title":"Ad Keyword Plan","summary":"Google Ads structure","budget":a.budget,"campaign_goal":a.campaign_goal}
def negative_keywords(a,p): return {"title":"Negative Keywords","summary":"Tiered exclusions","product_type":a.product_type}
def seo_meta(a,p): return {"title":"SEO Meta","summary":"Metadata pack","page_type":a.page_type,"target_keyword":a.target_keyword}
def product_description(a,p): return {"title":"Product Description","summary":"Card/listing copy","short_description":f"{a.product} for B2B buyers.","bullet_points":kws(a.features),"seo_snippet":a.target_keyword or a.product,"card_title":a.product,"compliance_notes":"available upon request / depending on order details","CTA":"Request quote"}
def category_page(a,p): return {"title":"Category Page","summary":"Collection-page copy","seo_title":f"{a.category} | {a.brand}","meta_description":f"{a.category} options for B2B buyers.","category_hero":a.category,"category_overview":"Compare by use-case and spec.","buyer_guide":["Select SKU","Confirm spec","Send RFQ"],"product_grouping_suggestions":["by application","by format"],"faq":["MOQ?","Sample?"],"CTA":"Request category quotation","internal_links":["/product-page","/contact"]}
def about_us(a,p): return {"title":"About Us","summary":"About page without fabricated numbers","brand_positioning":f"{a.brand} is a {a.industry} partner","what_we_do":a.mission or "Support sourcing workflows","who_we_serve":BRAND_PROFILES[p]['target_customers'],"workflow_process_credibility":"process-first communication","quality_philosophy":"consistency and transparency","verification_placeholders":{"history":a.history or "[verify]","team_size":a.team_size or "[verify]"},"CTA":"Share your project brief"}
def email_template(a,p): return {"title":"Email Template","summary":"B2B email draft","subject_options":["Quick sourcing request","Quote info request","Follow-up"],"email_body":f"Thanks for your interest in {a.product}. Please share quantity, specs, destination, and packaging requirements.","short_follow_up":"Following up on your request.","whatsapp_version":"Please share qty/specs/destination for quotation.","required_info_checklist":["quantity","specs","destination","packaging"]}
def social_post(a,p): return {"title":"Social Post","summary":"Platform post draft","post_text":f"{a.topic}: compare suppliers on process and QC, not only price.","hook":"Reduce sourcing risk with better requirements.","CTA":"DM for RFQ checklist","hashtag_suggestions":["#B2B","#Sourcing"],"visual_idea":BRAND_PROFILES[p]['visual_rules'][0],"short_version":f"{a.topic}: process + QC first."}
def prompt_pack(a,p):
    for k,v in {"intent":"commercial","platform":"TikTok","duration":"30s","style":"realistic","no_subtitles":"false","assets":"","scene":"product photo","ratio":"1:1"}.items():
        if not hasattr(a,k) or getattr(a,k) is None: setattr(a,k,v)
    return {"title":"Prompt Pack","summary":"Integrated outputs","blog_brief":blog_brief(a,p),"blog_draft":blog_draft(a,p),"landing_page":landing_page(a,p),"product_page":product_page(a,p),"service_page":service_page(a,p),"video_script":video_script(a,p),"image_prompt":image_prompt(a,p),"faq":faq(a,p),"content_calendar_preview":[content_calendar(a,p)],"ad_keyword_plan":ad_keyword_plan(a,p),"negative_keywords":negative_keywords(a,p),"seo_meta":seo_meta(a,p)}
CMDS={"geo-plan":geo_plan,"blog-brief":blog_brief,"blog-draft":blog_draft,"landing-page":landing_page,"product-page":product_page,"service-page":service_page,"video-script":video_script,"image-prompt":image_prompt,"inquiry-reply":inquiry_reply,"faq":faq,"content-calendar":content_calendar,"prompt-pack":prompt_pack,"ad-keyword-plan":ad_keyword_plan,"negative-keywords":negative_keywords,"seo-meta":seo_meta,"product-description":product_description,"category-page":category_page,"about-us":about_us,"email-template":email_template,"social-post":social_post}

def parser():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest='command',required=True)
    def add_common(s):
        for n in ["brand","industry","country","language","product","audience","keywords","tone","market","funnel_stage","target_market","buyer_level","brief","verify_mark"]: s.add_argument(f"--{n.replace('_','-')}",dest=n)
        s.add_argument('--brand-profile',choices=['auto','veytis','juese','generic'],default='auto'); s.add_argument('--output-dir'); s.add_argument('--format',choices=['markdown','json','text','both'],default='both')
    for c in CMDS:
        s=sp.add_parser(c); add_common(s)
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
        if c=='faq': s.add_argument('--count')
        if c=='category-page': s.add_argument('--category'); s.add_argument('--product-count')
        if c=='about-us': s.add_argument('--mission'); s.add_argument('--history'); s.add_argument('--team-size')
        if c=='email-template': s.add_argument('--scenario')
        if c=='social-post': s.add_argument('--platform')
    return p

def main():
    a=parser().parse_args(); pkey=profile_key(a.brand,a.brand_profile); write_result(a.command,CMDS[a.command](a,pkey),a.output_dir,a.format)
if __name__=='__main__': main()
