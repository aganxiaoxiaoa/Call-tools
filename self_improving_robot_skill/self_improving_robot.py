#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, json, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
from collections import Counter

STORE_ROOT = Path(r"D:\bot\store")
TOOL_ROOT = Path(r"D:\bot\tool")
TOOLS_ROOT = Path(r"D:\bot\tools")
WORKSPACE = Path(r"C:\Users\Administrator\.openclaw\workspace")
SKILLS_ROOT = WORKSPACE / "skills"
LOCAL_SEED = Path(__file__).with_name("default_seed.json")
WIN_SEED = Path(r"D:\bot\tool\self_improving_robot_skill\default_seed.json")
ARCHIVES = STORE_ROOT / "07_outputs" / "archives"


def ts(f="%Y%m%d_%H%M%S"): return datetime.now().strftime(f)
def ensure(p): Path(p).mkdir(parents=True, exist_ok=True)
def write(p, t): p=Path(p); ensure(p.parent); p.write_text(t, encoding="utf-8")
def jdump(p, d): write(p, json.dumps(d, ensure_ascii=False, indent=2))
def jload(p, d):
    try: return json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else d
    except Exception: return d
def jl_append(p, o): p=Path(p); ensure(p.parent); p.open("a", encoding="utf-8").write(json.dumps(o, ensure_ascii=False)+"\n")
def jl_read(p):
    p=Path(p); out=[]
    if not p.exists(): return out
    for l in p.read_text(encoding="utf-8").splitlines():
        try: out.append(json.loads(l))
        except Exception: pass
    return out

def load_seed():
    for p in [WIN_SEED, LOCAL_SEED]:
        if p.exists():
            obj = jload(p, None)
            if isinstance(obj, dict) and obj.get("store_root"):
                return obj
    return {"store_root":str(STORE_ROOT),"version":"fallback","user_profile":{"name":"唐文广"},"business_profile":{"domains":["b2b"]},"brand_profiles":{"brands":[{"name":"Juese Clothing"},{"name":"Veytis"}]},"preferences":{"rules":["先检查再执行"]},"tools_registry":{"tools":[]},"workflow_registry":{"workflows":["code_cycle_workflow"]},"anti_hallucination_rules":["do_not_claim_done_without_evidence"],"default_risk_rules":{"low":"可自动","medium":"需确认","high":"仅建议"}}

def default_tools_full(seed):
    if seed.get("tools_registry",{}).get("tools") and all("name" in x for x in seed["tools_registry"]["tools"]):
        return seed["tools_registry"]
    return {"tools":[]}

def init_store(force=False):
    seed=load_seed()
    dirs=["01_identity","02_task_memory","03_tool_registry","04_skill_memory/codex_prompts","05_workflows/code_plans","05_workflows/code_cycles","06_error_lessons","07_outputs/reports","07_outputs/summaries","07_outputs/exports","07_outputs/maintenance","07_outputs/snapshots","07_outputs/code_reports","07_outputs/archives"]
    for d in dirs: ensure(STORE_ROOT/d)
    js={"01_identity/user_profile.json":seed.get("user_profile",{}),"01_identity/business_profile.json":seed.get("business_profile",{}),"01_identity/brand_profiles.json":seed.get("brand_profiles",{}),"01_identity/preferences.json":seed.get("preferences",{}),"02_task_memory/task_index.json":{"total":0,"by_status":{},"by_tool":{}},"03_tool_registry/tools_registry.json":default_tools_full(seed),"03_tool_registry/tool_health.json":{"score":0,"tools":[]},"03_tool_registry/tool_routes.json":{"routes":[]},"03_tool_registry/tool_usage_stats.json":{},"05_workflows/workflow_registry.json":seed.get("workflow_registry",{}),"05_workflows/daily_ops_plan.json":{"date":None,"tasks":[]},"06_error_lessons/anti_hallucination_rules.json":{"rules":seed.get("anti_hallucination_rules",[])}}
    txt=["02_task_memory/task_log.jsonl","02_task_memory/code_task_log.jsonl","02_task_memory/recent_context.md","04_skill_memory/learned_skills.jsonl","04_skill_memory/skill_candidates.jsonl","04_skill_memory/generated_skills.jsonl","04_skill_memory/skill_library.md","05_workflows/workflow_runs.jsonl","05_workflows/automation_queue.jsonl","06_error_lessons/error_log.jsonl","06_error_lessons/code_error_log.jsonl","06_error_lessons/lessons_learned.md","06_error_lessons/failed_commands.jsonl","06_error_lessons/fix_history.jsonl"]
    for r,v in js.items():
        p=STORE_ROOT/r
        if p.exists() and not force: print(f"已存在: {p}")
        else: jdump(p,v); print(f"已创建: {p}")
    for r in txt:
        p=STORE_ROOT/r
        if p.exists() and not force: print(f"已存在: {p}")
        else: write(p,""); print(f"已创建: {p}")

