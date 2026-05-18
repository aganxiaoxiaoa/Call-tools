#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, datetime as dt, json, os, re
from pathlib import Path
from urllib import request

OUT_ROOT=Path('D:/bot/outputs/media_model_router')
OPENROUTER_MODELS_URL='https://openrouter.ai/api/v1/models'
OPENROUTER_CHAT_URL='https://openrouter.ai/api/v1/chat/completions'

PROVIDER_ALIASES={
 'z.ai':'z-ai/','glm':'z-ai/','qwen':'qwen/','deepseek':'deepseek/','minimax':'minimax/','llama':'meta-llama/',
 'mistral':'mistralai/','openai':'openai/','claude':'anthropic/','anthropic':'anthropic/','gemini':'google/','google':'google/'
}


def now_dir(base):
    d=Path(base)/dt.datetime.now().strftime('%Y%m%d-%H%M%S'); d.mkdir(parents=True,exist_ok=True); return d

def file_uri(p): return f'FILE:file:///{Path(p).as_posix()}'

def load_models():
    try:
        with request.urlopen(OPENROUTER_MODELS_URL, timeout=30) as r:
            data=json.loads(r.read().decode('utf-8','ignore'))
        return data.get('data',[]), None
    except Exception as e:
        return [], str(e)

def modalities(m):
    inp=set((m.get('architecture',{}).get('input_modalities') or []) + (m.get('input_modalities') or []))
    out=set((m.get('architecture',{}).get('output_modalities') or []) + (m.get('output_modalities') or []))
    return inp,out

def supports_media(m, media):
    inp,out=modalities(m)
    if media in ('image','vision'): return 'image' in inp
    if media=='video': return 'video' in inp
    if media=='audio': return 'audio' in inp
    if media=='generation': return ('image' in out) or ('video' in out)
    if media=='text': return 'text' in inp
    return True

def price_num(v):
    try: return float(str(v or '0'))
    except: return 999999.0

def is_free(m):
    p=m.get('pricing',{})
    return price_num(p.get('prompt'))==0 and price_num(p.get('completion'))==0

def filter_models(models, task='all', free_only=False, prefix=None, query=None):
    out=[]
    for m in models:
        mid=m.get('id','')
        if prefix and not mid.startswith(prefix): continue
        if query and (query.lower() not in mid.lower() and query.lower() not in (m.get('name') or '').lower()): continue
        if task!='all' and not supports_media(m,task): continue
        if free_only and not is_free(m): continue
        out.append(m)
    return out

def intent_to_prefix(req):
    low=req.lower()
    for k,v in PROVIDER_ALIASES.items():
        if k in low: return v
    return None

def resolve_model(models, req, media_type, quality, provider='openrouter'):
    low=req.lower(); exact=None
    for m in models:
        mid=m.get('id','').lower()
        if mid in low or re.search(r'\b'+re.escape(mid)+r'\b', low): exact=m; break
    prefix=intent_to_prefix(req)
    cand=models
    if prefix: cand=[m for m in cand if m.get('id','').startswith(prefix)]
    cand=[m for m in cand if supports_media(m, media_type)]
    if '免费' in req or 'free' in low or quality=='free':
        cand=[m for m in cand if is_free(m)]
    if exact:
        ok=supports_media(exact, media_type)
        return {'requested_intent':req,'resolved_provider':'openrouter','resolved_model':exact.get('id'),'model_available':True,'supports_media_type':ok,'reason':'exact model match','alternatives':[m.get('id') for m in cand[:8]],'blocked_reason':None if ok else f"model does not support {media_type} input"}
    if '最便宜' in req or 'cheap' in low or quality=='cheap':
        cand=sorted(cand,key=lambda m:(price_num(m.get('pricing',{}).get('prompt')),price_num(m.get('pricing',{}).get('completion'))))
    elif ('最强' in req or 'best' in low or quality in ('high','best')):
        blocked=('openai/' in ''.join([m.get('id','') for m in cand])) and any(x in low for x in ['限制','blocked','region'])
        if blocked:
            cand=[m for m in cand if not (m.get('id','').startswith('openai/') or m.get('id','').startswith('anthropic/') or m.get('id','').startswith('google/'))]
        cand=sorted(cand,key=lambda m: int(m.get('context_length') or 0), reverse=True)
    if not cand:
        fuzzy=[m.get('id') for m in models if any(t in m.get('id','').lower() for t in re.findall(r'[a-z0-9\.-]+',low))][:10]
        return {'requested_intent':req,'resolved_provider':'openrouter','resolved_model':None,'model_available':False,'supports_media_type':False,'reason':'no matched model','alternatives':fuzzy,'blocked_reason':'no model meeting constraints'}
    best=cand[0]
    return {'requested_intent':req,'resolved_provider':'openrouter','resolved_model':best.get('id'),'model_available':True,'supports_media_type':True,'reason':'resolved by intent/filters','alternatives':[m.get('id') for m in cand[1:9]],'blocked_reason':None}

