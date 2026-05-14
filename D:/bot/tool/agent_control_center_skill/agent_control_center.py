#!/usr/bin/env python3
import argparse, json, os, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
REG = BASE / "tool_registry.json"
OUT_ROOT = Path(r"D:\bot\outputs\agent_control_center")
SKILLS_ROOT = Path(r"C:\Users\Administrator\.openclaw\workspace\skills")
PROTECTED = ["openclaw.json","workspace","credentials","telegram","scripts","project"]
DANGER = ["remove-item"," del ","rmdir","format","clean","stop-process"," kill ","rm -rf"]


def load_registry():
    return json.loads(REG.read_text(encoding="utf-8"))["tools"]

def exists(p): return Path(p).exists()
def q(p): return f'"{p}"' if " " in p else p

def new_run_dir():
    d = OUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
    d.mkdir(parents=True, exist_ok=True)
    return d

def write_reports(cmd, data, lines):
    d = new_run_dir()
    md = d / f"{cmd}.md"; js = d / f"{cmd}.json"; tx = d / f"{cmd}.txt"
    md.write_text("\n".join(lines), encoding="utf-8")
    js.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8")
    tx.write_text("\n".join(lines), encoding="utf-8")
    uri='file:///' + str(md).replace('\\','/').replace('D:/','D:/')
    print(f"FILE:{uri}")

def tool_status(t):
    script = t.get("official_script_path") or ""
    script_required = t.get("script_required", True)
    tool_type = t.get("tool_type", "script_tool")
    if t.get("name") == "ffmpeg":
        se = bool(shutil.which("ffmpeg"))
    else:
        se = exists(script) if script else False
    re_ok = exists(t.get("readme_path", ""))
    sk_ok = exists(t.get("skill_path", ""))
    dep_checks = {}
    if t.get("name") == "agent_reach_safe_research":
        dep_checks = {
            "gh_exists": exists(r"D:\bot\github\gh.exe"),
            "yt_dlp_exists": exists(r"D:\bot\venvs\agent-reach\Scripts\yt-dlp.exe"),
            "rdt_exists": exists(r"D:\bot\venvs\agent-reach\Scripts\rdt.exe")
        }
    if (not script_required) or tool_type == "command_pattern_skill":
        install_ready = bool(re_ok and sk_ok and all(dep_checks.values() or [True]))
    else:
        install_ready = bool(se and re_ok and sk_ok)
    return {
      "tool_name": t["name"], "category": t.get("category", "unknown"), "script_path": script, "readme_path": t.get("readme_path", ""), "skill_path": t.get("skill_path", ""),
      "script_required": script_required, "command_pattern_skill": tool_type == "command_pattern_skill",
      "required_for_core": t.get("required_for_core", False), "optional": t.get("optional", False), "readiness_level": t.get("readiness_level", "recommended"), "readiness_note": t.get("readiness_note", ""),
      "script_exists": se, "readme_exists": re_ok, "skill_exists": sk_ok, "dependency_checks": dep_checks, "install_ready": install_ready
    }

def run_help(path):
    if not exists(path): return False,"script not found"
    if path.lower().endswith(".py"):
        py_exec = "py" if shutil.which("py") else sys.executable
        cmd=[py_exec,path,"--help"]
    elif path.lower().endswith(".ps1"): return False,"powershell help check skipped"
    else: return False,"help not applicable"
    try:
        r=subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return r.returncode==0, (r.stdout+r.stderr)[-400:]
    except Exception as e:
        return False,str(e)

def cmd_list_tools(args, tools):
    rows=[]
    for t in tools:
        s=tool_status(t)
        rows.append(s)
    md=["# Agent Control Center Report","","## Executive Summary",f"Registered tools: {len(rows)}","","## Tool Status Table"]
    for r in rows: md += [f"- {r['tool_name']}: script_exists={r['script_exists']} install_ready={r['install_ready']}"]
    md += ["","## Problems Found","- Missing files are reported in JSON.","","## Recommended Next Actions","- Run `status --deep`.","","## Verification Commands","- py \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\" status","","## Route Suggestions","- Use route command.","","## Safety Notes","- Read-only checks by default.","","## JSON Summary","See JSON report."]
    write_reports("list-tools", {"tools":rows}, md)