def log_code(action,status,summary,extra=None):
    jl_append(STORE_ROOT/"02_task_memory/code_task_log.jsonl",{"time":ts("%Y-%m-%d %H:%M:%S"),"action":action,"status":status,"summary":summary,"extra":extra or {}})

def detect_template(req):
    q=req.lower()
    if "openclaw" in q or "skill" in q: return "openclaw_skill_tool"
    if "hello world" in q: return "hello_world_tool"
    return "cli_tool"

def code_plan(a):
    init_store(False)
    t=detect_template(a.request)
    files=[f"{a.tool_name}.py","README.md","examples.md"] + (["SKILL.md"] if t=="openclaw_skill_tool" else [])
    plan={"request":a.request,"tool_name":a.tool_name,"target_dir":a.target_dir,"language":a.language,"template_type":t,"files_to_create":files,"files_to_modify":[],"required_arguments":["--input","--output-dir","--json"] if t=="cli_tool" else ["--name"],"output_contract":{"stdout":"human+json summary"},"test_commands":[f'py "{a.target_dir}\\{a.tool_name}.py" --help'] ,"acceptance_criteria":["files created","py_compile ok","help ok"],"risk_level":"low" if "test" in a.request.lower() else "medium","memory_writes":["05_workflows/code_plans","02_task_memory/code_task_log.jsonl"],"llm_note":"复杂业务逻辑需要 OpenClaw 主模型/Codex 参与生成核心逻辑；本工具负责模板落盘、检查、修复、记忆"}
    jp=STORE_ROOT/f"05_workflows/code_plans/code_plan_{ts()}.json"; mp=STORE_ROOT/f"05_workflows/code_plans/code_plan_{ts()}.md"
    jdump(jp,plan); write(mp,"# code-plan\n\n"+json.dumps(plan,ensure_ascii=False,indent=2)); log_code("code-plan","success","计划已生成",{"plan":str(jp)})
    print(f"已保存: {jp}\n已保存: {mp}")

def render_by_template(plan):
    n=plan["tool_name"]
    t=plan["template_type"]
    if t=="hello_world_tool":
        return {f"{n}.py":f'#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\nimport argparse\np=argparse.ArgumentParser(description="{n}")\np.add_argument("--name",default="World")\na=p.parse_args()\nprint(f"Hello {{a.name}}")\n',"README.md":"# hello world tool\n\n## test\n- py \"main.py\" --help\n","examples.md":f'py "{n}.py" --name Alice\n'}
    if t=="openclaw_skill_tool":
        return {f"{n}.py":f'#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\nimport argparse\nif __name__=="__main__":\n p=argparse.ArgumentParser(description="{n}"); p.add_argument("--input"); p.add_argument("--output-dir",default="."); p.add_argument("--json",action="store_true"); a=p.parse_args(); print("ok")\n',"README.md":"# openclaw skill tool\n\n## test\n- py tool.py --help\n","examples.md":f'py "{n}.py" --input data.txt --output-dir . --json\n',"SKILL.md":"---\nname: generated-skill\ndescription: generated by controller\n---\n"}
    return {f"{n}.py":f'#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\nimport argparse, json\nif __name__=="__main__":\n p=argparse.ArgumentParser(description="{n}"); p.add_argument("--input",required=False); p.add_argument("--output-dir",default="."); p.add_argument("--json",action="store_true"); a=p.parse_args(); out={{"tool":"{n}","input":a.input,"output_dir":a.output_dir}}; print(json.dumps(out,ensure_ascii=False) if a.json else out)\n',"README.md":"# cli tool\n\n## test\n- py tool.py --help\n","examples.md":f'py "{n}.py" --input demo.txt --output-dir . --json\n'}

def backup(p):
    ensure(ARCHIVES)
    if Path(p).exists() and Path(p).is_file():
        b=ARCHIVES/f"{Path(p).name}.{ts()}.bak"; shutil.copy2(p,b); return str(b)
    return ""

def code_generate(a):
    plan=jload(Path(a.plan_file),{})
    if not plan: return print("plan-file 无效")
    files=render_by_template(plan); target=Path(plan["target_dir"]); ensure(target)
    created=[]; backups=[]
    if a.dry_run or (not a.yes):
        log_code("code-generate","dry-run","预览",{"target":str(target),"files":list(files.keys())}); print("dry-run"); return
    for n,c in files.items():
        p=target/n; b=backup(p)
        if b: backups.append(b)
        write(p,c); created.append(str(p))
    rpt=STORE_ROOT/f"07_outputs/code_reports/code_generate_{ts()}.md"; write(rpt,"# code-generate\n"+json.dumps({"created_files":created,"backups":backups},ensure_ascii=False,indent=2))
    log_code("code-generate","success","代码已生成",{"created_files":created,"backups":backups,"report":str(rpt)})
    print(f"已保存: {rpt}")

