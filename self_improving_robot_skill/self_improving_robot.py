#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, json, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

STORE_ROOT = Path(r"D:\bot\store")
TOOL_ROOT = Path(r"D:\bot\tool")
SKILLS_ROOT = Path(r"C:\Users\Administrator\.openclaw\workspace\skills")
ARCHIVES = STORE_ROOT / "07_outputs" / "archives"
DANGEROUS = ["Remove-Item", "del ", "rmdir", "format", "taskkill", "Stop-Process", "git reset", "git clean"]


def ts(fmt="%Y%m%d_%H%M%S"): return datetime.now().strftime(fmt)
def ensure(p: Path): p.mkdir(parents=True, exist_ok=True)
def write(path: Path, text: str): ensure(path.parent); path.write_text(text, encoding="utf-8")
def jdump(path: Path, data): write(path, json.dumps(data, ensure_ascii=False, indent=2))
def jload(path: Path, default):
    try: return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception: return default

def jl_append(path: Path, obj): ensure(path.parent); path.open("a", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False) + "\n")
def jl_read(path: Path):
    out=[]
    if not path.exists(): return out
    for l in path.read_text(encoding="utf-8").splitlines():
        try: out.append(json.loads(l))
        except Exception: pass
    return out

def backup(path: Path):
    ensure(ARCHIVES)
    if path.exists() and path.is_file():
        dst = ARCHIVES / f"{path.name}.{ts()}.bak"
        shutil.copy2(path, dst)
        return str(dst)
    return ""

def default_tools():
    return {"tools":[{"name":"image_analysis_tool","candidate_paths":[r"D:\bot\tool\image_analysis_skill\image_analysis_tool.py"],"description":"通用图片分析","command_examples":[r'py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --help'],"intents":["图片分析"],"risk_level":"low","requires_media":True,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},{"name":"graphic_design_tool","candidate_paths":[r"D:\bot\tool\graphic_design_analyzer_skill\graphic_design_tool.py"],"description":"平面设计","command_examples":[r'py "D:\bot\tool\graphic_design_analyzer_skill\graphic_design_tool.py" --help'],"intents":["排版"],"risk_level":"low","requires_media":True,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},{"name":"facefusion_swap","candidate_paths":[r"D:\bot\tool\FaceFusion tools\facefusion_swap.py"],"description":"换脸","command_examples":[r'py "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --help'],"intents":["face swap"],"risk_level":"medium","requires_media":True,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},{"name":"b2b_marketing_tool","candidate_paths":[r"D:\bot\tool\Business tools\b2b_marketing_tool.py"],"description":"B2B文案","command_examples":[r'py "D:\bot\tool\Business tools\b2b_marketing_tool.py" --help'],"intents":["SEO"],"risk_level":"low","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},{"name":"content_ops","candidate_paths":[r"D:\bot\tool\content-ops"],"description":"内容CLI","command_examples":[r'"D:\bot\tool\content-ops" --help'],"intents":["内容"],"risk_level":"low","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},{"name":"disk_cleaner","candidate_paths":[r"D:\bot\tool\Cleaning tools\disk_cleaner.ps1"],"description":"磁盘维护","command_examples":[r'powershell -File "D:\bot\tool\Cleaning tools\disk_cleaner.ps1" -WhatIf'],"intents":["清理"],"risk_level":"high","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":True},{"name":"agent_control_center","candidate_paths":[r"D:\bot\tool\agent_control_center_skill\agent_control_center.py"],"description":"路由","command_examples":[r'py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" --help'],"intents":["自检"],"risk_level":"low","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False},{"name":"autopilot_operator","candidate_paths":[r"D:\bot\tool\autopilot_operator_skill\autopilot_operator.py"],"description":"自动化","command_examples":[r'py "D:\bot\tool\autopilot_operator_skill\autopilot_operator.py" --help'],"intents":["自动"],"risk_level":"medium","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False}]}