def cmd_registry_summary(args, tools):
    rows=[]
    for t in tools:
        s=tool_status(t)
        level=s.get("readiness_level","recommended")
        if s["install_ready"]:
            next_action="Ready."
        elif level=="core":
            next_action="Fix this core tool first."
        elif level=="optional":
            next_action="Optional tool; fix only when this workflow is needed."
        elif level=="dependency":
            next_action="Dependency status only; do not require README/SKILL unless separately registered as a skill."
        else:
            next_action="Recommended tool; fix when this workflow is required."
        rows.append({
            "name":s["tool_name"],"ready":s["install_ready"],"readiness_level":level,"required_for_core":s.get("required_for_core",False),
            "optional":s.get("optional",False),"safe":t.get("safe_by_default",False),"requires_media":t.get("requires_media",False),
            "requires_network":t.get("requires_network",False),"requires_login":t.get("requires_login",False),
            "allows_write_actions":t.get("allows_write_actions",False),"disallowed_platforms":t.get("disallowed_platforms",[]),
            "readiness_note":s.get("readiness_note",""),"recommended_next_action":next_action
        })
    core=[r for r in rows if r["readiness_level"]=="core"]
    optional=[r for r in rows if r["readiness_level"]=="optional"]
    deps=[r for r in rows if r["readiness_level"]=="dependency"]
    all_core_ready=all(r["ready"] for r in core) if core else True
    md=["# Agent Control Center Report","","## Executive Summary",f"Registry tools: {len(rows)}","","## Core tools"]+[f"- {r['name']}: ready={r['ready']} safe={r['safe']} action={r['recommended_next_action']}" for r in core]
    md += ["","## Optional tools"]+[f"- {r['name']}: ready={r['ready']} safe={r['safe']} action={r['recommended_next_action']}" for r in optional]
    md += ["","## Dependencies"]+[f"- {r['name']}: ready={r['ready']} action={r['recommended_next_action']}" for r in deps]
    next_line="Core system is usable. Optional tools can be fixed when their workflow is needed." if all_core_ready else "Fix core_not_ready_tools first."
    md += ["","## Problems Found","- See JSON for disallowed platforms and next actions.","","## Recommended Next Actions",f"- {next_line}","","## Verification Commands","- py \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\" check-tool --tool all --deep","","## Route Suggestions","- Use route command with user message.","","## Safety Notes","- Registry is the single source of truth.","","## JSON Summary","See JSON report."]
    write_reports("registry-summary",{"registry_summary":rows},md)

def cmd_status(args, tools):
    out=[]
    for t in tools:
        s=tool_status(t); s.update({"help_checked":False,"help_ok":False,"help_error":"","expected_commands_found":[],"expected_commands_missing":[],"duplicate_or_backup_risk":False,"risk_level":"low","notes":t["notes"],"recommended_next_action":"Run check-tool --tool %s --deep"%t["name"]})
        if args.deep:
            ok,txt=run_help(s["script_path"]); s["help_checked"]=True; s["help_ok"]=ok; s["help_error"]="" if ok else txt
            terms=t.get("expected_help_terms",[])
            found=[x for x in terms if x in txt]; miss=[x for x in terms if x not in txt]
            s["expected_commands_found"]=found; s["expected_commands_missing"]=miss
        out.append(s)
    data={"status":out}
    if args.json_only:
        print(json.dumps(data,indent=2))
    md=["# Agent Control Center Report","","## Executive Summary",f"Tools checked: {len(out)}","","## Tool Status Table"]+[f"- {x['tool_name']}: ready={x['install_ready']} help_ok={x['help_ok']}" for x in out]
    md += ["","## Problems Found","- See JSON fields expected_commands_missing/help_error.","","## Recommended Next Actions","- Resolve missing script/readme/skill files.","","## Verification Commands","- py \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\" check-tool --tool all --deep","","## Route Suggestions","- Use route for user requests.","","## Safety Notes","- No destructive execution performed.","","## JSON Summary","See JSON report."]
    write_reports("status",data,md)