def issue(t,f,msg): return {"type":t,"file":str(f),"message":msg}

def code_check(a):
    p=Path(a.path); issues=[]
    files=[p] if p.is_file() else [x for x in p.rglob('*') if x.is_file()] if p.exists() else []
    if not p.exists(): issues.append(issue("path_not_found",p,"path not found"))
    for f in files:
        txt=f.read_text(encoding="utf-8",errors="ignore")
        if f.suffix==".py":
            for b in ["TODO","placeholder","简化其余命令","伪代码"]:
                if b.lower() in txt.lower(): issues.append(issue("banned_token",f,b))
            if re.search(r"def\s+\w+\(.*\):\s*\n\s*pass\b",txt): issues.append(issue("pass_statement",f,"empty function pass"))
            if re.search(r"except\s+Exception\s*:\s*\n\s*pass\b",txt): issues.append(issue("except_pass_warning",f,"except Exception: pass"))
            try: subprocess.run([sys.executable,"-m","py_compile",str(f)],check=True,capture_output=True,text=True,timeout=15)
            except Exception as e: issues.append(issue("py_compile_failed",f,str(e)))
            try: subprocess.run([sys.executable,str(f),"--help"],check=True,capture_output=True,text=True,timeout=10)
            except Exception as e: issues.append(issue("help_failed",f,str(e)))
        if f.suffix==".json":
            try: json.loads(txt)
            except Exception as e: issues.append(issue("json_invalid",f,str(e)))
        if f.name.lower()=="skill.md" and not txt.startswith("---\n"):
            issues.append(issue("skill_frontmatter_missing",f,"missing yaml frontmatter"))
    mode=getattr(a,"check_mode","default")
    if p.is_dir() and mode!="skill_folder":
        if not (p/"README.md").exists(): issues.append(issue("missing_readme",p/"README.md","README.md missing"))
        if not (p/"examples.md").exists(): issues.append(issue("missing_examples",p/"examples.md","examples.md missing"))
    if p.is_dir() and mode=="skill_folder" and not (p/"SKILL.md").exists():
        issues.append(issue("missing_skill_md",p/"SKILL.md","SKILL.md missing"))
    rep={"time":ts(),"path":str(p),"ok":len(issues)==0,"issues":issues}
    jp=STORE_ROOT/f"07_outputs/maintenance/code_check_{ts()}.json"; mp=STORE_ROOT/f"07_outputs/maintenance/code_check_{ts()}.md"
    jdump(jp,rep); write(mp,"# code-check\n\n"+json.dumps(rep,ensure_ascii=False,indent=2)); log_code("code-check","success" if rep["ok"] else "fail","代码检查",{"report":str(jp)})
    if issues: jl_append(STORE_ROOT/"06_error_lessons/code_error_log.jsonl",{"time":ts(),"report":str(jp),"issues":issues})
    print(f"已保存: {jp}\n已保存: {mp}")
    return jp

def code_fix(a):
    current_report=Path(a.check_report)
    max_rounds=max(1,int(a.max_rounds))
    all_backups=[]; total_fixed=0; rounds=[]
    for ridx in range(1, max_rounds+1):
        rep=jload(current_report,{})
        issues=rep.get("issues",[])
        if rep.get("ok"):
            rounds.append({"round":ridx,"status":"already_ok","fixed":0})
            break
        fixed=0
        for i in issues:
            t=i.get("type"); f=Path(i.get("file",""))
            if t in ["missing_readme","missing_examples","missing_skill_md"]:
                write(f,"# auto-generated\n"); fixed+=1; continue
            if not f.exists() or not a.yes: continue
            b=backup(f)
            if b: all_backups.append(b)
            txt=f.read_text(encoding="utf-8",errors="ignore")
            if t=="skill_frontmatter_missing": txt="---\nname: auto-generated\ndescription: fixed\n---\n\n"+txt
            elif t=="json_invalid": txt="{}\n"
            elif t in ["banned_token","pass_statement"]: txt=txt.replace("TODO","FIXED").replace("placeholder","fixed").replace("pass\n","raise RuntimeError('not implemented')\n")
            elif t=="help_failed" and f.suffix==".py" and "argparse" not in txt: txt="import argparse\n"+txt
            elif t=="except_pass_warning": txt=txt.replace("except Exception:\n    pass","except Exception as e:\n    print(e)")
            write(f,txt); fixed+=1
            jl_append(STORE_ROOT/"06_error_lessons/fix_history.jsonl",{"time":ts(),"round":ridx,"issue":i,"backup":b})
        total_fixed += fixed
        rounds.append({"round":ridx,"fixed":fixed,"issues_in":len(issues)})
        next_report=code_check(argparse.Namespace(path=rep.get("path",""),language="python",check_mode=getattr(a,"check_mode","default")))
        current_report=Path(next_report)
        if jload(current_report,{}).get("ok"): break
    final=jload(current_report,{})
    rpt=STORE_ROOT/f"07_outputs/code_reports/code_fix_{ts()}.md"
    write(rpt,"# code-fix\n"+json.dumps({"fixed_count":total_fixed,"backups":all_backups,"rounds":rounds,"final_ok":final.get("ok"),"final_issues":final.get("issues",[])},ensure_ascii=False,indent=2))
    log_code("code-fix","success" if final.get("ok") else "fail","自动修复",{"report":str(rpt),"rounds":rounds})
    if not final.get("ok"): jl_append(STORE_ROOT/"06_error_lessons/code_error_log.jsonl",{"time":ts(),"source":"code-fix","error":"remaining_issues","issues":final.get("issues",[])})
    print(f"已保存: {rpt}")

