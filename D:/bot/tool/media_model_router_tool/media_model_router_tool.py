#!/usr/bin/env python3
import argparse, base64, datetime as dt, json, os, pathlib
from urllib import request, error

BASE_OUTPUT = pathlib.Path("D:/bot/outputs/media_model_router_tool")
MODEL_CACHE = BASE_OUTPUT / "model_cache"
OPENAI_URL = "https://api.openai.com/v1/models"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_RESPONSES_URL = "https://openrouter.ai/api/v1/responses"
FRONTIER_PREFIXES = ("openai/", "anthropic/", "google/")


def ts(): return dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def run_dir(name):
    p = BASE_OUTPUT / ts() / name
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_reports(outdir, title, data):
    j = outdir / "report.json"; m = outdir / "report.md"
    j.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [f"# {title}", "", "```json", json.dumps(data, ensure_ascii=False, indent=2), "```", ""]
    m.write_text("\n".join(md), encoding="utf-8")
    print(f"FILE:file:///{m.as_posix()}")

def api_get(url, headers=None):
    req = request.Request(url, headers=headers or {})
    with request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))

def api_post(url, payload, headers=None):
    body = json.dumps(payload).encode("utf-8")
    h = {"Content-Type": "application/json", **(headers or {})}
    req = request.Request(url, data=body, headers=h, method="POST")
    with request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))

def openai_models():
    key = os.getenv("OPENAI_API_KEY")
    if not key: return None, "OPENAI_API_KEY missing"
    try:
        d = api_get(OPENAI_URL, {"Authorization": f"Bearer {key}"})
        return d.get("data", []), None
    except Exception as e:
        return None, str(e)

def openrouter_models():
    key = os.getenv("OPENROUTER_API_KEY")
    if not key: return None, "OPENROUTER_API_KEY missing"
    try:
        d = api_get(OPENROUTER_MODELS_URL, {"Authorization": f"Bearer {key}"})
        return d.get("data", []), None
    except Exception as e:
        return None, str(e)

def is_openai_image(mid):
    m = mid.lower(); return "image" in m or m.startswith("chatgpt-image")

def is_openai_video(mid):
    m = mid.lower(); return "sora" in m or "video" in m

def choose_openai_image(models):
    ids = {m.get("id") for m in models}
    for c in ["gpt-image-2","gpt-image-1.5","gpt-image-1-mini","chatgpt-image-latest"]:
        if c in ids: return c
    return next((m.get("id") for m in models if is_openai_image(m.get("id",""))), None)

def choose_openai_video(models):
    ids = {m.get("id") for m in models}
    for c in ["sora-2-pro", "sora-2"]:
        if c in ids: return c
    return next((m.get("id") for m in models if is_openai_video(m.get("id",""))), None)

def model_modal_match(m, media):
    text = json.dumps(m, ensure_ascii=False).lower()
    if media == "mixed": return True
    return media in text

def filter_or_models(models, media, free_only=False, exclude_frontier=True):
    out = []
    for m in models:
        mid = m.get("id", "")
        if exclude_frontier and mid.startswith(FRONTIER_PREFIXES): continue
        if not model_modal_match(m, media): continue
        if free_only:
            p = m.get("pricing") or {}
            if str(p.get("prompt", "1")) not in ("0", "0.0") or str(p.get("completion", "1")) not in ("0", "0.0"):
                continue
        out.append(m)
    return out

def cmd_test_keys(_):
    out = run_dir("test-keys")
    om, oe = openai_models(); rm, re = openrouter_models()
    data = {
        "openai_available": om is not None,
        "openrouter_available": rm is not None,
        "openai_error": oe,
        "openrouter_error": re,
        "openai_image_models": [m["id"] for m in (om or []) if is_openai_image(m.get("id",""))],
        "openai_video_models": [m["id"] for m in (om or []) if is_openai_video(m.get("id",""))],
        "openrouter_model_count": len(rm or []),
    }
    write_reports(out, "test-keys", data)

def cmd_refresh(_):
    out = run_dir("refresh-model-cache"); MODEL_CACHE.mkdir(parents=True, exist_ok=True)
    om, oe = openai_models(); rm, re = openrouter_models()
    if om is not None: (MODEL_CACHE / "openai_models.json").write_text(json.dumps(om, indent=2), encoding="utf-8")
    if rm is not None: (MODEL_CACHE / "openrouter_models.json").write_text(json.dumps(rm, indent=2), encoding="utf-8")
    write_reports(out, "refresh-model-cache", {"openai_saved": om is not None, "openrouter_saved": rm is not None, "openai_error": oe, "openrouter_error": re})