def cmd_check_tool(args, tools):
    names=[t["name"] for t in tools]
    selected=tools if args.tool=="all" else [t for t in tools if t["name"]==args.tool]
    if not selected: selected=[]
    out=[]
    for t in selected:
        s=tool_status(t)
        if (not s.get("script_required", True)) or s.get("command_pattern_skill", False):
            s["verification_commands"] = t.get("verification_commands", [])
        else:
            s["verification_commands"]= [f"Test-Path {q(s['script_path'])}",f"Test-Path {q(s['readme_path'])}",f"Test-Path {q(s['skill_path'])}"]
        s["next_recommended_action"]="Fix missing files" if not s["install_ready"] else "Run business workflow tests"
        if args.run_help or args.deep:
            if s.get("script_required", True) and s.get("script_path"):
                ok,txt=run_help(s["script_path"]); s["help_checked"]=True; s["help_ok"]=ok; s["help_error"]="" if ok else txt
            else:
                s["help_checked"]=False; s["help_ok"]=False; s["help_error"]="help check skipped for command_pattern_skill"
        out.append(s)
    md=["# Agent Control Center Report","","## Executive Summary",f"Checked tools: {len(out)}","","## Tool Status Table"]+[f"- {x['tool_name']}: script={x['script_exists']} readme={x['readme_exists']} skill={x['skill_exists']}" for x in out]
    md += ["","## Problems Found","- Missing files or help failures listed in JSON.","","## Recommended Next Actions","- Run listed Test-Path commands.","","## Verification Commands"]
    for x in out: md += [f"- {c}" for c in x["verification_commands"]]
    for x in out:
        if x.get("command_pattern_skill"):
            md += [f"- {x['tool_name']} command_pattern_skill=true script_required={x.get('script_required')} dependency_checks={x.get('dependency_checks')}"]
    md += ["","## Route Suggestions","- Use route command for user messages.","","## Safety Notes","- This command is read-only.","","## JSON Summary","See JSON report."]
    write_reports("check-tool",{"supported_tool_names":names,"results":out},md)

def route_logic(msg, tools):
    m=msg.lower()
    blocked_terms=["xiaohongshu","douyin","weibo","wechat","bilibili","zhihu","xueqiu","v2ex","boss zhipin","小红书","抖音","微博","微信","知乎","哔哩","雪球"]
    if any(x in m for x in blocked_terms):
        return {"recommended_tool":"blocked","reason":"Chinese app/social platform requests are disallowed for safe research.","confidence":0.99,"blocked":True}
    if any(x in m for x in ["tool status","install check","powershell output","codex verify","test-path"]):
        return {"recommended_tool":"agent_control_center_skill","reason":"Governance and verification request.","confidence":0.9,"blocked":False}
    if any(x in m for x in ["automatic task plan","low-risk execution"]):
        return {"recommended_tool":"autopilot_operator_skill","reason":"Autopilot requested; require preflight first.","confidence":0.85,"blocked":False}
    for t in tools:
        keys=[k.lower() for k in t.get("intents",[])]
        if any(k in m for k in keys):
            return {"recommended_tool":t["name"],"reason":"Matched registry intents.","confidence":0.82,"blocked":False}
    if any(x in m for x in ["international","github","reddit","youtube","rss","public website","竞品","国际网站"]):
        return {"recommended_tool":"agent_reach_safe_research","reason":"Public international research request.","confidence":0.9,"blocked":False}
    return {"recommended_tool":"content_ops","reason":"Fallback route.","confidence":0.4,"blocked":False}