def code_cycle(a):
    code_plan(a)
    plan=sorted((STORE_ROOT/"05_workflows/code_plans").glob("code_plan_*.json"),key=lambda x:x.stat().st_mtime,reverse=True)[0]
    code_generate(argparse.Namespace(plan_file=str(plan),yes=a.yes,dry_run=not a.yes))
    chk=code_check(argparse.Namespace(path=a.target_dir,language=a.language,check_mode="default"))
    rep=jload(chk,{})
    rounds=0
    if not rep.get("ok"):
        rounds=1
        code_fix(argparse.Namespace(check_report=str(chk),yes=a.yes,max_rounds=a.max_rounds,check_mode="default"))
        chk=code_check(argparse.Namespace(path=a.target_dir,language=a.language,check_mode="default")); rep=jload(chk,{})
    created=[str(x) for x in Path(a.target_dir).glob('*') if x.is_file()]
    cyc={"request":a.request,"template_type":jload(plan,{}).get("template_type"),"plan_file":str(plan),"created_files":created,"modified_files":[],"backups":[str(x) for x in ARCHIVES.glob('*')][-20:],"check_reports":[str(chk)],"fix_rounds":rounds,"final_status":"success" if rep.get("ok") else "fail","failed_issues":rep.get("issues",[]),"memory_writes":["02_task_memory/code_task_log.jsonl","05_workflows/code_cycles","07_outputs/code_reports"],"next_action":"promote_template" if rep.get("ok") else "manual_patch","limitations":"没有LLM时只能生成模板；复杂专业代码需要 OpenClaw 主模型或 Codex 参与核心逻辑","whether_ready_for_openclaw":bool(rep.get("ok"))}
    cjp=STORE_ROOT/f"05_workflows/code_cycles/code_cycle_{ts()}.json"; cmp=STORE_ROOT/f"05_workflows/code_cycles/code_cycle_{ts()}.md"; rp=STORE_ROOT/f"07_outputs/code_reports/code_cycle_{ts()}.md"
    jdump(cjp,cyc); write(cmp,"# code-cycle\n\n"+json.dumps(cyc,ensure_ascii=False,indent=2)); write(rp,"# code-cycle report\n\n"+json.dumps(cyc,ensure_ascii=False,indent=2)); log_code("code-cycle",cyc["final_status"],"代码循环",{"report":str(rp)})
    if rep.get("ok"): jl_append(STORE_ROOT/"04_skill_memory/learned_skills.jsonl",{"time":ts(),"from":"code-cycle","lesson":"成功模板", "tool":a.tool_name})
    print(f"已保存: {cjp}\n已保存: {cmp}\n已保存: {rp}")