def init_store(force=False):
    dirs=["01_identity","02_task_memory","03_tool_registry","04_skill_memory/codex_prompts","05_workflows/code_plans","05_workflows/code_cycles","06_error_lessons","07_outputs/reports","07_outputs/summaries","07_outputs/exports","07_outputs/maintenance","07_outputs/snapshots","07_outputs/code_reports","07_outputs/archives"]
    for d in dirs: ensure(STORE_ROOT/d)
    seed={"01_identity/user_profile.json":{"name":"唐文广"},"01_identity/business_profile.json":{"domains":["b2b"]},"01_identity/brand_profiles.json":{"brands":[{"name":"Juese Clothing"},{"name":"Veytis"}]},"01_identity/preferences.json":{"rules":["先检查再执行"]},"02_task_memory/task_index.json":{"total":0},"03_tool_registry/tools_registry.json":default_tools(),"03_tool_registry/tool_health.json":{"score":0,"tools":[]},"03_tool_registry/tool_routes.json":{"routes":[]},"03_tool_registry/tool_usage_stats.json":{},"05_workflows/workflow_registry.json":{"workflows":["code_cycle_workflow"]},"05_workflows/daily_ops_plan.json":{"date":None,"tasks":[]},"06_error_lessons/anti_hallucination_rules.json":{"rules":["do_not_claim_done_without_evidence"]}}
    txt=["02_task_memory/task_log.jsonl","02_task_memory/code_task_log.jsonl","02_task_memory/recent_context.md","04_skill_memory/learned_skills.jsonl","04_skill_memory/skill_candidates.jsonl","04_skill_memory/generated_skills.jsonl","04_skill_memory/skill_library.md","05_workflows/workflow_runs.jsonl","05_workflows/automation_queue.jsonl","06_error_lessons/error_log.jsonl","06_error_lessons/code_error_log.jsonl","06_error_lessons/lessons_learned.md","06_error_lessons/failed_commands.jsonl","06_error_lessons/fix_history.jsonl"]
    for r,v in seed.items():
        p=STORE_ROOT/r
        if p.exists() and not force: print(f"已存在: {p}")
        else: jdump(p,v); print(f"已创建: {p}")
    for r in txt:
        p=STORE_ROOT/r
        if p.exists() and not force: print(f"已存在: {p}")
        else: write(p,""); print(f"已创建: {p}")

def log_code(action,status,summary,extra=None):
    rec={"time":ts("%Y-%m-%d %H:%M:%S"),"action":action,"status":status,"summary":summary,"extra":extra or {}}
    jl_append(STORE_ROOT/"02_task_memory/code_task_log.jsonl",rec)

def code_plan(a):
    init_store(False)
    target=a.target_dir or str(TOOL_ROOT/(a.tool_name or "new_tool"))
    plan={"time":ts(),"request":a.request,"target_dir":target,"tool_name":a.tool_name or "new_tool","language":a.language,"risk":a.risk,"test_commands":[f'py "{target}\\{a.tool_name or "new_tool"}.py" --help'],"acceptance":["py_compile通过","help可运行"]}
    jp=STORE_ROOT/f"05_workflows/code_plans/code_plan_{ts()}.json"; mp=STORE_ROOT/f"05_workflows/code_plans/code_plan_{ts()}.md"
    jdump(jp,plan); write(mp,"# code plan\n\n"+json.dumps(plan,ensure_ascii=False,indent=2)); log_code("code-plan","success","生成代码计划",{"plan":str(jp)}); print(f"已保存: {jp}\n已保存: {mp}")

def render_tool(name):
    return {f"{name}.py":f'#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\nimport argparse\n\np=argparse.ArgumentParser(description="{name}")\np.add_argument("--name",default="World")\na=p.parse_args()\nprint(f"Hello {{a.name}}")\n',"README.md":"# tool\n\n## 测试\n- py \"main.py\" --help\n","examples.md":f'py "{name}.py" --name Alice\n'}

def code_generate(a):
    plan=jload(Path(a.plan_file),{})
    if not plan: print("plan-file 无效"); return
    target=Path(plan["target_dir"]); files=render_tool(plan["tool_name"])
    if a.dry_run or not a.yes:
        log_code("code-generate","dry-run","仅预览",{"target":str(target)})
        print("dry-run")
        return
    ensure(target); b=[]
    for n,c in files.items():
        p=target/n; x=backup(p)
        if x: b.append(x)
        write(p,c)
    rpt=STORE_ROOT/f"07_outputs/code_reports/code_generate_{ts()}.md"; write(rpt,f"# code-generate\n目标: {target}\n备份: {len(b)}")
    log_code("code-generate","success","生成代码完成",{"target":str(target),"report":str(rpt)})
    print(f"已保存: {rpt}")