def report(name,data):
    od=now_dir(OUT_ROOT); js=od/f'{name}.json'; md=od/f'{name}.md'
    js.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    md.write_text('# Report\n\n```json\n'+json.dumps(data,ensure_ascii=False,indent=2)+'\n```',encoding='utf-8')
    print(file_uri(md))

def cmd_list(a):
    ms,err=load_models(); rows=[]
    if err:
        return report('list-openrouter-models',{'error':'models_fetch_failed','reason':err,'models':[]})
    for m in filter_models(ms,a.task,a.free_only,a.provider_prefix,a.query):
        inp,out=modalities(m)
        rows.append({'id':m.get('id'),'name':m.get('name'),'pricing':m.get('pricing',{}),'input_modalities':sorted(inp),'output_modalities':sorted(out)})
    report('list-openrouter-models',{'count':len(rows),'models':rows})

def cmd_resolve(a):
    ms,err=load_models()
    if err:
        return report('resolve-model',{'requested_intent':a.request,'resolved_provider':'openrouter','resolved_model':None,'model_available':False,'supports_media_type':False,'reason':'models_fetch_failed','alternatives':[],'blocked_reason':err})
    r=resolve_model(ms,a.request,a.media_type,a.quality,a.provider); report('resolve-model',r)

def cmd_recommend(a):
    ms,err=load_models()
    if err:
        return report('recommend-openrouter-model',{'requested_intent':a.task,'resolved_provider':'openrouter','resolved_model':None,'model_available':False,'supports_media_type':False,'reason':'models_fetch_failed','alternatives':[],'blocked_reason':err})
    r=resolve_model(ms,a.task,a.media_type,a.quality,'openrouter'); report('recommend-openrouter-model',r)

def call_openrouter_vision(image_path, model, req_text):
    api_key=os.getenv('OPENROUTER_API_KEY','')
    if not api_key: return {'error':'missing OPENROUTER_API_KEY'}
    data_url='data:image/jpeg;base64,'+__import__('base64').b64encode(Path(image_path).read_bytes()).decode('ascii')
    payload={'model':model,'messages':[{'role':'user','content':[{'type':'text','text':req_text},{'type':'image_url','image_url':{'url':data_url}}]}]}
    req=request.Request(OPENROUTER_CHAT_URL,data=json.dumps(payload).encode('utf-8'),headers={'Authorization':f'Bearer {api_key}','Content-Type':'application/json'})
    with request.urlopen(req,timeout=90) as r:
        data=json.loads(r.read().decode('utf-8','ignore'))
    txt=((data.get('choices') or [{}])[0].get('message') or {}).get('content','')
    return {'model':model,'semantic_analysis':txt,'raw':data}

def cmd_call(a):
    ms,err=load_models()
    if err:
        return report('call-openrouter-vision',{'error':'models_fetch_failed','reason':err})
    chosen=a.model or resolve_model(ms,a.request,'image',a.quality,'openrouter').get('resolved_model')
    mm=next((m for m in ms if m.get('id')==chosen),None)
    if not mm:
        return report('call-openrouter-vision',{'error':'model not found','model':chosen})
    if not supports_media(mm,'image'):
        return report('call-openrouter-vision',{'error':'model does not support image input','model':chosen})
    out=call_openrouter_vision(a.image,chosen,a.request)
    report('call-openrouter-vision',out)

def main():
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest='cmd',required=True)
    s1=sp.add_parser('list-openrouter-models'); s1.add_argument('--task',default='all',choices=['text','image','vision','video','audio','generation','all']); s1.add_argument('--free-only',action='store_true'); s1.add_argument('--provider-prefix'); s1.add_argument('--query')
    s2=sp.add_parser('resolve-model'); s2.add_argument('--request',required=True); s2.add_argument('--media-type',default='text',choices=['text','image','video','audio','mixed']); s2.add_argument('--quality',default='medium',choices=['free','cheap','medium','high','best']); s2.add_argument('--provider',default='openrouter',choices=['openrouter','openai','auto'])
    s3=sp.add_parser('call-openrouter-vision'); s3.add_argument('--image',required=True); s3.add_argument('--request',required=True); s3.add_argument('--model'); s3.add_argument('--quality',default='medium',choices=['free','cheap','medium','high','best'])
    s4=sp.add_parser('recommend-openrouter-model'); s4.add_argument('--task',required=True); s4.add_argument('--media-type',default='text',choices=['text','image','video','audio','mixed']); s4.add_argument('--quality',default='medium',choices=['free','cheap','medium','high','best'])
    a=p.parse_args()
    {'list-openrouter-models':cmd_list,'resolve-model':cmd_resolve,'call-openrouter-vision':cmd_call,'recommend-openrouter-model':cmd_recommend}[a.cmd](a)

if __name__=='__main__': main()