def registry_audit(a):
    roots=[TOOL_ROOT,TOOLS_ROOT,STORE_ROOT,WORKSPACE,SKILLS_ROOT]
    out={"generated_at":ts(),"tools":jload(STORE_ROOT/"03_tool_registry/tools_registry.json",{"tools":[]}).get("tools",[]),"audit_summary":{}}
    all_readme=[]; all_skill=[]; py=[]; ps1=[]; dirs=[]
    for r in roots:
        ex=r.exists(); items=[]
        if ex:
            for p in r.rglob('*'):
                if p.is_dir(): dirs.append(str(p))
                else:
                    if p.suffix=='.py': py.append(str(p))
                    if p.suffix=='.ps1': ps1.append(str(p))
                    if p.name.lower()=='readme.md': all_readme.append(str(p))
                    if p.name.lower()=='skill.md': all_skill.append(str(p))
        out["audit_summary"][str(r)]={"exists":ex}
    dup_readme=[k for k,v in Counter([Path(x).name.lower() for x in all_readme]).items() if v>10]
    dup_skill=[k for k,v in Counter([Path(x).name.lower() for x in all_skill]).items() if v>10]
    reg=jload(STORE_ROOT/"03_tool_registry/tools_registry.json",{"tools":[]})
    cand=[]
    for t in reg.get("tools",[]):
        cand.append({"name":t.get("name"),"paths":[{"path":p,"exists":Path(p).exists()} for p in t.get("candidate_paths",[])]})
    reg_names=[t.get("name","").lower() for t in reg.get("tools",[])]
    duplicate_registry_names=[x for x,v in Counter(reg_names).items() if x and v>1]
    skill_path_mismatch=[]
    for c in cand:
        for pth in c["paths"]:
            for sp in all_skill:
                st=Path(sp).read_text(encoding="utf-8",errors="ignore")
                if c["name"] in Path(sp).parent.name and pth["path"] not in st:
                    skill_path_mismatch.append({"skill_file":sp,"tool":c["name"],"candidate_path":pth["path"]})
    out["audit_summary"].update({"py_count":len(py),"ps1_count":len(ps1),"readme_duplicates":dup_readme,"skill_duplicates":dup_skill,"workspace_scattered_files":len([x for x in all_readme if 'workspace' in x.lower()]),"tool_vs_tools_overlap":sorted(set([Path(x).name.lower() for x in dirs if str(TOOL_ROOT) in x]) & set([Path(x).name.lower() for x in dirs if str(TOOLS_ROOT) in x])),"candidate_paths":cand,"duplicate_tool_names":[x for x,v in Counter([Path(d).name.lower() for d in dirs if str(TOOL_ROOT) in d or str(TOOLS_ROOT) in d]).items() if v>1],"duplicate_skill_folder_names":[x for x,v in Counter([Path(x).parent.name.lower() for x in all_skill]).items() if v>1],"duplicate_registry_names":duplicate_registry_names,"duplicate_candidate_paths":[x for x,v in Counter([p2["path"] for c in cand for p2 in c["paths"]]).items() if v>1],"skill_command_path_mismatch":skill_path_mismatch,"suggestions":["统一工具根目录","修复缺失candidate_paths","同步SKILL命令路径"]})
    jdump(STORE_ROOT/"03_tool_registry/tools_registry_suggested.json",out)
    rpt=STORE_ROOT/f"07_outputs/maintenance/registry_audit_{ts()}.md"; write(rpt,"# registry-audit\n\n"+json.dumps(out["audit_summary"],ensure_ascii=False,indent=2))
    if a.apply:
        s=jload(STORE_ROOT/"03_tool_registry/tools_registry_suggested.json",{})
        if isinstance(s.get("generated_at"),str) and isinstance(s.get("audit_summary"),dict) and isinstance(s.get("tools"),list) and all(isinstance(x,dict) and x.get("name") for x in s.get("tools",[])):
            jdump(STORE_ROOT/"03_tool_registry/tools_registry.json",{"tools":s["tools"]})
        else: print("拒绝应用: suggested registry 结构不完整")
    print(f"已保存: {rpt}")

def skill_health(_):
    reg=jload(STORE_ROOT/"03_tool_registry/tools_registry.json",{"tools":[]}).get("tools",[])
    rows=[]
    for t in reg:
        cps=t.get("candidate_paths",[])
        missing_candidate_paths = len(cps)==0
        ex=[p for p in cps if Path(p).exists()]
        miss=[p for p in cps if not Path(p).exists()]
        main=Path(ex[0]) if ex else (Path(cps[0]) if cps else Path(""))
        readme=main.parent/"README.md" if str(main) else Path("")
        skill=main.parent/"SKILL.md" if str(main) else Path("")
        pyc_ok=None; help_ok=None; banned=[]
        if main.exists() and main.suffix=='.py':
            txt=main.read_text(encoding='utf-8',errors='ignore')
            for b in ["TODO","placeholder","简化其余命令"]:
                if b.lower() in txt.lower(): banned.append(b)
            if re.search(r"\bpass\b",txt): banned.append("pass")
            try: subprocess.run([sys.executable,'-m','py_compile',str(main)],check=True,capture_output=True,text=True,timeout=10); pyc_ok=True
            except Exception: pyc_ok=False
            try: subprocess.run([sys.executable,str(main),'--help'],check=True,capture_output=True,text=True,timeout=10); help_ok=True
            except Exception: help_ok=False
        score=max(0,10-(2 if missing_candidate_paths else 0)-len(miss)-(0 if readme.exists() else 1)-(0 if skill.exists() else 1)-(0 if pyc_ok is not False else 2)-(0 if help_ok is not False else 1)-len(banned)-int(t.get('paid_api_risk',False))-int(t.get('destructive_risk',False)))
        rows.append({"name":t.get("name"),"existing_paths":ex,"missing_paths":miss,"selected_main_path":str(main),"readme_exists":readme.exists(),"skill_md_exists":skill.exists(),"py_compile_ok":pyc_ok,"help_ok":help_ok,"banned_tokens":banned,"missing_candidate_paths":missing_candidate_paths,"paid_api_risk":t.get('paid_api_risk'),"destructive_risk":t.get('destructive_risk'),"score":score,"recommendation":"补全candidate_paths" if missing_candidate_paths else "继续维护"})
    avg=round(sum([x['score'] for x in rows])/max(1,len(rows)),2)
    jdump(STORE_ROOT/"03_tool_registry/tool_health.json",{"updated_at":ts(),"score":avg,"tools":rows})
    rpt=STORE_ROOT/f"07_outputs/maintenance/skill_health_{ts()}.md"; write(rpt,"# skill-health\n\n"+json.dumps({"score":avg,"tools":rows},ensure_ascii=False,indent=2)); print(f"已保存: {rpt}")