def cmd_route(args,tools):
    msg=args.user_message or args.intent or ""
    r=route_logic(msg,tools)
    tool=r["recommended_tool"]; conf=r["confidence"]
    t=next((x for x in tools if x["name"]==tool),None)
    tpl=(t.get("command_templates",["py \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\" status"])[0] if t else "py \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\" status")
    caution="Blocked request" if r.get("blocked") else ("Run preflight first" if tool=="autopilot_operator_skill" else "Ask confirmation for risky operations.")
    sequence=["agent_reach_safe_research -> b2b_marketing_tool"] if ("marketing" in msg.lower() and any(x in msg.lower() for x in ["research","github","reddit","youtube","rss","international"])) else []
    data={"recommended_tool":tool,"recommended_subcommand":"check-tool" if tool=="agent_control_center_skill" else "run","recommended_command_template":tpl,"reason":r["reason"],"confidence":conf,"required_inputs":["user request"],"missing_inputs":[] if msg else ["user request"],"caution":caution,"fallback_tool":"agent_control_center_skill","should_ask_user_for_file_or_image": args.has_image=="false" and "image" in msg.lower(),"example_command":tpl,"route_sequence":sequence,"blocked":r.get("blocked",False)}
    md=["# Agent Control Center Report","","## Executive Summary",f"Routed to: {tool} (confidence={conf})","","## Tool Status Table",f"- recommended_tool: {tool}","","## Problems Found","- Missing user message." if not msg else "- None.","","## Recommended Next Actions","- Confirm required input files.","","## Verification Commands","- Run check-tool for selected tool.","","## Route Suggestions",f"- {tpl}","","## Safety Notes","- Routing result is advisory.","","## JSON Summary","See JSON report."]
    write_reports("route",data,md)

def validate(command):
    c=" "+command.lower()+" "
    warnings=[]; blocked=False; path_issues=[]
    for k in DANGER:
        if k in c: warnings.append(f"dangerous token: {k.strip()}")
    if "cleansafe" in c: warnings.append("CleanSafe requires explicit user confirmation")
    if any(p in c for p in PROTECTED) and any(x in c for x in ["remove-item"," del ","rmdir","rm -rf"]): blocked=True; warnings.append("protected path deletion attempt")
    if re.search(r"api[_-]?key\s*[=:]\s*\S+",command,re.I): warnings.append("possible plaintext API key")
    for tok in re.findall(r"[A-Za-z]:\\[^\"]*\s+[^\"]*",command):
        if f'"{tok}"' not in command: path_issues.append(tok)
    return {"risk_level":"high" if warnings else "low","blocked":blocked,"warnings":warnings,"path_issues":path_issues,"suggested_safe_version":"Use scan-only command and quote every path.","requires_user_confirmation": bool(warnings)}

def cmd_validate(args):
    data=validate(args.command)
    md=["# Agent Control Center Report","","## Executive Summary",f"risk_level={data['risk_level']} blocked={data['blocked']}","","## Tool Status Table","- N/A","","## Problems Found"]+[f"- {w}" for w in data["warnings"]] + ["","## Recommended Next Actions","- Use suggested safe version.","","## Verification Commands","- Test-Path <script>","","## Route Suggestions","- Use preflight before execution.","","## Safety Notes","- Potentially dangerous command detected.","","## JSON Summary","See JSON report."]
    write_reports("validate-command",data,md)

def cmd_preflight(args):
    reasons=[]; miss=[]; decision="safe"
    if not args.task: miss.append("task"); decision="needs_more_info"
    if args.command:
        v=validate(args.command); reasons += v["warnings"]
        if v["blocked"]: decision="blocked"
        elif v["warnings"] and decision=="safe": decision="needs_confirmation"
    if "api" in (args.task or "").lower(): reasons.append("paid API risk may exist")
    data={"decision":decision,"reasons":reasons,"missing_inputs":miss,"suggested_next_step":"Run validate-command and check-tool before execution."}
    md=["# Agent Control Center Report","","## Executive Summary",f"decision={decision}","","## Tool Status Table","- N/A","","## Problems Found"]+[f"- {x}" for x in reasons] + ["","## Recommended Next Actions",f"- {data['suggested_next_step']}","","## Verification Commands","- Run check-tool --tool target","","## Route Suggestions","- Use route for intent mapping.","","## Safety Notes","- Default behavior is inspection only.","","## JSON Summary","See JSON report."]
    write_reports("preflight",data,md)