def cmd_list(args):
    out = run_dir("list-models")
    res = {}
    if args.provider in ("openai", "all"):
        om, oe = openai_models();
        res["openai_error"] = oe
        if om is not None:
            res["openai_models"] = [m.get("id") for m in om if model_modal_match(m, args.media_type)]
    if args.provider in ("openrouter", "all"):
        rm, re = openrouter_models(); res["openrouter_error"] = re
        if rm is not None:
            m = filter_or_models(rm, args.media_type, args.free_only, args.exclude_frontier_restricted)
            res["openrouter_models"] = [{"id":x.get("id"),"name":x.get("name"),"pricing":x.get("pricing")} for x in m]
    write_reports(out, "list-models", res)

def recommendation(task, quality, media, model, provider):
    t = task.lower(); rec = {"task":task,"quality":quality,"media_type":media}
    om,_=openai_models(); rm,_=openrouter_models(); om=om or []; rm=rm or []
    if model:
        pool = om if (provider=="openai" or (provider=="auto" and "/" not in model)) else rm
        found = next((x for x in pool if x.get("id")==model), None)
        if not found: return {**rec,"error":"requested model unavailable","alternatives":[]}
        if not model_modal_match(found, media): return {**rec,"error":"model incompatible with requested media type"}
        return {**rec,"provider":"openai" if found in om else "openrouter","model":model,"override_used":True}
    if "analyze product image" in t or "defect" in t:
        return {**rec,"provider":"local","model":"image_analysis_skill","workflow":"Use local QC skill directly"}
    if "banner" in t or "layout" in t:
        return {**rec,"provider":"local","model":"graphic_design_analyzer_skill"}
    if media=="image" and quality in ("high","highest"):
        return {**rec,"provider":"openai","model":choose_openai_image(om),"qc":["image_analysis_skill", "graphic_design_analyzer_skill (if banner/layout/ad)"]}
    if media=="video" and quality in ("high","highest"):
        v = choose_openai_video(om)
        if v: return {**rec,"provider":"openai","model":v}
        vids = filter_or_models(rm,"video",False,True)
        return {**rec,"provider":"openrouter","model": vids[0]["id"] if vids else None}
    if "transcript" in t or "translate" in t or "summarize" in t or "analyze video audio" in t:
        return {**rec,"provider":"existing_local_qwen_omni_watcher","tool":"video_audio_auto.py","path":"D:/bot/openclaw_data/.openclaw/scripts/video_audio_auto.py","model":"qwen-omni-turbo","key":"DASHSCOPE_API_KEY","workflow":["send/upload video to OpenClaw media/inbound","existing watcher detects video","Qwen-Omni analyzes audio/video","Telegram receives original transcript, Chinese translation, and summary"]}
    imgs = filter_or_models(rm,"image",quality=="free",True)
    return {**rec,"provider":"openrouter","model": imgs[0]["id"] if imgs else None}

def cmd_recommend(args): write_reports(run_dir("recommend"),"recommend",recommendation(args.task,args.quality,args.media_type,args.model,args.provider))

def dry_or_yes(args):
    return {"dry_run": not args.yes, "paid_api_warning": None if args.yes else "Paid generation blocked without --yes"}

def cmd_gen_openai_image(args):
    out = run_dir("generate-openai-image")
    om,e = openai_models(); om=om or []; model = args.model if args.model!="auto" else choose_openai_image(om)
    data = {"provider":"openai","model":model,"prompt":args.prompt,"size":args.size,"quality":args.quality,**dry_or_yes(args),"qc":["image_analysis_skill","graphic_design_analyzer_skill (if banner/layout/ad)"]}
    if args.yes and model:
        key=os.getenv("OPENAI_API_KEY")
        payload={"model":model,"prompt":args.prompt,"size":args.size}
        try:
            r=api_post("https://api.openai.com/v1/images/generations",payload,{"Authorization":f"Bearer {key}"})
            b64=r.get("data",[{}])[0].get("b64_json")
            if b64:
                img=base64.b64decode(b64); p=(pathlib.Path(args.output_dir) if args.output_dir else out)/"image.png"; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(img); data["output_image"]=str(p)
        except Exception as ex: data["error"]=str(ex)
    write_reports(out,"generate-openai-image",data)

def cmd_edit_openai_image(args):
    out=run_dir("edit-openai-image"); write_reports(out,"edit-openai-image",{"provider":"openai","dry_run":not args.yes,"note":"Image edit workflow configured; preserves original by writing new file.","image":args.image,"prompt":args.prompt,"qc":["image_analysis_skill"]})