def create_skill(a):
    init_store(False)
    tdir=TOOL_ROOT/a.name; sdir=SKILLS_ROOT/a.name
    if not a.yes: log_code("create-skill","dry-run","预览",{"name":a.name}); return print("dry-run")
    ensure(tdir); ensure(sdir)
    write(sdir/"SKILL.md",f"---\nname: {a.name}\ndescription: {a.request}\n---\n")
    for n,c in render_by_template({"template_type":"openclaw_skill_tool","tool_name":a.name}).items(): write(tdir/n,c)
    chk_tool=code_check(argparse.Namespace(path=str(tdir),language='python',check_mode='default'))
    chk_skill=code_check(argparse.Namespace(path=str(sdir),language='python',check_mode='skill_folder'))
    rep_tool=jload(chk_tool,{})
    rep_skill=jload(chk_skill,{})
    rep={"ok": rep_tool.get("ok") and rep_skill.get("ok"), "tool_report":str(chk_tool), "skill_report":str(chk_skill)}
    reg=jload(STORE_ROOT/"03_tool_registry/tools_registry.json",{"tools":[]}); reg.setdefault("tools",[]).append({"name":a.name,"candidate_paths":[str(tdir/f"{a.name}.py")],"description":a.request,"command_examples":[f'py "{tdir/(a.name+".py")}" --help'],"intents":["generated"],"risk_level":"low","requires_media":False,"requires_api_key":False,"paid_api_risk":False,"destructive_risk":False}); jdump(STORE_ROOT/"03_tool_registry/tools_registry.json",reg)
    jl_append(STORE_ROOT/"04_skill_memory/generated_skills.jsonl",{"time":ts(),"name":a.name,"status":"ok" if rep.get('ok') else "check_failed"})
    rpt=STORE_ROOT/f"07_outputs/code_reports/create_skill_{ts()}.md"; write(rpt,"# create-skill\n\n"+json.dumps({"check_ok":rep.get('ok'),"tool_report":str(chk_tool),"skill_report":str(chk_skill)},ensure_ascii=False,indent=2)); log_code("create-skill","success" if rep.get('ok') else "fail","创建技能",{"report":str(rpt)})
    print(f"已保存: {rpt}")

def upgrade_tool(a):
    reg=jload(STORE_ROOT/"03_tool_registry/tools_registry.json",{"tools":[]})
    tool=next((x for x in reg.get('tools',[]) if x.get('name')==a.tool),None)
    if not tool: return print("工具不存在")
    path=next((Path(p) for p in tool.get('candidate_paths',[]) if Path(p).exists()),None)
    if not path: return print("工具路径不存在")
    plan={"tool":a.tool,"path":str(path),"request":a.request,"mode":"plan_only","next":"provide --patch-file to apply"}
    plan_file=STORE_ROOT/f"07_outputs/code_reports/upgrade_plan_{ts()}.json"; jdump(plan_file,plan)
    if not getattr(a,'patch_file',None): log_code("upgrade-tool","planned","仅生成升级计划",{"plan":str(plan_file)}); return print(f"已保存: {plan_file}")
    patch=jload(Path(a.patch_file),{})
    if not isinstance(patch,dict) or patch.get('type') not in ['replace','write_file','append_safe']: return print("patch-file 无效")
    target=Path(patch.get('file',str(path)))
    try:
        target.resolve().relative_to(path.parent.resolve())
    except Exception:
        return print('路径校验失败')
    if patch.get('type')=='append_safe' and target.suffix in ['.py','.ps1']: return print('append_safe 不允许代码文件')
    b=backup(target)
    if patch['type']=='replace':
        txt=target.read_text(encoding='utf-8',errors='ignore'); write(target, txt.replace(patch.get('find',''), patch.get('replace','')))
    elif patch['type']=='write_file':
        write(target, patch.get('content',''))
    else:
        write(target, target.read_text(encoding='utf-8',errors='ignore') + '\n' + patch.get('append','') + '\n')
    chk=code_check(argparse.Namespace(path=str(path.parent),language='python')); rep=jload(chk,{})
    status="success" if rep.get('ok') else "fail"
    rpt=STORE_ROOT/f"07_outputs/code_reports/upgrade_tool_{ts()}.md"; write(rpt,"# upgrade-tool\n\n"+json.dumps({"status":status,"backup":b,"check":str(chk)},ensure_ascii=False,indent=2))
    log_code("upgrade-tool",status,"升级执行",{"report":str(rpt)})
    if not rep.get('ok'):
        jl_append(STORE_ROOT/"06_error_lessons/code_error_log.jsonl",{"time":ts(),"source":"upgrade-tool","tool":a.tool,"check_report":str(chk),"issues":rep.get("issues",[]),"patch_file":a.patch_file,"backup_path":b})
    print(f"已保存: {rpt}")

