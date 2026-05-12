#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, json, re, sys, subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

STORE_ROOT = Path(r"D:\bot\store")
TOOL_ROOT = Path(r"D:\bot\tool")
TOOLS_ROOT = Path(r"D:\bot\tools")
WORKSPACE = Path(r"C:\Users\Administrator\.openclaw\workspace")
SKILLS = Path(r"C:\Users\Administrator\.openclaw\workspace\skills")

DANGEROUS = ["CleanSafe", "Remove-Item", "del ", "rmdir", "format", "taskkill", "Stop-Process", "git reset", "git clean"]


def ts(fmt="%Y%m%d_%H%M%S"): return datetime.now().strftime(fmt)
def ensure(p: Path): p.mkdir(parents=True, exist_ok=True)
def jdump(path: Path, data): ensure(path.parent); path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def jload(path: Path, default):
    try: return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception: return default

def jl_append(path: Path, obj): ensure(path.parent); path.open("a", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False)+"\n")
def jl_read(path: Path):
    out=[]
    if not path.exists(): return out
    for l in path.read_text(encoding="utf-8").splitlines():
        l=l.strip()
        if not l: continue
        try: out.append(json.loads(l))
        except Exception: pass
    return out


def default_tools():
    return {"tools":[
        {"name":"image_analysis_tool","description":"通用图片分析","candidate_paths":[r"D:\bot\tool\image_analysis_skill\image_analysis_tool.py"],"command_examples":[r'py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --help'],"intents":["图片分析","风格分析"],"risk_level":"low","requires_media":True,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},
        {"name":"graphic_design_tool","description":"平面设计/排版分析","candidate_paths":[r"D:\bot\tool\graphic_design_analyzer_skill\graphic_design_tool.py"],"command_examples":[r'py "D:\bot\tool\graphic_design_analyzer_skill\graphic_design_tool.py" --help'],"intents":["平面设计","排版"],"risk_level":"low","requires_media":True,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},
        {"name":"facefusion_swap","description":"人脸替换","candidate_paths":[r"D:\bot\tool\FaceFusion tools\facefusion_swap.py"],"command_examples":[r'py "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --help'],"intents":["face swap"],"risk_level":"medium","requires_media":True,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},
        {"name":"b2b_marketing_tool","description":"B2B营销内容","candidate_paths":[r"D:\bot\tool\Business tools\b2b_marketing_tool.py"],"command_examples":[r'py "D:\bot\tool\Business tools\b2b_marketing_tool.py" --help'],"intents":["GEO","SEO","博客","落地页"],"risk_level":"low","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},
        {"name":"content_ops","description":"内容运营CLI","candidate_paths":[r"D:\bot\tool\content-ops"],"command_examples":[r'"D:\bot\tool\content-ops" --help'],"intents":["内容运营"],"risk_level":"low","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},
        {"name":"disk_cleaner","description":"磁盘扫描清理","candidate_paths":[r"D:\bot\tool\Cleaning tools\disk_cleaner.ps1"],"command_examples":[r'powershell -File "D:\bot\tool\Cleaning tools\disk_cleaner.ps1" -WhatIf'],"intents":["磁盘维护"],"risk_level":"high","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":True},
        {"name":"agent_control_center","description":"路由/自检/防幻觉","candidate_paths":[r"D:\bot\tool\agent_control_center_skill\agent_control_center.py"],"command_examples":[r'py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" --help'],"intents":["路由","自检"],"risk_level":"low","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},
        {"name":"autopilot_operator","description":"自动化任务执行","candidate_paths":[r"D:\bot\tool\autopilot_operator_skill\autopilot_operator.py"],"command_examples":[r'py "D:\bot\tool\autopilot_operator_skill\autopilot_operator.py" --help'],"intents":["自动执行","任务管家"],"risk_level":"medium","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False}
    ]}

def seed():
    return {
      "store_root": str(STORE_ROOT), "version":"2.0.0",
      "user_profile":{"name":"唐文广","language":"Chinese","environment":"Windows + OpenClaw + Telegram","working_style":"step_by_step, practical, path_sensitive","safety_preferences":["check_before_execute","no_dangerous_delete_without_confirmation","codex_writes_code_when_requested","use_existing_codex_tools_not_rewrite"]},
      "business_profile":{"domains":["international_b2b_independent_site_operations","geo_seo","blog_writing","image_generation","video_generation","customer_inquiry_reply","product_page_copy","tool_automation"]},
      "brand_profiles":{"brands":[{"name":"Juese Clothing","directions":["服装工厂","定制服装","批发服装","OEM/ODM","样衣","印花","刺绣","质检","B2B garment factory"],"tasks":["custom clothing manufacturer 页面文案","custom hoodie manufacturer 短视频脚本","garment factory production floor 图片提示词","服装工厂图片分析","平面设计/广告图分析","客户询盘英文回复","Google Ads / GEO / SEO 内容规划"]},{"name":"Veytis","directions":["精油","纯露","香薰原料","B2B 批发","private label","bulk essential oils","hydrosol supplier"],"tasks":["bulk essential oils GEO 内容","private label essential oils 产品页","hydrosol supplier 博客","精油产品图提示词","产品图色彩/构图/真实感分析","B2B FAQ","客户询盘英文回复"]}]},
      "preferences":{"rules":["不要自己直接写代码，让 Codex 写","用 Codex 创建的工具，不要重写","路径必须准确","先检查再执行","不要乱删文件","付费 API 先提醒","输出中文","路径有空格必须加引号"]},
      "anti_hallucination_rules":["do_not_claim_file_exists_without_check","do_not_claim_done_without_evidence","do_not_repeat_failed_command","do_not_treat_pr_page_as_local_file","do_not_treat_github_merge_as_local_install","raw_404_means_file_not_found_or_private_or_not_merged","quote_paths_with_spaces","if_user_says_codex_writes_code_then_provide_codex_prompt_not_code","high_risk_requires_confirmation","paid_api_requires_warning"],
      "tools_registry": default_tools(),
      "workflow_registry":{"workflows":["image_review_workflow","graphic_design_review_workflow","b2b_content_workflow","disk_maintenance_workflow","codex_tool_install_workflow","error_debug_workflow","daily_ops_workflow"]},
      "default_risk_rules":{"low":"可自动建议执行","medium":"需要用户确认","high":"只给建议不执行"}
    }

def init_store(force=False):
    s=seed()
    dirs=["01_identity","02_task_memory","03_tool_registry","04_skill_memory/codex_prompts","05_workflows","06_error_lessons","07_outputs/reports","07_outputs/summaries","07_outputs/exports","07_outputs/maintenance","07_outputs/snapshots"]
    for d in dirs: ensure(STORE_ROOT/d)
    json_files={
      "01_identity/user_profile.json":s["user_profile"],"01_identity/business_profile.json":s["business_profile"],"01_identity/brand_profiles.json":s["brand_profiles"],"01_identity/preferences.json":s["preferences"],
      "02_task_memory/task_index.json":{"total":0,"by_status":{},"by_tool":{}},
      "03_tool_registry/tools_registry.json":s["tools_registry"],"03_tool_registry/tool_health.json":{"score":0,"updated_at":None,"tools":[]},"03_tool_registry/tool_routes.json":{"routes":[]},"03_tool_registry/tool_usage_stats.json":{},
      "05_workflows/workflow_registry.json":s["workflow_registry"],"05_workflows/daily_ops_plan.json":{"date":None,"tasks":[]},
      "06_error_lessons/anti_hallucination_rules.json":{"rules":s["anti_hallucination_rules"]},
    }
    text_files=["02_task_memory/task_log.jsonl","02_task_memory/recent_context.md","04_skill_memory/learned_skills.jsonl","04_skill_memory/skill_candidates.jsonl","04_skill_memory/skill_library.md","05_workflows/workflow_runs.jsonl","05_workflows/automation_queue.jsonl","06_error_lessons/error_log.jsonl","06_error_lessons/lessons_learned.md","06_error_lessons/failed_commands.jsonl"]
    for r,v in json_files.items():
        p=STORE_ROOT/r
        if p.exists() and not force: print(f"已存在: {p}")
        else: jdump(p,v); print(f"已创建: {p}")
    for r in text_files:
        p=STORE_ROOT/r
        if p.exists() and not force: print(f"已存在: {p}")
        else: ensure(p.parent); p.write_text("",encoding="utf-8"); print(f"已创建: {p}")

def classify_error(err: str):
    t=err.lower()
    mapping=[("early eof","Git clone early EOF"),("404","404 raw 文件不存在"),("401","401 API Key"),("402","402 余额/额度"),("429","429 限流"),("timeout","timeout"),("json","JSON parse error"),("terminator","PowerShell 字符串缺少终止符"),("unicode","Unicode 乱码"),("gateway","gateway not reachable"),("model not found","model not found"),("not a git repository","not a git repository"),("modulenotfounderror","Python ModuleNotFoundError"),("is not recognized","PowerShell command not found"),("path not found","Path not found")]
    for k,v in mapping:
        if k in t: return v
    return "Path not found" if "not found" in t else "unknown"

def remember(args):
    init_store(False)
    item={"time":ts("%Y-%m-%d %H:%M:%S"),"task":args.task,"tool":args.tool,"status":args.status,"summary":args.summary,"output":args.output or "","error":args.error or "","tags":[x.strip() for x in (args.tags or "").split(",") if x.strip()]}
    jl_append(STORE_ROOT/"02_task_memory/task_log.jsonl",item)
    idx=jload(STORE_ROOT/"02_task_memory/task_index.json",{"total":0,"by_status":{},"by_tool":{}})
    if "by_tool" not in idx or not isinstance(idx.get("by_tool"),dict): idx["by_tool"]={}
    if "by_status" not in idx or not isinstance(idx.get("by_status"),dict): idx["by_status"]={}
    idx["total"]=int(idx.get("total",0))+1; idx["by_status"][args.status]=idx["by_status"].get(args.status,0)+1; idx["by_tool"][args.tool]=idx["by_tool"].get(args.tool,0)+1; jdump(STORE_ROOT/"02_task_memory/task_index.json",idx)
    if args.status=="fail" or args.error:
        et=classify_error(args.error or args.summary)
        jl_append(STORE_ROOT/"06_error_lessons/error_log.jsonl",{"time":item["time"],"task":args.task,"tool":args.tool,"error":args.error or args.summary,"error_type":et})
    (STORE_ROOT/"02_task_memory/recent_context.md").write_text(f"- {item['time']} | {args.tool} | {args.status} | {args.task}\n",encoding="utf-8")
    usage=jload(STORE_ROOT/"03_tool_registry/tool_usage_stats.json",{}); usage[args.tool]=usage.get(args.tool,0)+1; jdump(STORE_ROOT/"03_tool_registry/tool_usage_stats.json",usage)
    print(f"记录成功: {STORE_ROOT/'02_task_memory/task_log.jsonl'}")

def review(args):
    rows=jl_read(STORE_ROOT/"02_task_memory/task_log.jsonl")[-args.limit:]
    succ=[x for x in rows if x.get("status")=="success"]
    fail=[x for x in rows if x.get("status")=="fail"]
    top_tools=Counter([x.get("tool","") for x in rows]).most_common(5)
    rep_err=Counter([classify_error(x.get("error","")) for x in fail]).most_common(5)
    task_types=Counter([x.get("task","").split()[0] if x.get("task") else "unknown" for x in rows]).most_common(5)
    md=["# 任务复盘","","## 最近成功任务"]+[f"- {x['task']} ({x['tool']})" for x in succ[-5:]]+["","## 最近失败任务"]+[f"- {x['task']} | {x.get('error','')[:80]}" for x in fail[-5:]]+["","## 最常用工具"]+[f"- {k}: {v}" for k,v in top_tools]+["","## 重复错误"]+[f"- {k}: {v}" for k,v in rep_err]+["","## 常见任务类型"]+[f"- {k}: {v}" for k,v in task_types]+["","## 需要维护的工具"]+[f"- {k}" for k,v in top_tools if v>=3]+["","## 可沉淀技能经验","- 高频成功任务可沉淀为 workflow/模板。","","## 建议下一步","- 执行 learn","- 执行 skill-health","- 执行 daily-ops"]
    p=STORE_ROOT/f"07_outputs/summaries/review_{ts()}.md"; ensure(p.parent); p.write_text("\n".join(md),encoding="utf-8"); print(f"已保存: {p}")

def learn(_):
    logs=jl_read(STORE_ROOT/"02_task_memory/task_log.jsonl"); errs=jl_read(STORE_ROOT/"06_error_lessons/error_log.jsonl")
    pref=jload(STORE_ROOT/"01_identity/preferences.json",{})
    succ=[x for x in logs if x.get("status")=="success"]
    rec={"time":ts("%Y-%m-%d %H:%M:%S"),"user_preferences":pref.get("rules",[]),"common_tasks":Counter([x.get("task","") for x in logs]).most_common(8),"success_paths":Counter([x.get("tool","") for x in succ]).most_common(8),"failure_patterns":Counter([x.get("error_type",classify_error(x.get("error",""))) for x in errs]).most_common(8),"avoid_repeat":["失败命令先查原因","路径含空格必须加引号"],"skill_candidates":["高频任务模板化"],"codex_improvements":[x for x,c in Counter([e.get("tool","") for e in errs]).items() if c>=2]}
    jl_append(STORE_ROOT/"04_skill_memory/learned_skills.jsonl",rec)
    ll=STORE_ROOT/"06_error_lessons/lessons_learned.md"
    ll.write_text(ll.read_text(encoding="utf-8")+f"\n## {rec['time']}\n- 失败模式: {rec['failure_patterns']}\n",encoding="utf-8")
    p=STORE_ROOT/f"07_outputs/summaries/learn_summary_{ts()}.md"; p.write_text("# 长期学习总结\n"+json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8"); print(f"已保存: {p}")

def propose(args):
    idea=args.idea
    rules=[("b2b|blog|seo|geo|landing|faq|询盘|内容","b2b_marketing_tool"),("图片|风格|真实感|图像","image_analysis_tool"),("平面|排版|设计","graphic_design_tool"),("路由|自检|防幻觉","agent_control_center"),("自动|调度|执行","autopilot_operator"),("复盘|长期记忆|学习","self_improving_robot")]
    recommend="new_tool"
    for pat,t in rules:
        if re.search(pat,idea,re.I): recommend=t; break
    need_new=(recommend=="new_tool")
    proposal={"time":ts("%Y-%m-%d %H:%M:%S"),"idea":idea,"need_new_tool":need_new,"recommend":recommend,"skill_name":("new_"+re.sub(r"\W+","_",idea.lower())[:30]) if need_new else f"extend_{recommend}","file_path":r"D:\bot\tool\<skill_name>","boundary":"仅低风险文本/分析处理，不做删除/付费API","risk_level":"medium" if need_new else "low"}
    jl_append(STORE_ROOT/"04_skill_memory/skill_candidates.jsonl",proposal)
    prompt=("# Codex 任务提示词\n"f"目标: {idea}\n"f"结论: {'建议扩展已有工具 '+recommend if not need_new else '建议新建工具'}\n""安全限制: 不删除文件、不改openclaw.json、不调用付费API、不覆盖旧工具。\n测试: --help / 样例命令。\n")
    p=STORE_ROOT/f"04_skill_memory/codex_prompts/{ts()}_skill_prompt.md"; p.write_text(prompt,encoding="utf-8"); print(f"已保存: {p}")

def gen_codex(args):
    files=[x.strip() for x in (args.files or "").split(",") if x.strip()]
    txt=["# Codex Prompt",f"- 任务目标: {args.goal}",f"- 风险等级: {args.risk}","- 文件范围:"]+([f"  - {x}" for x in files] if files else ["  - 待确认文件"])+["- 安全限制: 不删除文件、不改openclaw.json、不调付费API、不覆盖已有工具。","- 测试命令: py \"...self_improving_robot.py\" --help","- 验收标准: 命令可运行/报告落盘/路径正确。","- 禁止事项: 危险删除命令、静默覆盖、伪造完成状态。"]
    p=STORE_ROOT/f"04_skill_memory/codex_prompts/{ts()}_codex_prompt.md"; p.write_text("\n".join(txt),encoding="utf-8"); print(f"已保存: {p}")

def scan_tree(root: Path):
    out={"root":str(root),"exists":root.exists(),"py":[],"ps1":[],"readme":[],"skill":[],"dirs":[]}
    if not root.exists(): return out
    for p in root.rglob("*"):
        if p.is_dir(): out["dirs"].append(str(p))
        else:
            n=p.name.lower()
            if n.endswith(".py"): out["py"].append(str(p))
            if n.endswith(".ps1"): out["ps1"].append(str(p))
            if n=="readme.md": out["readme"].append(str(p))
            if n=="skill.md": out["skill"].append(str(p))
    return out

def registry_audit(args):
    reg=jload(STORE_ROOT/"03_tool_registry/tools_registry.json",default_tools())
    scans=[scan_tree(x) for x in [TOOL_ROOT,TOOLS_ROOT,STORE_ROOT,WORKSPACE,SKILLS]]
    all_readmes=[p for s in scans for p in s["readme"]]; all_skills=[p for s in scans for p in s["skill"]]
    dup_readme=[k for k,v in Counter([Path(x).name for x in all_readmes]).items() if v>1]
    dup_skill=[k for k,v in Counter([Path(x).name for x in all_skills]).items() if v>1]
    candidate_check=[]
    for t in reg.get("tools",[]):
        candidate_check.append({"name":t.get("name"),"candidate_paths":[{"path":p,"exists":Path(p).exists()} for p in t.get("candidate_paths",[])]})
    tool_dirs=set([Path(p).name.lower() for p in scans[0]["dirs"]]) if scans[0]["exists"] else set()
    tools_dirs2=set([Path(p).name.lower() for p in scans[1]["dirs"]]) if scans[1]["exists"] else set()
    overlap=sorted(tool_dirs & tools_dirs2)
    workspace_notes=[p for p in scans[3]["readme"] if "workspace" in p.lower()]
    suggested={"generated_at":ts("%Y-%m-%d %H:%M:%S"),"tools":reg.get("tools",[]),"candidate_path_check":candidate_check,"path_overlap_between_tool_and_tools":overlap,"scan_summary":scans}
    jdump(STORE_ROOT/"03_tool_registry/tools_registry_suggested.json",suggested)
    lines=["# Registry Audit","","## 已发现工具目录"]+[f"- {s['root']} | exists={s['exists']} | py={len(s['py'])} ps1={len(s['ps1'])}" for s in scans]+["","## README/SKILL 发现"]+[f"- README.md: {len(all_readmes)}","- SKILL.md: {len(all_skills)}",f"- 重名 README.md: {dup_readme or '无'}",f"- 重名 SKILL.md: {dup_skill or '无'}"]+["","## workspace 说明文件散乱"]+[f"- workspace相关README数: {len(workspace_notes)}"]+["","## 路径冲突与重复"]+[f"- D:\\bot\\tool 与 D:\\bot\\tools 目录重叠: {overlap or '无'}"]+["","## candidate_paths 存在性"]
    for c in candidate_check:
        lines.append(f"- {c['name']}: "+", ".join([f"{x['path']} ({'存在' if x['exists'] else '不存在'})" for x in c['candidate_paths']]))
    lines += ["","## 建议整理方案","- 保留单一工具根目录规范。","- candidate_paths 缺失项优先修复路径。","- 保持 README.md 与 SKILL.md 在每个技能目录下。"]
    rpt=STORE_ROOT/f"07_outputs/maintenance/registry_audit_{ts()}.md"; rpt.write_text("\n".join(lines),encoding="utf-8"); print(f"已保存: {rpt}")
    if args.apply:
        sug=jload(STORE_ROOT/"03_tool_registry/tools_registry_suggested.json",{})
        tools=sug.get("tools")
        if isinstance(tools,list) and all(isinstance(x,dict) and "name" in x for x in tools):
            jdump(STORE_ROOT/"03_tool_registry/tools_registry.json",{"tools":tools}); print("已安全应用 suggested tools 到 tools_registry.json")
        else:
            print("拒绝应用: suggested registry 结构不完整（必须包含 tools:list）")

def run_help_check(tool):
    for ex in tool.get("command_examples",[]):
        if "--help" in ex:
            try:
                r=subprocess.run(ex,shell=True,capture_output=True,text=True,timeout=10)
                return {"ok":r.returncode==0,"code":r.returncode,"out":(r.stdout+r.stderr)[:200]}
            except Exception as e:
                return {"ok":False,"code":-1,"out":str(e)}
    return {"ok":False,"code":-1,"out":"no --help command"}

def has_mojibake(path: Path):
    if not path.exists() or path.is_dir(): return False
    try: txt=path.read_text(encoding="utf-8")
    except Exception: return True
    bad=["�","锟斤拷"]
    return any(b in txt for b in bad)

def skill_health(_):
    reg=jload(STORE_ROOT/"03_tool_registry/tools_registry.json",default_tools()).get("tools",[])
    rows=[]; points=[]
    for t in reg:
        cp=t.get("candidate_paths",[])
        main=next((Path(p) for p in cp if Path(p).suffix in [".py",".ps1"]), Path(cp[0]) if cp else Path(""))
        main_exists=main.exists()
        parent=main.parent if str(main) else Path("")
        readme=parent/"README.md"; skill=parent/"SKILL.md"
        help_result=run_help_check(t) if main.suffix==".py" else {"ok":main_exists,"code":0 if main_exists else -1,"out":"ps1 skip help run"}
        quote_issue=any((" " in ex and '"' not in ex) for ex in t.get("command_examples",[]))
        encoding_issue=has_mojibake(main) or (readme.exists() and has_mojibake(readme))
        score=0
        score+=3 if main_exists else 0; score+=1 if readme.exists() else 0; score+=1 if skill.exists() else 0; score+=2 if help_result["ok"] else 0; score+=1 if not quote_issue else 0; score+=1 if not encoding_issue else 0; score+=1 if not t.get("paid_api_risk",False) else 0
        score-=1 if t.get("destructive_risk",False) else 0
        rows.append({"name":t.get("name"),"main_script_exists":main_exists,"readme_exists":readme.exists(),"skill_exists":skill.exists(),"help_check":help_result,"encoding_issue":encoding_issue,"path_quote_issue":quote_issue,"paid_api_risk":t.get("paid_api_risk"),"destructive_risk":t.get("destructive_risk"),"score_raw":max(score,0)})
        points.append(max(score,0))
    final=round((sum(points)/max(len(points),1))/10*10,1)
    data={"updated_at":ts("%Y-%m-%d %H:%M:%S"),"score":final,"tools":rows}
    jdump(STORE_ROOT/"03_tool_registry/tool_health.json",data)
    rpt=STORE_ROOT/f"07_outputs/maintenance/skill_health_{ts()}.md"
    rpt.write_text("# Skill Health\n总分(0-10): %s\n\n%s"%(final,"\n".join([f"- {r['name']}: {r['score_raw']}/10" for r in rows])),encoding="utf-8")
    print(f"已保存: {rpt}")

def anti(args):
    ans=args.answer; risks=[]; safer=[]
    if re.search(r"已经(创建|安装|完成)",ans): risks.append("声称已完成但无证据"); safer.append("补充检查证据：Test-Path / 日志路径。")
    if "存在" in ans and "Test-Path" not in ans: risks.append("声称文件存在但未建议 Test-Path"); safer.append("先执行 Test-Path 再确认。")
    failed=jl_read(STORE_ROOT/"06_error_lessons/failed_commands.jsonl"); failed_text="\n".join([x.get("error","") for x in failed[-30:]])
    if failed_text and any(w in ans for w in failed_text.split()[:15]): risks.append("可能重复失败命令")
    if re.search(r"[A-Za-z]:\\[^\"]* [^\"]*",ans): risks.append("路径含空格可能未加引号")
    if any(d.lower() in ans.lower() for d in DANGEROUS): risks.append("包含危险删除/重置命令"); safer.append("改为只给建议，不直接执行危险命令。")
    if "api" in ans.lower() and "收费" not in ans: risks.append("可能忽略API收费提示")
    if all(x.lower() in ans.lower() for x in ["openclaw","codex","hermes"]): risks.append("可能混淆 OpenClaw/Codex/Hermes")
    if "让 codex 写" in ans.lower() and "prompt" not in ans.lower(): risks.append("用户要求Codex写代码但回复未转为Codex prompt")
    content="# Anti Hallucination Check\n\n## 风险点\n"+"\n".join([f"- {x}" for x in (risks or ["未发现高风险"] )])+"\n\n## 更稳妥回复\n"+"\n".join([f"- {x}" for x in (safer or ["保持证据化表达，并附路径检查命令。"])])
    p=STORE_ROOT/f"07_outputs/reports/anti_hallucination_{ts()}.md"; p.write_text(content,encoding="utf-8"); print(f"已保存: {p}")

def error_learn(args):
    et=classify_error(args.error)
    causes={"Path not found":"路径错误或目录不存在","Git clone early EOF":"网络中断或远端连接不稳定","404 raw 文件不存在":"链接错误/私有仓库/未合并","401 API Key":"密钥缺失或无效","402 余额/额度":"账户额度不足","429 限流":"请求过快","timeout":"超时","JSON parse error":"JSON格式错误","PowerShell 字符串缺少终止符":"引号不成对","Unicode 乱码":"编码不一致","gateway not reachable":"网关不可达","model not found":"模型名错误","not a git repository":"当前目录不是 git 仓库","Python ModuleNotFoundError":"依赖未安装或环境错误","PowerShell command not found":"命令拼写错误或未安装"}
    fix={k:f"最小修复: {v} -> 先验证路径/网络/配置后重试。" for k,v in causes.items()}
    rec={"time":ts("%Y-%m-%d %H:%M:%S"),"error":args.error,"context":args.context or "","error_type":et,"reason":causes.get(et,"待人工分析"),"minimal_fix":fix.get(et,"最小修复: 先收集上下文并定位失败点"),"avoid_repeat":"不要直接重复失败命令，先定位根因"}
    jl_append(STORE_ROOT/"06_error_lessons/error_log.jsonl",rec)
    jl_append(STORE_ROOT/"06_error_lessons/failed_commands.jsonl",{"time":rec["time"],"error":args.error,"context":args.context or ""})
    ll=STORE_ROOT/"06_error_lessons/lessons_learned.md"; ll.write_text(ll.read_text(encoding="utf-8")+f"\n- {rec['time']} | {et} | {rec['minimal_fix']}\n",encoding="utf-8")
    print(f"错误类型: {et}\n原因: {rec['reason']}\n{rec['minimal_fix']}")

def daily(args):
    plan={"date":ts("%Y-%m-%d"),"brand":args.brand or "","industry":args.industry or "","geo_seo":["更新关键词簇与长尾词","发布1篇GEO/SEO内容"],"content":["产品页优化","FAQ补充"],"image_video":["产图提示词优化","短视频脚本草案"],"conversion":["回复询盘","跟进报价"],"tool_maintenance":["registry-audit","skill-health"],"auto_executable":["review","learn"],"need_confirmation":["高风险维护操作"],"paid_api":"禁止自动调用付费API"}
    jdump(STORE_ROOT/"05_workflows/daily_ops_plan.json",plan)
    p=STORE_ROOT/f"07_outputs/reports/daily_ops_{ts()}.md"; p.write_text("# Daily Ops\n"+json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8"); print(f"已保存: {p}")

def auto_plan(args):
    due=ts("%Y-%m-%d") if args.frequency=="daily" else (datetime.now()+timedelta(days=7)).strftime("%Y-%m-%d") if args.frequency=="weekly" else "manual"
    rec={"time":ts("%Y-%m-%d %H:%M:%S"),"task":args.task,"frequency":args.frequency,"risk":args.risk,"due_at":due,"command":""}
    jl_append(STORE_ROOT/"05_workflows/automation_queue.jsonl",rec)
    print(f"已写入: {STORE_ROOT/'05_workflows/automation_queue.jsonl'}")
    if args.risk in ["medium","high"]: print("需要用户确认")
    else: print("低风险，可建议自动运行。")
    if args.create_task and args.risk=="low": print('建议命令: schtasks /Create /SC DAILY /TN "SelfImprovingRobotDaily" /TR "py \"D:\\bot\\tool\\self_improving_robot_skill\\self_improving_robot.py\" daily-ops"')

def run_due(_):
    q=jl_read(STORE_ROOT/"05_workflows/automation_queue.jsonl")
    today=ts("%Y-%m-%d")
    ran=0
    for it in q:
        if it.get("risk") in ["medium","high"]: print(f"等待确认: {it.get('task')}"); continue
        if it.get("due_at") not in ["manual",today]: continue
        cmd=it.get("command","")
        jl_append(STORE_ROOT/"05_workflows/workflow_runs.jsonl",{"time":ts("%Y-%m-%d %H:%M:%S"),"task":it.get("task"),"status":"planned"})
        if not cmd: print(f"任务 {it.get('task')} 无命令，仅输出建议。")
        elif any(d.lower() in cmd.lower() for d in DANGEROUS) or "openclaw.json" in cmd: print(f"阻止执行高风险命令: {cmd}")
        else:
            try:
                r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=30)
                print(f"执行: {it.get('task')} code={r.returncode}")
            except Exception as e:
                print(f"执行失败: {e}")
        ran+=1
    print(f"run-due 完成，处理低风险任务: {ran}")

def export_ctx(_):
    s=seed(); reg=s["tools_registry"]["tools"]
    txt=["# System Context Export","","## 业务背景","- 国际B2B独立站运营（服装工厂、精油香薰）","","## 品牌","- Juese Clothing","- Veytis","","## 工具列表"]+[f"- {t['name']}: {t['description']}" for t in reg]+["","## 七层记忆架构","- D:\\bot\\store\\01_identity ... 07_outputs","","## 安全规则","- 不删文件/不改openclaw.json/不调付费API/高风险需确认","","## 常见路径","- D:\\bot\\tool","- C:\\Users\\Administrator\\.openclaw\\workspace\\skills","","## 行为偏好","- 先检查再执行，路径含空格加引号，用户要求Codex写则仅产出Prompt","","## 路线图","- 每日review/learn，周期registry-audit/skill-health，持续优化自动化队列"]
    p=STORE_ROOT/f"07_outputs/exports/system_context_{ts()}.md"; p.write_text("\n".join(txt),encoding="utf-8"); print(f"已保存: {p}")

def snapshot(_):
    files=[x for x in STORE_ROOT.rglob("*") if x.is_file()] if STORE_ROOT.exists() else []
    data={"time":ts("%Y-%m-%d %H:%M:%S"),"store_file_count":len(files),"latest_task":(jl_read(STORE_ROOT/"02_task_memory/task_log.jsonl") or [None])[-1],"latest_error":(jl_read(STORE_ROOT/"06_error_lessons/error_log.jsonl") or [None])[-1],"latest_skill_candidate":(jl_read(STORE_ROOT/"04_skill_memory/skill_candidates.jsonl") or [None])[-1],"tool_health":jload(STORE_ROOT/"03_tool_registry/tool_health.json",{}).get("score"),"recent_outputs":[str(x) for x in sorted([f for f in files if "07_outputs" in str(f)], key=lambda p:p.stat().st_mtime, reverse=True)[:10]]}
    p=STORE_ROOT/f"07_outputs/snapshots/snapshot_{ts()}.json"; jdump(p,data); print(f"已保存: {p}")

def parser_build():
    p=argparse.ArgumentParser(description="self_improving_robot")
    s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("init-store"); a.add_argument("--force",action="store_true")
    a=s.add_parser("remember-task"); [a.add_argument(*x[0],**x[1]) for x in [(("--task",),{"required":True}),(("--tool",),{"required":True}),(("--status",),{"required":True,"choices":["success","fail","partial"]}),(("--summary",),{"required":True}),(("--output",),{}),(("--error",),{}),(("--tags",),{})]]
    a=s.add_parser("review"); a.add_argument("--limit",type=int,default=20)
    s.add_parser("learn")
    a=s.add_parser("propose-skill"); a.add_argument("--idea",required=True)
    a=s.add_parser("generate-codex-prompt"); a.add_argument("--goal",required=True); a.add_argument("--files"); a.add_argument("--risk",choices=["low","medium","high"],default="low")
    a=s.add_parser("registry-audit"); a.add_argument("--apply",action="store_true")
    s.add_parser("skill-health")
    a=s.add_parser("anti-hallucination-check"); a.add_argument("--answer",required=True)
    a=s.add_parser("error-learn"); a.add_argument("--error",required=True); a.add_argument("--context")
    a=s.add_parser("daily-ops"); a.add_argument("--brand"); a.add_argument("--industry")
    a=s.add_parser("automation-plan"); a.add_argument("--task",required=True); a.add_argument("--frequency",choices=["daily","weekly","manual"],default="manual"); a.add_argument("--risk",choices=["low","medium","high"],default="medium"); a.add_argument("--create-task",action="store_true")
    s.add_parser("run-due"); s.add_parser("export-system-context"); s.add_parser("snapshot")
    return p

def main():
    args=parser_build().parse_args()
    try:
        {"init-store":lambda:init_store(args.force),"remember-task":lambda:remember(args),"review":lambda:review(args),"learn":lambda:learn(args),"propose-skill":lambda:propose(args),"generate-codex-prompt":lambda:gen_codex(args),"registry-audit":lambda:registry_audit(args),"skill-health":lambda:skill_health(args),"anti-hallucination-check":lambda:anti(args),"error-learn":lambda:error_learn(args),"daily-ops":lambda:daily(args),"automation-plan":lambda:auto_plan(args),"run-due":lambda:run_due(args),"export-system-context":lambda:export_ctx(args),"snapshot":lambda:snapshot(args)}[args.cmd]()
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)

if __name__=="__main__":
    main()