def cmd_self_check(args):
    a=(args.answer or "").lower(); risk=[]
    for claim in ["created","installed","ready","done"]:
        if claim in a: risk.append(f"unsupported claim may require evidence: {claim}")
    if "test-path" not in a: risk.append("missing explicit verification command such as Test-Path")
    if "api" in a and "cost" not in a: risk.append("missing API cost warning")
    data={"risk_points":risk,"safer_answer_suggestions":["State what is verified vs unverified.","Run Test-Path and --help checks before claiming readiness."],"recommended_verification_commands":["Test-Path \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\"","py \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\" status"]}
    md=["# Agent Control Center Report","","## Executive Summary",f"risk_points={len(risk)}","","## Tool Status Table","- N/A","","## Problems Found"]+[f"- {x}" for x in risk] + ["","## Recommended Next Actions","- Use safer answer suggestions.","","## Verification Commands"]+[f"- {x}" for x in data["recommended_verification_commands"]]+["","## Route Suggestions","- N/A","","## Safety Notes","- Avoid unsupported completion claims.","","## JSON Summary","See JSON report."]
    write_reports("self-check",data,md)

def cmd_error(args):
    l=args.log.lower(); et="unknown"
    mapping={"Path not found":["path not found","no such file"],"ModuleNotFoundError":["modulenotfounderror"],"ImportError":["importerror"],"401 API key error":["401","unauthorized"],"402 quota or balance error":["402","quota","payment required"],"404 path/model/endpoint not found":["404","not found"],"429 rate limit":["429","rate limit"],"timeout":["timeout"],"JSON parse error":["json","parse"],"PowerShell missing string terminator":["missing the terminator"],"Unicode or mojibake issue":["unicode","codec"],"Git clone early EOF":["early eof"],"gateway not reachable":["gateway"],"fatal: not a git repository":["not a git repository"],"command not recognized":["not recognized"],"invalid choice in argparse":["invalid choice"],"AttributeError":["attributeerror"]}
    for k,v in mapping.items():
        if any(x in l for x in v): et=k; break
    data={"error_type":et,"likely_causes":["path/dependency/environment mismatch"],"minimal_fix_steps":["Run from correct directory","Verify path with Test-Path","Run --help for target tool"],"commands_to_run_next":["py \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\" status"],"repeated_actions_to_avoid":["Do not repeat same failing command without changes"]}
    md=["# Agent Control Center Report","","## Executive Summary",f"error_type={et}","","## Tool Status Table","- N/A","","## Problems Found",f"- {et}","","## Recommended Next Actions","- Apply minimal fix steps.","","## Verification Commands","- status","","## Route Suggestions","- N/A","","## Safety Notes","- Keep full logs for diagnosis.","","## JSON Summary","See JSON report."]
    write_reports("error-explain",data,md)

def cmd_project_map(args):
    roots=[r"D:\bot\tool",r"D:\bot\tools",r"D:\bot\video",r"D:\bot\outputs",r"C:\Users\Administrator\.openclaw\workspace",r"C:\Users\Administrator\.openclaw\workspace\skills"]
    py=[];ps=[];rd=[];sk=[];dirs=[]
    for r in roots:
        p=Path(r)
        if p.exists():
            dirs.append(r)
            for f in p.rglob("*"):
                if f.is_file():
                    n=f.name.lower()
                    if n.endswith(".py"): py.append(str(f))
                    if n.endswith(".ps1"): ps.append(str(f))
                    if n=="readme.md": rd.append(str(f))
                    if n=="skill.md": sk.append(str(f))
    data={"discovered_directories":dirs,"discovered_python_scripts":py[:200],"discovered_powershell_scripts":ps[:200],"readme_files":rd[:200],"skill_files":sk[:200],"duplicate_or_backup_files":[],"possible_path_conflicts":[],"recommended_cleanup_notes":["Do not delete automatically."],"official_path_suggestions":["Use D:\\bot\\tool as official root."]}
    md=["# Agent Control Center Report","","## Executive Summary",f"discovered_directories={len(dirs)}","","## Tool Status Table","- N/A","","## Problems Found","- Potential conflicts may exist between D:\\bot\\tool and D:\\bot\\tools.","","## Recommended Next Actions","- Keep official scripts in D:\\bot\\tool.","","## Verification Commands","- Test-Path checks per tool","","## Route Suggestions","- N/A","","## Safety Notes","- Map is read-only.","","## JSON Summary","See JSON report."]
    write_reports("project-map",data,md)