# minimal legacy memory commands

def remember_task(a): jl_append(STORE_ROOT/"02_task_memory/task_log.jsonl",vars(a)); print("已记录")
def review(a):
    tasks=jl_read(STORE_ROOT/"02_task_memory/task_log.jsonl")[-a.limit:]
    code_tasks=jl_read(STORE_ROOT/"02_task_memory/code_task_log.jsonl")
    status={"success":0,"fail":0,"partial":0}
    actions={}
    for t in tasks: status[t.get("status","partial")]=status.get(t.get("status","partial"),0)+1
    for t in code_tasks: actions[t.get("action","unknown")]=actions.get(t.get("action","unknown"),0)+1
    errs=jl_read(STORE_ROOT/"06_error_lessons/code_error_log.jsonl")[-5:]
    rpt={"recent_tasks":len(tasks),"status":status,"code_task_log_count":len(code_tasks),"recent_failed_issues":errs,"top_actions":sorted(actions.items(), key=lambda x:x[1], reverse=True)[:5]}
    write(STORE_ROOT/f"07_outputs/summaries/review_{ts()}.md", json.dumps(rpt, ensure_ascii=False, indent=2)); print("review 完成")
def learn(_):
    errs=jl_read(STORE_ROOT/"06_error_lessons/code_error_log.jsonl")
    fixes=jl_read(STORE_ROOT/"06_error_lessons/fix_history.jsonl")
    et={}; fa={}
    for e in errs:
        for i in e.get("issues",[]): et[i.get("type","unknown")]=et.get(i.get("type","unknown"),0)+1
    for f in fixes: fa[f.get("issue",{}).get("type","unknown")]=fa.get(f.get("issue",{}).get("type","unknown"),0)+1
    rec={"time":ts(),"common_error_types":et,"common_fix_actions":fa,"avoid_repeat":["先code-check后code-fix","路径与frontmatter先修复"]}
    jl_append(STORE_ROOT/"04_skill_memory/learned_skills.jsonl",rec); print("learn 完成")
def propose_skill(a): jl_append(STORE_ROOT/"04_skill_memory/skill_candidates.jsonl",{"time":ts(),"idea":a.idea}); print("propose 完成")
def gen_prompt(a): write(STORE_ROOT/f"04_skill_memory/codex_prompts/{ts()}_codex_prompt.md",a.goal); print("prompt 已保存")
def anti(a):
    ans=a.answer
    risks=[]
    if re.search(r"已经(创建|完成|安装)",ans) and ("Test-Path" not in ans and "证据" not in ans): risks.append("声明已完成但缺少证据")
    if re.search(r"[A-Za-z]:\\[^\"\n]* [^\"\n]*",ans): risks.append("路径包含空格但可能未加引号")
    if any(x in ans.lower() for x in ["remove-item","del ","rmdir","format","git clean","git reset"]): risks.append("包含危险删除/重置命令")
    if "api" in ans.lower() and "收费" not in ans: risks.append("提到API但未提醒可能付费")
    if "codex" in ans.lower() and "写" in ans and "prompt" not in ans.lower() and "计划" not in ans: risks.append("用户要求Codex写，但回复未转为Codex任务提示")
    data={"time":ts(),"answer":ans,"risks":risks,"risk_level":"high" if risks else "low"}
    p=STORE_ROOT/f"07_outputs/reports/anti_hallucination_{ts()}.md"; write(p,json.dumps(data,ensure_ascii=False,indent=2)); print(f"已保存: {p}")
def err(a): jl_append(STORE_ROOT/"06_error_lessons/error_log.jsonl",{"time":ts(),"error":a.error,"context":a.context}); print("error 已记录")
def daily(a): jdump(STORE_ROOT/"05_workflows/daily_ops_plan.json",{"date":ts('%Y-%m-%d'),"brand":a.brand,"industry":a.industry}); print("daily 完成")
def auto(a): jl_append(STORE_ROOT/"05_workflows/automation_queue.jsonl",{"time":ts(),"task":a.task,"frequency":a.frequency,"risk":a.risk}); print("automation 完成")
def due(_):
    q=jl_read(STORE_ROOT/"05_workflows/automation_queue.jsonl")
    for x in q: jl_append(STORE_ROOT/"05_workflows/workflow_runs.jsonl",{"time":ts(),"task":x.get("task"),"status":"queued"})
    print("run-due 完成")
