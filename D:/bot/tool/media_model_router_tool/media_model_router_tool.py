#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, datetime as dt, json, os, re
from pathlib import Path
from urllib import request

OUT_ROOT=Path('D:/bot/outputs/media_model_router')
DASHSCOPE_CATALOG=[
 {'id':'qwen-vl-plus','provider':'dashscope','input_modalities':['text','image'],'output_modalities':['text']},
 {'id':'qwen-vl-max','provider':'dashscope','input_modalities':['text','image'],'output_modalities':['text']},
 {'id':'qwen-omni-turbo','provider':'dashscope','input_modalities':['text','image','audio','video'],'output_modalities':['text']},
 {'id':'qwen-plus','provider':'dashscope','input_modalities':['text'],'output_modalities':['text']},
 {'id':'qwen-flash','provider':'dashscope','input_modalities':['text'],'output_modalities':['text']},
 {'id':'deepseek-v4-pro','provider':'dashscope','input_modalities':['text'],'output_modalities':['text']},
]


def now_dir():
 d=OUT_ROOT/dt.datetime.now().strftime('%Y%m%d-%H%M%S'); d.mkdir(parents=True,exist_ok=True); return d

def report(name,data):
 od=now_dir(); md=od/f'{name}.md'; js=od/f'{name}.json'; js.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); md.write_text('# Report\n\n```json\n'+json.dumps(data,ensure_ascii=False,indent=2)+'\n```',encoding='utf-8'); print(f'FILE:file:///{md.as_posix()}')

def fetch_openrouter():
 try:
  with request.urlopen('https://openrouter.ai/api/v1/models',timeout=30) as r: d=json.loads(r.read().decode('utf-8','ignore')).get('data',[])
  out=[]
  for m in d:
   inp=list(set((m.get('architecture',{}).get('input_modalities') or [])+(m.get('input_modalities') or []))); outm=list(set((m.get('architecture',{}).get('output_modalities') or [])+(m.get('output_modalities') or [])))
   out.append({'id':m.get('id'),'name':m.get('name'),'provider':'openrouter','pricing':m.get('pricing',{}),'input_modalities':inp,'output_modalities':outm,'raw':m})
  return out,None
 except Exception as e: return [],str(e)

def fetch_openai():
 k=os.getenv('OPENAI_API_KEY','')
 if not k: return [],'missing OPENAI_API_KEY'
 try:
  req=request.Request('https://api.openai.com/v1/models',headers={'Authorization':f'Bearer {k}'})
  with request.urlopen(req,timeout=30) as r: d=json.loads(r.read().decode('utf-8','ignore')).get('data',[])
  out=[]
  for m in d:
   mid=m.get('id',''); im=['text'];
   if any(x in mid for x in ['gpt-4.1','gpt-4o','vision']): im=['text','image']
   out.append({'id':mid,'name':mid,'provider':'openai','pricing':{},'input_modalities':im,'output_modalities':['text'],'raw':m})
  return out,None
 except Exception as e: return [],str(e)

def fetch_dashscope():
 return DASHSCOPE_CATALOG,None

def fetch_deepseek():
 return [{'id':'deepseek-chat','name':'deepseek-chat','provider':'deepseek','input_modalities':['text'],'output_modalities':['text'],'pricing':{}},{'id':'deepseek-reasoner','name':'deepseek-reasoner','provider':'deepseek','input_modalities':['text'],'output_modalities':['text'],'pricing':{}}],None

def fetch_local():
 m=os.getenv('LOCAL_VISION_MODEL','local-model')
 return [{'id':m,'name':m,'provider':'local','input_modalities':['text','image'],'output_modalities':['text'],'pricing':{}}],None

def get_models(provider):
 sources=[]
 if provider in ['openrouter','all','auto']: sources.append(fetch_openrouter())
 if provider in ['dashscope','all','auto']: sources.append(fetch_dashscope())
 if provider in ['openai','all','auto']: sources.append(fetch_openai())
 if provider in ['deepseek','all','auto']: sources.append(fetch_deepseek())
 if provider in ['local','all','auto']: sources.append(fetch_local())
 models=[]; errs=[]
 for ms,er in sources:
  models.extend(ms)
  if er: errs.append(er)
 return models,errs