def cmd_verify_skills(args):
    res=[]
    if SKILLS_ROOT.exists():
        for d in SKILLS_ROOT.iterdir():
            if d.is_dir():
                sm=d/"SKILL.md"; txt=sm.read_text(encoding="utf-8",errors="ignore") if sm.exists() else ""
                fm=txt.strip().startswith("---") and "name:" in txt and "description:" in txt
                refs=re.findall(r"[A-Za-z]:\\[^\s\"\n]+",txt)
                miss=[p for p in refs if not exists(p)]
                res.append({"skill_name":d.name,"skill_md_exists":sm.exists(),"frontmatter_ok":fm,"name":d.name,"description":"present" if "description:" in txt else "missing","referenced_paths":refs,"missing_referenced_paths":miss,"risk_level":"high" if (not sm.exists() or not fm or miss) else "low","fix_suggestion":"Add missing SKILL.md/frontmatter/path references."})
    data={"skills":res}
    md=["# Agent Control Center Report","","## Executive Summary",f"skills_checked={len(res)}","","## Tool Status Table"]+[f"- {x['skill_name']}: skill_md_exists={x['skill_md_exists']} frontmatter_ok={x['frontmatter_ok']}" for x in res]
    md += ["","## Problems Found","- Missing files and bad references are listed in JSON.","","## Recommended Next Actions","- Fix high-risk skills first.","","## Verification Commands","- Test-Path SKILL.md for each skill","","## Route Suggestions","- N/A","","## Safety Notes","- No files are modified.","","## JSON Summary","See JSON report."]
    write_reports("verify-openclaw-skills",data,md)

def cmd_doctor(args,tools):
    st=[tool_status(t) for t in tools]
    ready=[x['tool_name'] for x in st if x['install_ready']]; not_ready=[x['tool_name'] for x in st if not x['install_ready']]
    core_ready=[x['tool_name'] for x in st if x.get('required_for_core') and x['install_ready']]
    core_not_ready=[x['tool_name'] for x in st if x.get('required_for_core') and not x['install_ready']]
    optional_not_ready=[x['tool_name'] for x in st if x.get('optional') and not x['install_ready']]
    dependency_status={x['tool_name']:x['install_ready'] for x in st if x.get('readiness_level')=='dependency'}
    env={"D_bot_exists":exists(r"D:\bot"),"D_bot_tool_exists":exists(r"D:\bot\tool"),"openclaw_config_exists":exists(r"C:\Users\Administrator\.openclaw\openclaw.json"),"openclaw_skills_exists":SKILLS_ROOT.exists(),"py_exists":bool(shutil.which("py") or shutil.which("python")),"powershell_exists":bool(shutil.which("powershell") or shutil.which("pwsh")),"openclaw_cmd_exists":bool(shutil.which("openclaw")),"HTTP_PROXY_exists":bool(os.getenv("HTTP_PROXY")),"HTTPS_PROXY_exists":bool(os.getenv("HTTPS_PROXY")),"DASHSCOPE_API_KEY_exists":bool(os.getenv("DASHSCOPE_API_KEY")),"LOCAL_VISION_BASE_URL_exists":bool(os.getenv("LOCAL_VISION_BASE_URL")),"LOCAL_VISION_MODEL_exists":bool(os.getenv("LOCAL_VISION_MODEL"))}
    old_tools_path_usage=[t["tool_name"] for t in st if "D:\\bot\\tools" in (t.get("script_path") or "") or "D:\\bot\\tools" in (t.get("readme_path") or "")]
    unsafe_marked_safe=[t["tool_name"] for t,treg in zip(st,tools) if treg.get("destructive_risk") and treg.get("safe_by_default")]
    recommended_actions=[]
    if not core_not_ready:
        recommended_actions.append("Core system is usable. Optional tools can be fixed only when that workflow is needed.")
    else:
        recommended_actions.append("Fix core_not_ready_tools first before wider automation.")
    if optional_not_ready:
        recommended_actions.append("Optional tools are not fully registered; defer fixes unless user requests those workflows.")
    data={"overall_status":"ready" if not core_not_ready else "partial","ready_tools":ready,"not_ready_tools":not_ready,"core_ready_tools":core_ready,"core_not_ready_tools":core_not_ready,"optional_not_ready_tools":optional_not_ready,"dependency_status":dependency_status,"missing_scripts":[x['tool_name'] for x in st if x.get('script_required',True) and not x['script_exists']],"missing_skills":[x['tool_name'] for x in st if not x['skill_exists']],"help_failed_tools":[],"duplicate_risks":[],"old_entry_risks":old_tools_path_usage,"unsafe_tools_marked_safe":unsafe_marked_safe,"environment_status":env,"recommended_next_actions":recommended_actions,"recommended_verification_commands":["py \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\" status --deep","py \"D:\\bot\\tool\\agent_control_center_skill\\agent_control_center.py\" verify-openclaw-skills"]}
    md=["# Agent Control Center Report","","## Executive Summary",f"overall_status={data['overall_status']}","","## Tool Status Table"]+[f"- {x['tool_name']}: ready={x['install_ready']}" for x in st]
    md += ["","## Problems Found"]+[f"- core_not_ready_tool: {x}" for x in core_not_ready]+[f"- optional_not_ready_tool: {x}" for x in optional_not_ready] + ["","## Recommended Next Actions"]+[f"- {x}" for x in data["recommended_next_actions"]]+["","## Verification Commands"]+[f"- {x}" for x in data["recommended_verification_commands"]]+["","## Route Suggestions","- Use route command.","","## Safety Notes","- Secrets are never printed.","","## JSON Summary","See JSON report."]
    write_reports("doctor",data,md)