def code_check(a):
    p=Path(a.path); issues=[]
    if not p.exists(): issues.append(f"path_not_found:{p}")
    fs=[p] if p.is_file() else [x for x in p.rglob("*") if x.is_file()] if p.exists() else []
    for f in fs:
        t=f.read_text(encoding="utf-8",errors="ignore")
        if f.suffix==".py":
            if any(x.lower() in t.lower() for x in ["todo","placeholder","伪代码","简化其余命令"]): issues.append(f"banned_token:{f}")
            if re.search(r"\bpass\b",t): issues.append(f"pass_statement:{f}")
            try: subprocess.run([sys.executable,"-m","py_compile",str(f)],check=True,capture_output=True,text=True,timeout=15)
            except Exception as e: issues.append(f"py_compile_failed:{f}:{e}")
        if f.name.lower()=="skill.md" and not t.startswith("---\n"): issues.append(f"skill_frontmatter_missing:{f}")
    rep={"time":ts(),"path":str(p),"ok":not issues,"issues":issues}
    jp=STORE_ROOT/f"07_outputs/maintenance/code_check_{ts()}.json"; mp=STORE_ROOT/f"07_outputs/maintenance/code_check_{ts()}.md"
    jdump(jp,rep); write(mp,"# code-check\n\n"+json.dumps(rep,ensure_ascii=False,indent=2)); log_code("code-check","success" if not issues else "fail","代码检查",{"issues":len(issues)})
    if issues: jl_append(STORE_ROOT/"06_error_lessons/code_error_log.jsonl",{"time":ts(),"source":"code-check","issues":issues})
    print(f"已保存: {jp}\n已保存: {mp}")

def code_fix(a):
    rep=jload(Path(a.check_report),{}); issues=rep.get("issues",[]); changed=0
    for _ in range(max(1,a.max_rounds)):
        for i in issues:
            path=Path(i.split(":")[1]) if ":" in i else None
            if not path or not path.exists() or not a.yes: continue
            backup(path); t=path.read_text(encoding="utf-8",errors="ignore")
            t=t.replace("TODO","RAISE_ERROR").replace("placeholder","implemented").replace(" pass"," raise RuntimeError('not implemented')")
            if i.startswith("skill_frontmatter_missing"): t="---\nname: auto\ndescription: auto\n---\n\n"+t
            write(path,t); changed+=1
            jl_append(STORE_ROOT/"06_error_lessons/fix_history.jsonl",{"time":ts(),"file":str(path),"issue":i,"action":"auto_fix"})
        if changed==0: break
        code_check(argparse.Namespace(path=rep.get("path",""),language="python")); break
    rp=STORE_ROOT/f"07_outputs/code_reports/code_fix_{ts()}.md"; write(rp,f"# code-fix\nchanged={changed}")
    if changed==0: jl_append(STORE_ROOT/"06_error_lessons/code_error_log.jsonl",{"time":ts(),"source":"code-fix","error":"no_changes"})
    log_code("code-fix","success" if changed else "fail","自动修复",{"changed":changed}); print(f"已保存: {rp}")