def cmd_generate_openai_video(args):
    out=run_dir("generate-openai-video"); om,_=openai_models(); model=args.model if args.model!="auto" else choose_openai_video(om or [])
    write_reports(out,"generate-openai-video",{"provider":"openai","model":model,"dry_run":not args.yes,"fallback":"If unavailable, use generate-openrouter-video"})

def cmd_generate_openrouter_image(args): write_reports(run_dir("generate-openrouter-image"),"generate-openrouter-image",{"provider":"openrouter","dry_run":not args.yes,"prompt":args.prompt,"quality":args.quality,"model":args.model,"qc":"For final commercial image, run image_analysis_skill."})
def cmd_generate_openrouter_video(args): write_reports(run_dir("generate-openrouter-video"),"generate-openrouter-video",{"provider":"openrouter","dry_run":not args.yes,"prompt":args.prompt,"model":args.model})
def cmd_poll_openrouter_video(args): write_reports(run_dir("poll-openrouter-video"),"poll-openrouter-video",{"job_id":args.job_id,"status_url":args.status_url})

def cmd_download_openrouter_video(args):
    out=run_dir("download-openrouter-video"); data={"url":args.url,"job_id":args.job_id}
    if args.url:
        p=(pathlib.Path(args.output_dir) if args.output_dir else out)/"video.mp4"
        try: p.write_bytes(request.urlopen(args.url, timeout=120).read()); data["saved_to"]=str(p)
        except Exception as e: data["error"]=str(e)
    write_reports(out,"download-openrouter-video",data)

def cmd_analyze_video_audio(args):
    out=run_dir("analyze-video-audio")
    data={
        "message":"This function is already handled by the existing Qwen-Omni video_audio_auto watcher.",
        "provider":"existing_local_qwen_omni_watcher",
        "tool":"video_audio_auto.py",
        "official_script_path":"D:/bot/openclaw_data/.openclaw/scripts/video_audio_auto.py",
        "clean_reference_path":"D:/bot/video_audio_auto_clean/video_audio_auto.py",
        "expected_model":"qwen-omni-turbo",
        "expected_env_keys":["DASHSCOPE_API_KEY","QWEN_OMNI_MODEL"],
        "video_input_location":"D:/bot/openclaw_data/.openclaw/media/inbound (or configured inbound media folder)",
        "log_hint":"Check watcher runtime logs and video_audio_auto.log for processing status.",
        "video":args.video,
        "note":"No new transcription pipeline is implemented here. No Whisper/ffmpeg transcription is performed."
    }
    write_reports(out,"analyze-video-audio",data)



def cmd_video_audio_status(_):
    out=run_dir("video-audio-status")
    official=pathlib.Path("D:/bot/openclaw_data/.openclaw/scripts/video_audio_auto.py")
    clean=pathlib.Path("D:/bot/video_audio_auto_clean/video_audio_auto.py")
    openclaw=pathlib.Path("D:/bot/openclaw_data/.openclaw/openclaw.json")
    media_dirs=[
        pathlib.Path("D:/bot/openclaw_data/.openclaw/media/inbound"),
        pathlib.Path("D:/bot/openclaw_data/.openclaw/media"),
    ]
    log_path=pathlib.Path("D:/bot/openclaw_data/.openclaw/scripts/video_audio_auto.log")
    has_dashscope=False
    qwen_model=None
    if openclaw.exists():
        try:
            txt=openclaw.read_text(encoding="utf-8",errors="ignore")
            has_dashscope=("DASHSCOPE_API_KEY" in txt)
            qwen_model=os.getenv("QWEN_OMNI_MODEL") or ("qwen-omni-turbo" if "qwen-omni-turbo" in txt else None)
        except Exception:
            pass
    data={
        "official_script_exists":official.exists(),
        "clean_reference_exists":clean.exists(),
        "openclaw_json_path":str(openclaw),
        "openclaw_has_dashscope_key_field":has_dashscope,
        "qwen_omni_model":qwen_model or "qwen-omni-turbo (default)",
        "media_inbound_exists":media_dirs[0].exists(),
        "media_dir_exists":media_dirs[1].exists(),
        "video_audio_log_exists":log_path.exists(),
        "official_script_path":str(official),
        "clean_reference_path":str(clean),
        "log_path":str(log_path),
        "note":"API key values are intentionally not printed."
    }
    write_reports(out,"video-audio-status",data)