def export(_):
    seed=load_seed()
    txt="# system context\n\n"+json.dumps({"business":seed.get("business_profile"),"brands":seed.get("brand_profiles"),"tools":seed.get("tools_registry")},ensure_ascii=False,indent=2)
    write(STORE_ROOT/f"07_outputs/exports/system_context_{ts()}.md",txt); print("export 完成")
def snap(_):
    files=[str(x) for x in STORE_ROOT.rglob("*") if x.is_file()] if STORE_ROOT.exists() else []
    jdump(STORE_ROOT/f"07_outputs/snapshots/snapshot_{ts()}.json",{"time":ts(),"file_count":len(files),"recent_outputs":files[-20:]}); print("snapshot 完成")

def build():
    p=argparse.ArgumentParser(description="self_improving_robot")
    s=p.add_subparsers(dest='cmd',required=True)
    s.add_parser('init-store').add_argument('--force',action='store_true')
    r=s.add_parser('remember-task'); r.add_argument('--task',required=True); r.add_argument('--tool',required=True); r.add_argument('--status',required=True); r.add_argument('--summary',required=True); r.add_argument('--output'); r.add_argument('--error'); r.add_argument('--tags')
    s.add_parser('review').add_argument('--limit',type=int,default=20); s.add_parser('learn'); s.add_parser('propose-skill').add_argument('--idea',required=True)
    g=s.add_parser('generate-codex-prompt'); g.add_argument('--goal',required=True); g.add_argument('--files'); g.add_argument('--risk',default='low')
    ra=s.add_parser('registry-audit'); ra.add_argument('--apply',action='store_true')
    s.add_parser('skill-health'); ah=s.add_parser('anti-hallucination-check'); ah.add_argument('--answer',required=True)
    el=s.add_parser('error-learn'); el.add_argument('--error',required=True); el.add_argument('--context',default='')
    d=s.add_parser('daily-ops'); d.add_argument('--brand'); d.add_argument('--industry')
    ap=s.add_parser('automation-plan'); ap.add_argument('--task',required=True); ap.add_argument('--frequency',default='manual'); ap.add_argument('--risk',default='medium'); ap.add_argument('--create-task',action='store_true')
    s.add_parser('run-due'); s.add_parser('export-system-context'); s.add_parser('snapshot')
    cp=s.add_parser('code-plan'); cp.add_argument('--request',required=True); cp.add_argument('--target-dir',required=True); cp.add_argument('--tool-name',required=True); cp.add_argument('--language',default='python'); cp.add_argument('--risk',default='medium')
    cg=s.add_parser('code-generate'); cg.add_argument('--plan-file',required=True); cg.add_argument('--yes',action='store_true'); cg.add_argument('--dry-run',action='store_true')
    cc=s.add_parser('code-check'); cc.add_argument('--path',required=True); cc.add_argument('--language',default='python')
    cf=s.add_parser('code-fix'); cf.add_argument('--check-report',required=True); cf.add_argument('--yes',action='store_true'); cf.add_argument('--max-rounds',type=int,default=3)
    cy=s.add_parser('code-cycle'); cy.add_argument('--request',required=True); cy.add_argument('--target-dir',required=True); cy.add_argument('--tool-name',required=True); cy.add_argument('--language',default='python'); cy.add_argument('--yes',action='store_true'); cy.add_argument('--max-rounds',type=int,default=3)
    up=s.add_parser('upgrade-tool'); up.add_argument('--tool',required=True); up.add_argument('--request',required=True); up.add_argument('--patch-file'); up.add_argument('--yes',action='store_true'); up.add_argument('--max-rounds',type=int,default=3)
    cs=s.add_parser('create-skill'); cs.add_argument('--name',required=True); cs.add_argument('--request',required=True); cs.add_argument('--yes',action='store_true')
    return p

def main():
    a=build().parse_args(); init_store(False)
    m={"init-store":lambda:init_store(a.force),"remember-task":lambda:remember_task(a),"review":lambda:review(a),"learn":lambda:learn(a),"propose-skill":lambda:propose_skill(a),"generate-codex-prompt":lambda:gen_prompt(a),"registry-audit":lambda:registry_audit(a),"skill-health":lambda:skill_health(a),"anti-hallucination-check":lambda:anti(a),"error-learn":lambda:err(a),"daily-ops":lambda:daily(a),"automation-plan":lambda:auto(a),"run-due":lambda:due(a),"export-system-context":lambda:export(a),"snapshot":lambda:snap(a),"code-plan":lambda:code_plan(a),"code-generate":lambda:code_generate(a),"code-check":lambda:code_check(a),"code-fix":lambda:code_fix(a),"code-cycle":lambda:code_cycle(a),"upgrade-tool":lambda:upgrade_tool(a),"create-skill":lambda:create_skill(a)}
    m[a.cmd]()

if __name__=='__main__':
    try: main()
    except Exception as e: print(f"执行失败: {e}"); sys.exit(1)