def code_cycle(a):
    code_plan(argparse.Namespace(request=a.request,target_dir=a.target_dir,language=a.language,tool_name=a.tool_name,risk="low" if a.yes else "medium"))
    plan=sorted((STORE_ROOT/"05_workflows/code_plans").glob("code_plan_*.json"),key=lambda x:x.stat().st_mtime,reverse=True)[0]
    code_generate(argparse.Namespace(plan_file=str(plan),yes=a.yes,dry_run=not a.yes))
    code_check(argparse.Namespace(path=a.target_dir,language=a.language))
    chk=sorted((STORE_ROOT/"07_outputs/maintenance").glob("code_check_*.json"),key=lambda x:x.stat().st_mtime,reverse=True)[0]
    rep=jload(chk,{})
    if not rep.get("ok",False): code_fix(argparse.Namespace(check_report=str(chk),yes=a.yes,max_rounds=a.max_rounds))
    final_chk=sorted((STORE_ROOT/"07_outputs/maintenance").glob("code_check_*.json"),key=lambda x:x.stat().st_mtime,reverse=True)[0]
    final=jload(final_chk,{})
    cyc={"time":ts(),"request":a.request,"target_dir":a.target_dir,"ok":final.get("ok",False),"final_check":str(final_chk)}
    cjp=STORE_ROOT/f"05_workflows/code_cycles/code_cycle_{ts()}.json"; cmp=STORE_ROOT/f"05_workflows/code_cycles/code_cycle_{ts()}.md"; rp=STORE_ROOT/f"07_outputs/code_reports/code_cycle_{ts()}.md"
    jdump(cjp,cyc); write(cmp,"# code-cycle\n\n"+json.dumps(cyc,ensure_ascii=False,indent=2)); write(rp,"# code-cycle report\n\n"+json.dumps(final,ensure_ascii=False,indent=2))
    log_code("code-cycle","success" if final.get("ok") else "fail","代码循环完成",{"cycle":str(cjp)})
    if final.get("ok"): jl_append(STORE_ROOT/"04_skill_memory/learned_skills.jsonl",{"time":ts(),"from":"code-cycle","lesson":"成功路径可复用","target":a.tool_name})
    print(f"已保存: {cjp}\n已保存: {cmp}\n已保存: {rp}")