def supports(m, media):
 im=set(m.get('input_modalities') or []); om=set(m.get('output_modalities') or [])
 if media=='image': return 'image' in im
 if media=='video': return 'video' in im
 if media=='audio': return 'audio' in im
 if media=='generation': return 'image' in om or 'video' in om
 if media=='text': return 'text' in im
 return True

def resolve(request_text, media, quality, provider):
 req=request_text.lower(); forced=provider if provider!='auto' else None
 if 'openrouter' in req or 'glm-4.5v' in req: forced='openrouter'
 if any(x in req for x in ['百炼','dashscope','千问','qwen-vl']): forced='dashscope'
 if 'openai' in req: forced='openai'
 if 'deepseek' in req: forced='deepseek'
 if '本地' in req or 'local' in req: forced='local'
 models,errs=get_models(forced or 'all')
 tokens=re.findall(r'[a-z0-9][a-z0-9._/-]*',req)
 exact=None
 for m in models:
  mid=(m.get('id') or '').lower()
  if mid and (mid in req or mid in tokens): exact=m; break
 cand=models
 if exact: cand=[exact]
 if '免费' in req or quality=='free': cand=[m for m in cand if m.get('provider')=='openrouter' and float(str(m.get('pricing',{}).get('prompt',0) or 0))==0 and float(str(m.get('pricing',{}).get('completion',0) or 0))==0]
 cand=[m for m in cand if supports(m,media)]
 if '最便宜' in req or quality=='cheap': cand=sorted(cand,key=lambda m:(float(str(m.get('pricing',{}).get('prompt',0) or 0)),float(str(m.get('pricing',{}).get('completion',0) or 0))))
 if '最强' in req or quality in ['high','best']: cand=sorted(cand,key=lambda m:len(m.get('id','')),reverse=True)
 if 'glm-4.5v' in req and not exact:
  hit=[m for m in models if (m.get('id') or '').lower()=='z-ai/glm-4.5v']
  if hit and supports(hit[0],media): cand=[hit[0]]+cand
 if any(x in req for x in ['百炼','千问','qwen-vl']) and not exact:
  hit=[m for m in models if m.get('provider')=='dashscope' and m.get('id')=='qwen-vl-plus']
  if hit and supports(hit[0],media): cand=[hit[0]]+cand
 if forced=='deepseek' and media=='image':
  return {'requested_intent':request_text,'resolved_provider':'deepseek','resolved_model':'deepseek-chat','model_available':True,'supports_media_type':False,'reason':'DeepSeek 当前主要文本模型','alternatives':['dashscope/qwen-vl-plus','openrouter/z-ai/glm-4.5v'],'blocked_reason':'model does not support image input','errors':errs}
 if not cand:
  return {'requested_intent':request_text,'resolved_provider':forced or 'auto','resolved_model':None,'model_available':False,'supports_media_type':False,'reason':'no model meeting constraints','alternatives':[m.get('id') for m in models[:10]],'blocked_reason':('; '.join(errs) if errs else None),'errors':errs}
 b=cand[0]
 return {'requested_intent':request_text,'resolved_provider':b.get('provider'),'resolved_model':b.get('id'),'model_available':True,'supports_media_type':True,'reason':'resolved by intent and filters','alternatives':[m.get('id') for m in cand[1:10]],'blocked_reason':None,'errors':errs}