def cmd_verify_command(args):
    c=args.command.strip(); lc=c.lower(); blocked=False; reason=""
    if any(x in (" "+lc+" ") for x in DANGER+["cleansafe","set-content"]): blocked=True; reason="contains blocked token"
    allowed=lc.startswith("py ") or lc.startswith("python ") or (lc.startswith("powershell ") and "-scan" in lc and "-file" in lc) or lc.startswith("openclaw config get")
    if not allowed: blocked=True; reason="not in whitelist"
    if blocked:
        data={"return_code":None,"stdout_tail":"","stderr_tail":"","last_line":"","file_output_detected":False,"success_guess":False,"blocked":True,"block_reason":reason}
    else:
        r=subprocess.run(c,shell=True,text=True,capture_output=True,timeout=args.timeout)
        out=(r.stdout or "")[-500:]; err=(r.stderr or "")[-500:]
        data={"return_code":r.returncode,"stdout_tail":out,"stderr_tail":err,"last_line":(out.splitlines()[-1] if out.splitlines() else ""),"file_output_detected":"FILE:file:///" in out,"success_guess":r.returncode==0,"blocked":False,"block_reason":""}
    md=["# Agent Control Center Report","","## Executive Summary",f"blocked={data['blocked']} success_guess={data['success_guess']}","","## Tool Status Table","- N/A","","## Problems Found",f"- block_reason: {data['block_reason']}" if data['blocked'] else "- None.","","## Recommended Next Actions","- Use whitelist-safe commands only.","","## Verification Commands","- validate-command before execution","","## Route Suggestions","- N/A","","## Safety Notes","- verify-command enforces whitelist.","","## JSON Summary","See JSON report."]
    write_reports("verify-command",data,md)