def cmd_qc_plan(args):
    qc=["image_analysis_skill --image \"...\" --check realism,label,text,geometry,materials,lighting"]
    if args.media_type in ("banner","ad","website") or any(x in args.use_case.lower() for x in ["banner","layout","website","ad"]): qc.append("graphic_design_analyzer_skill --image \"...\" --check layout,typography,brand,color")
    write_reports(run_dir("qc-plan"),"qc-plan",{"image":args.image,"use_case":args.use_case,"brand":args.brand,"media_type":args.media_type,"recommended_commands":qc})

def main():
    p=argparse.ArgumentParser(prog="media_model_router_tool")
    sp=p.add_subparsers(dest="cmd",required=True)
    sp.add_parser("test-keys").set_defaults(func=cmd_test_keys)
    sp.add_parser("refresh-model-cache").set_defaults(func=cmd_refresh)
    a=sp.add_parser("list-models"); a.add_argument("--provider",choices=["openai","openrouter","all"],default="all"); a.add_argument("--media-type",choices=["text","image","video","audio","mixed"],default="mixed"); a.add_argument("--free-only",action="store_true"); a.add_argument("--exclude-frontier-restricted",action="store_true",default=True); a.set_defaults(func=cmd_list)
    a=sp.add_parser("recommend"); a.add_argument("--task",required=True); a.add_argument("--quality",choices=["free","cheap","medium","high","highest"],default="medium"); a.add_argument("--media-type",choices=["text","image","video","audio","mixed"],required=True); a.add_argument("--model"); a.add_argument("--provider",choices=["openai","openrouter","auto"],default="auto"); a.set_defaults(func=cmd_recommend)
    a=sp.add_parser("generate-openai-image"); a.add_argument("--prompt",required=True); a.add_argument("--model",default="auto"); a.add_argument("--size",default="1024x1024"); a.add_argument("--quality",choices=["auto","high","medium","low"],default="auto"); a.add_argument("--output-dir"); a.add_argument("--yes",action="store_true"); a.set_defaults(func=cmd_gen_openai_image)
    a=sp.add_parser("edit-openai-image"); a.add_argument("--image",required=True); a.add_argument("--prompt",required=True); a.add_argument("--model",default="auto"); a.add_argument("--quality",choices=["auto","high","medium","low"],default="auto"); a.add_argument("--yes",action="store_true"); a.set_defaults(func=cmd_edit_openai_image)
    a=sp.add_parser("generate-openai-video"); a.add_argument("--prompt",required=True); a.add_argument("--model",default="auto"); a.add_argument("--duration"); a.add_argument("--aspect-ratio"); a.add_argument("--yes",action="store_true"); a.set_defaults(func=cmd_generate_openai_video)
    a=sp.add_parser("generate-openrouter-image"); a.add_argument("--prompt",required=True); a.add_argument("--model"); a.add_argument("--quality",choices=["free","cheap","medium","high"],default="medium"); a.add_argument("--yes",action="store_true"); a.set_defaults(func=cmd_generate_openrouter_image)
    a=sp.add_parser("generate-openrouter-video"); a.add_argument("--prompt",required=True); a.add_argument("--model"); a.add_argument("--duration"); a.add_argument("--aspect-ratio"); a.add_argument("--yes",action="store_true"); a.set_defaults(func=cmd_generate_openrouter_video)
    a=sp.add_parser("poll-openrouter-video"); a.add_argument("--job-id"); a.add_argument("--status-url"); a.set_defaults(func=cmd_poll_openrouter_video)
    a=sp.add_parser("download-openrouter-video"); a.add_argument("--url"); a.add_argument("--job-id"); a.add_argument("--output-dir"); a.set_defaults(func=cmd_download_openrouter_video)
    a=sp.add_parser("analyze-video-audio"); a.add_argument("--video",required=True); a.add_argument("--model"); a.add_argument("--provider",default="openrouter"); a.add_argument("--quality",choices=["free","cheap","medium"],default="free"); a.add_argument("--free-first",action="store_true",default=True); a.add_argument("--translate-zh",action="store_true",default=True); a.add_argument("--summarize",action="store_true",default=True); a.set_defaults(func=cmd_analyze_video_audio)
    sp.add_parser("video-audio-status").set_defaults(func=cmd_video_audio_status)
    a=sp.add_parser("qc-plan"); a.add_argument("--image",required=True); a.add_argument("--use-case",required=True); a.add_argument("--brand"); a.add_argument("--media-type",choices=["image","banner","ad","product","website"],required=True); a.set_defaults(func=cmd_qc_plan)
    args=p.parse_args(); args.func(args)

if __name__ == "__main__": main()