def call_vision(image, reqtxt, provider, model, quality):
 r=resolve(reqtxt,'image',quality,provider)
 if model: r.update({'resolved_model':model,'resolved_provider':provider if provider!='auto' else r.get('resolved_provider')})
 if not r.get('resolved_model'): return {'error':'unresolved_model','resolve':r}
 rp=r['resolved_provider']; m=r['resolved_model']
 if rp=='local':
  key=os.getenv('LOCAL_VISION_API_KEY','lm-studio'); base=os.getenv('LOCAL_VISION_BASE_URL','http://127.0.0.1:1234/v1')
 elif rp=='dashscope':
  key=os.getenv('DASHSCOPE_API_KEY',''); base='https://dashscope.aliyuncs.com/compatible-mode/v1'
 elif rp=='openai':
  key=os.getenv('OPENAI_API_KEY',''); base='https://api.openai.com/v1'
 else:
  key=os.getenv('OPENROUTER_API_KEY',''); base='https://openrouter.ai/api/v1'
 if not key and rp!='local': return {'error':f'missing_api_key_for_{rp}','resolve':r}
 data_url='data:image/jpeg;base64,'+__import__('base64').b64encode(Path(image).read_bytes()).decode('ascii')
 payload={'model':m,'messages':[{'role':'user','content':[{'type':'text','text':reqtxt},{'type':'image_url','image_url':{'url':data_url}}]}]}
 try:
  req=request.Request(base.rstrip('/')+'/chat/completions',data=json.dumps(payload).encode('utf-8'),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
  with request.urlopen(req,timeout=90) as rr: d=json.loads(rr.read().decode('utf-8','ignore'))
  txt=((d.get('choices') or [{}])[0].get('message') or {}).get('content','')
  return {'provider':rp,'model':m,'semantic_analysis':txt,'resolve':r}
 except Exception as e:
  return {'error':'provider_call_failed','reason':str(e),'provider':rp,'model':m,'resolve':r}

def main():
 p=argparse.ArgumentParser(description='Unified multi-provider model router')
 sp=p.add_subparsers(dest='cmd',required=True)
 a1=sp.add_parser('list-models'); a1.add_argument('--provider',default='all',choices=['openrouter','dashscope','openai','deepseek','local','all']); a1.add_argument('--media-type',default='mixed',choices=['text','image','video','audio','generation','mixed']); a1.add_argument('--free-only',action='store_true'); a1.add_argument('--query')
 a2=sp.add_parser('resolve-model'); a2.add_argument('--request',required=True); a2.add_argument('--media-type',default='text',choices=['text','image','video','audio','mixed']); a2.add_argument('--quality',default='medium',choices=['free','cheap','medium','high','best']); a2.add_argument('--provider',default='auto',choices=['auto','openrouter','dashscope','openai','deepseek','local'])
 a3=sp.add_parser('call-vision'); a3.add_argument('--image',required=True); a3.add_argument('--request',required=True); a3.add_argument('--provider',default='auto',choices=['auto','openrouter','dashscope','openai','local']); a3.add_argument('--model'); a3.add_argument('--quality',default='medium',choices=['free','cheap','medium','high','best'])
 a4=sp.add_parser('recommend-model'); a4.add_argument('--task',required=True); a4.add_argument('--media-type',default='text',choices=['text','image','video','audio','mixed']); a4.add_argument('--quality',default='medium',choices=['free','cheap','medium','high','best']); a4.add_argument('--provider',default='auto',choices=['auto','openrouter','dashscope','openai','deepseek','local'])
 a=p.parse_args()
 if a.cmd=='list-models':
  ms,errs=get_models(a.provider); out=[m for m in ms if (a.media_type=='mixed' or supports(m,a.media_type)) and (not a.query or a.query.lower() in (m.get('id') or '').lower()) and (not a.free_only or (m.get('provider')=='openrouter' and float(str(m.get('pricing',{}).get('prompt',0) or 0))==0 and float(str(m.get('pricing',{}).get('completion',0) or 0))==0))]; report('list-models',{'provider':a.provider,'count':len(out),'errors':errs,'models':out})
 elif a.cmd=='resolve-model': report('resolve-model',resolve(a.request,a.media_type,a.quality,a.provider))
 elif a.cmd=='recommend-model': report('recommend-model',resolve(a.task,a.media_type,a.quality,a.provider))
 else: report('call-vision',call_vision(a.image,a.request,a.provider,a.model,a.quality))

if __name__=='__main__': main()