def cmd_generate_verification(args):
    t=args.tool
    reg=load_registry()
    entry=next((x for x in reg if x["name"]==t),None)
    if entry:
        cmds=entry.get("verification_commands",[])
    else:
        cmds=[]
    if not cmds and t=="b2b_marketing_tool":
        sp=r"D:\bot\tool\Business tools\b2b_marketing_tool.py"; rp=r"D:\bot\tool\Business tools\README.md"; kp=r"C:\Users\Administrator\.openclaw\workspace\skills\b2b_marketing_skill\SKILL.md"
        cmds=[f"Test-Path {q(sp)}",f"Test-Path {q(rp)}",f"Test-Path {q(kp)}",f"py {q(sp)} --help",f"py {q(sp)} product-page --brand Veytis --product \"bulk lavender essential oil\"",f"py {q(sp)} negative-keywords --campaign \"lavender oil\"",f"py {q(sp)} inquiry-reply --input inquiry.txt"]
    elif t=="image_analysis_skill":
        sp=r"D:\bot\tool\image_analysis_skill\image_analysis_tool.py"; rp=r"D:\bot\tool\image_analysis_skill\README.md"; kp=r"C:\Users\Administrator\.openclaw\workspace\skills\image_analysis_skill\SKILL.md"
        cmds=[f"Test-Path {q(sp)}",f"Test-Path {q(rp)}",f"Test-Path {q(kp)}",f"py {q(sp)} --help",f"py {q(sp)} --image \"D:\\bot\\samples\\product.jpg\" --mode full",f"py {q(sp)} --image \"D:\\bot\\samples\\product.jpg\" --mode semantic-full"]
    else:
        sp=r"D:\bot\tool\agent_control_center_skill\agent_control_center.py"; rp=r"D:\bot\tool\agent_control_center_skill\README.md"; kp=r"C:\Users\Administrator\.openclaw\workspace\skills\agent_control_center_skill\SKILL.md"
        cmds=[f"Test-Path {q(sp)}",f"Test-Path {q(rp)}",f"Test-Path {q(kp)}",f"py {q(sp)} --help",f"py {q(sp)} status",f"py {q(sp)} doctor",f"py {q(sp)} route --user-message \"Create product page\""]
    data={"tool":t,"verification_commands":cmds}
    md=["# Agent Control Center Report","","## Executive Summary",f"Generated commands for: {t}","","## Tool Status Table","- N/A","","## Problems Found","- None.","","## Recommended Next Actions","- Execute commands one by one.","","## Verification Commands"]+[f"- {c}" for c in cmds]+["","## Route Suggestions","- N/A","","## Safety Notes","- Commands are generated only; not executed.","","## JSON Summary","See JSON report."]
    write_reports("generate-verification",data,md)


def main():
    ap=argparse.ArgumentParser(description="Agent control center for local Windows OpenClaw and Telegram bot governance")
    sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("list-tools")
    sub.add_parser("registry-summary")
    s=sub.add_parser("status"); s.add_argument("--deep",action="store_true"); s.add_argument("--json-only",action="store_true"); s.add_argument("--include-auto-discovered",action="store_true")
    c=sub.add_parser("check-tool"); c.add_argument("--tool",required=True); c.add_argument("--deep",action="store_true"); c.add_argument("--run-help",action="store_true")
    r=sub.add_parser("route"); r.add_argument("--user-message"); r.add_argument("--intent"); r.add_argument("--has-image",default="false"); r.add_argument("--has-file",default="false"); r.add_argument("--language",default="auto")
    p=sub.add_parser("preflight"); p.add_argument("--task",required=True); p.add_argument("--command")
    v=sub.add_parser("validate-command"); v.add_argument("--command",required=True)
    sc=sub.add_parser("self-check"); sc.add_argument("--answer",required=True)
    e=sub.add_parser("error-explain"); e.add_argument("--log",required=True)
    sub.add_parser("project-map")
    sub.add_parser("verify-openclaw-skills")
    sub.add_parser("doctor")
    vc=sub.add_parser("verify-command"); vc.add_argument("--command",required=True); vc.add_argument("--timeout",type=int,default=30)
    gv=sub.add_parser("generate-verification"); gv.add_argument("--tool",required=True)

    args=ap.parse_args(); tools=load_registry()
    if args.cmd=="list-tools": cmd_list_tools(args,tools)
    elif args.cmd=="registry-summary": cmd_registry_summary(args,tools)
    elif args.cmd=="status": cmd_status(args,tools)
    elif args.cmd=="check-tool": cmd_check_tool(args,tools)
    elif args.cmd=="route": cmd_route(args,tools)
    elif args.cmd=="preflight": cmd_preflight(args)
    elif args.cmd=="validate-command": cmd_validate(args)
    elif args.cmd=="self-check": cmd_self_check(args)
    elif args.cmd=="error-explain": cmd_error(args)
    elif args.cmd=="project-map": cmd_project_map(args)
    elif args.cmd=="verify-openclaw-skills": cmd_verify_skills(args)
    elif args.cmd=="doctor": cmd_doctor(args,tools)
    elif args.cmd=="verify-command": cmd_verify_command(args)
    elif args.cmd=="generate-verification": cmd_generate_verification(args)

if __name__=="__main__": main()