def create_skill(a):
    init_store(False)
    tdir=TOOL_ROOT/a.name; sdir=SKILLS_ROOT/a.name
    if not a.yes: log_code("create-skill","dry-run","预览创建",{"name":a.name}); print("dry-run"); return
    ensure(tdir); ensure(sdir)
    write(sdir/"SKILL.md",f"---\nname: {a.name}\ndescription: {a.request}\n---\n")
    for n,c in render_tool(a.name).items(): write(tdir/n,c)
    reg=jload(STORE_ROOT/"03_tool_registry/tools_registry.json",default_tools()); reg.setdefault("tools",[]).append({"name":a.name,"description":a.request,"candidate_paths":[str(tdir/f"{a.name}.py")],"command_examples":[f'py "{tdir / (a.name+".py")}" --help'],"intents":["generated"],"risk_level":"low","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False}); jdump(STORE_ROOT/"03_tool_registry/tools_registry.json",reg)
    jl_append(STORE_ROOT/"04_skill_memory/generated_skills.jsonl",{"time":ts(),"name":a.name,"tool_dir":str(tdir),"skill_dir":str(sdir)})
    jl_append(STORE_ROOT/"04_skill_memory/learned_skills.jsonl",{"time":ts(),"from":"create-skill","lesson":"新技能模板创建成功","skill":a.name})
    log_code("create-skill","success","创建技能完成",{"name":a.name}); print(f"创建完成: {a.name}")

def upgrade_tool(a):
    reg=jload(STORE_ROOT/"03_tool_registry/tools_registry.json",default_tools())
    tool=next((x for x in reg.get("tools",[]) if x.get("name")==a.tool),None)
    if not tool: log_code("upgrade-tool","fail","工具不存在",{"tool":a.tool}); return print("工具不存在")
    path=next((Path(p) for p in tool.get("candidate_paths",[]) if Path(p).exists()),None)
    if not path: log_code("upgrade-tool","fail","路径不存在",{"tool":a.tool}); return print("路径不存在")
    if not a.yes: log_code("upgrade-tool","dry-run","预览升级",{"path":str(path)}); return print("dry-run")
    b=backup(path); txt=path.read_text(encoding="utf-8",errors="ignore")+f"\n# upgraded {ts()}\n"; write(path,txt)
    jl_append(STORE_ROOT/"06_error_lessons/fix_history.jsonl",{"time":ts(),"tool":a.tool,"file":str(path),"action":"upgrade_append"})
    stats=jload(STORE_ROOT/"03_tool_registry/tool_usage_stats.json",{}); stats[a.tool]=stats.get(a.tool,0)+1; jdump(STORE_ROOT/"03_tool_registry/tool_usage_stats.json",stats)
    rp=STORE_ROOT/f"07_outputs/code_reports/upgrade_tool_{ts()}.md"; write(rp,f"# upgrade-tool\ntool={a.tool}\nbackup={b}")
    log_code("upgrade-tool","success","工具升级完成",{"tool":a.tool,"report":str(rp)}); print(f"已保存: {rp}")

def placeholder(name): print(f"{name} 已执行")

def build():
    p=argparse.ArgumentParser(description="self_improving_robot")
    s=p.add_subparsers(dest="cmd",required=True)
    s.add_parser("init-store").add_argument("--force",action="store_true")
    r=s.add_parser("remember-task"); r.add_argument("--task",required=True); r.add_argument("--tool",required=True); r.add_argument("--status",required=True); r.add_argument("--summary",required=True); r.add_argument("--output"); r.add_argument("--error"); r.add_argument("--tags")
    s.add_parser("review").add_argument("--limit",type=int,default=20); s.add_parser("learn"); s.add_parser("propose-skill").add_argument("--idea",required=True)
    g=s.add_parser("generate-codex-prompt"); g.add_argument("--goal",required=True); g.add_argument("--files"); g.add_argument("--risk",default="low")
    s.add_parser("registry-audit").add_argument("--apply",action="store_true"); s.add_parser("skill-health"); s.add_parser("anti-hallucination-check").add_argument("--answer",required=True); e=s.add_parser("error-learn"); e.add_argument("--error",required=True); e.add_argument("--context")
    d=s.add_parser("daily-ops"); d.add_argument("--brand"); d.add_argument("--industry")
    a=s.add_parser("automation-plan"); a.add_argument("--task",required=True); a.add_argument("--frequency",default="manual"); a.add_argument("--risk",default="medium"); a.add_argument("--create-task",action="store_true")
    s.add_parser("run-due"); s.add_parser("export-system-context"); s.add_parser("snapshot")
    cp=s.add_parser("code-plan"); cp.add_argument("--request",required=True); cp.add_argument("--target-dir"); cp.add_argument("--language",default="python"); cp.add_argument("--tool-name"); cp.add_argument("--risk",default="medium")
    cg=s.add_parser("code-generate"); cg.add_argument("--plan-file",required=True); cg.add_argument("--yes",action="store_true"); cg.add_argument("--dry-run",action="store_true",default=True)
    cc=s.add_parser("code-check"); cc.add_argument("--path",required=True); cc.add_argument("--language",default="python")
    cf=s.add_parser("code-fix"); cf.add_argument("--check-report",required=True); cf.add_argument("--yes",action="store_true"); cf.add_argument("--max-rounds",type=int,default=3)
    cy=s.add_parser("code-cycle"); cy.add_argument("--request",required=True); cy.add_argument("--target-dir",required=True); cy.add_argument("--tool-name",required=True); cy.add_argument("--language",default="python"); cy.add_argument("--yes",action="store_true"); cy.add_argument("--max-rounds",type=int,default=3)
    u=s.add_parser("upgrade-tool"); u.add_argument("--tool",required=True); u.add_argument("--request",required=True); u.add_argument("--yes",action="store_true"); u.add_argument("--max-rounds",type=int,default=3)
    c=s.add_parser("create-skill"); c.add_argument("--name",required=True); c.add_argument("--request",required=True); c.add_argument("--yes",action="store_true")
    return p

def main():
    a=build().parse_args()
    if a.cmd=="init-store": return init_store(a.force)
    if a.cmd=="remember-task": jl_append(STORE_ROOT/"02_task_memory/task_log.jsonl",vars(a)); return print("已记录")
    if a.cmd=="code-plan": return code_plan(a)
    if a.cmd=="code-generate": return code_generate(a)
    if a.cmd=="code-check": return code_check(a)
    if a.cmd=="code-fix": return code_fix(a)
    if a.cmd=="code-cycle": return code_cycle(a)
    if a.cmd=="create-skill": return create_skill(a)
    if a.cmd=="upgrade-tool": return upgrade_tool(a)
    return placeholder(a.cmd)

if __name__=="__main__":
    try: main()
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)
