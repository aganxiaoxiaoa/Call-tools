#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

STORE_ROOT = Path(r"D:\bot\store")
TOOL_ROOT = Path(r"D:\bot\tool")
TOOLS_ALT_ROOT = Path(r"D:\bot\tools")
WORKSPACE_ROOT = Path(r"C:\Users\Administrator\.openclaw\workspace")
SKILLS_ROOT = Path(r"C:\Users\Administrator\.openclaw\workspace\skills")

DANGEROUS_TOKENS = ["Remove-Item", "del", "rmdir", "format", "taskkill", "Stop-Process", "git reset", "git clean", "CleanSafe"]


def now_str(fmt="%Y%m%d_%H%M%S"):
    return datetime.now().strftime(fmt)


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any):
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, obj: Dict[str, Any]):
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def seed_data():
    return {
        "user_profile": {
            "name": "唐文广", "language": "Chinese", "environment": "Windows + OpenClaw + Telegram",
            "working_style": "step_by_step, practical, path_sensitive",
            "safety_preferences": ["check_before_execute", "no_dangerous_delete_without_confirmation", "codex_writes_code_when_requested", "use_existing_codex_tools_not_rewrite"]
        },
        "business_profile": {"domains": ["international_b2b_independent_site_operations", "geo_seo", "blog_writing", "image_generation", "video_generation", "customer_inquiry_reply", "product_page_copy", "tool_automation"]},
        "brand_profiles": {"brands": [{"name": "Juese Clothing", "focus": ["OEM/ODM", "garment factory", "custom hoodie", "SEO/GEO"]}, {"name": "Veytis", "focus": ["bulk essential oils", "hydrosol supplier", "private label", "B2B FAQ"]}]},
        "preferences": {"rules": ["不要自己直接写代码，让 Codex 写", "用 Codex 创建的工具，不要重写", "路径必须准确", "先检查再执行", "不要乱删文件", "付费 API 先提醒", "输出中文", "路径有空格必须加引号"]},
        "anti_hallucination_rules": ["do_not_claim_file_exists_without_check", "do_not_claim_done_without_evidence", "do_not_repeat_failed_command", "do_not_treat_pr_page_as_local_file", "do_not_treat_github_merge_as_local_install", "raw_404_means_file_not_found_or_private_or_not_merged", "quote_paths_with_spaces", "if_user_says_codex_writes_code_then_provide_codex_prompt_not_code", "high_risk_requires_confirmation", "paid_api_requires_warning"],
    }


def default_tools():
    return {"tools": [
        {"name": "image_analysis_tool", "description": "通用图片分析", "candidate_paths": [r"D:\bot\tool\image_analysis_skill\image_analysis_tool.py"], "command_examples": [r'py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --help'], "intents": ["图片分析"], "risk_level": "low", "requires_media": True, "requires_api_key": False, "paid_api_risk": False, "destructive_risk": False},
        {"name": "graphic_design_tool", "description": "平面设计分析", "candidate_paths": [r"D:\bot\tool\graphic_design_analyzer_skill\graphic_design_tool.py"], "command_examples": [r'py "D:\bot\tool\graphic_design_analyzer_skill\graphic_design_tool.py" --help'], "intents": ["排版分析"], "risk_level": "low", "requires_media": True, "requires_api_key": False, "paid_api_risk": False, "destructive_risk": False},
        {"name": "facefusion_swap", "description": "人脸替换", "candidate_paths": [r"D:\bot\tool\FaceFusion tools\facefusion_swap.py"], "command_examples": [r'py "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --help'], "intents": ["face swap"], "risk_level": "medium", "requires_media": True, "requires_api_key": False, "paid_api_risk": False, "destructive_risk": False},
        {"name": "b2b_marketing_tool", "description": "B2B营销文案", "candidate_paths": [r"D:\bot\tool\Business tools\b2b_marketing_tool.py"], "command_examples": [r'py "D:\bot\tool\Business tools\b2b_marketing_tool.py" --help'], "intents": ["GEO", "SEO", "文案"], "risk_level": "low", "requires_media": False, "requires_api_key": False, "paid_api_risk": False, "destructive_risk": False},
        {"name": "content_ops", "description": "内容运营 CLI", "candidate_paths": [r"D:\bot\tool\content-ops"], "command_examples": [r'"D:\bot\tool\content-ops" --help'], "intents": ["内容运营"], "risk_level": "low", "requires_media": False, "requires_api_key": False, "paid_api_risk": False, "destructive_risk": False},
        {"name": "disk_cleaner", "description": "磁盘扫描清理", "candidate_paths": [r"D:\bot\tool\Cleaning tools\disk_cleaner.ps1"], "command_examples": [r'powershell -File "D:\bot\tool\Cleaning tools\disk_cleaner.ps1" -WhatIf'], "intents": ["维护"], "risk_level": "high", "requires_media": False, "requires_api_key": False, "paid_api_risk": False, "destructive_risk": True},
        {"name": "agent_control_center", "description": "工具路由自检", "candidate_paths": [r"D:\bot\tool\agent_control_center_skill\agent_control_center.py"], "command_examples": [r'py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" --help'], "intents": ["路由", "防幻觉"], "risk_level": "low", "requires_media": False, "requires_api_key": False, "paid_api_risk": False, "destructive_risk": False},
        {"name": "autopilot_operator", "description": "自动化任务", "candidate_paths": [r"D:\bot\tool\autopilot_operator_skill\autopilot_operator.py"], "command_examples": [r'py "D:\bot\tool\autopilot_operator_skill\autopilot_operator.py" --help'], "intents": ["自动执行"], "risk_level": "medium", "requires_media": False, "requires_api_key": False, "paid_api_risk": False, "destructive_risk": False}
    ]}


def init_store(force=False):
    s = seed_data()
    dirs = ["01_identity", "02_task_memory", "03_tool_registry", "04_skill_memory/codex_prompts", "05_workflows", "06_error_lessons", "07_outputs/reports", "07_outputs/summaries", "07_outputs/exports", "07_outputs/maintenance", "07_outputs/snapshots"]
    for d in dirs: ensure_dir(STORE_ROOT / d)
    files = {
        "01_identity/user_profile.json": s["user_profile"], "01_identity/business_profile.json": s["business_profile"], "01_identity/brand_profiles.json": s["brand_profiles"], "01_identity/preferences.json": s["preferences"],
        "03_tool_registry/tools_registry.json": default_tools(), "03_tool_registry/tool_health.json": {"score": 0, "updated_at": None}, "03_tool_registry/tool_routes.json": {"routes": []}, "03_tool_registry/tool_usage_stats.json": {},
        "05_workflows/workflow_registry.json": {"workflows": ["image_review_workflow", "graphic_design_review_workflow", "b2b_content_workflow", "disk_maintenance_workflow", "codex_tool_install_workflow", "error_debug_workflow", "daily_ops_workflow"]}, "05_workflows/daily_ops_plan.json": {"date": None, "tasks": []},
        "06_error_lessons/anti_hallucination_rules.json": {"rules": s["anti_hallucination_rules"]},
        "02_task_memory/task_index.json": {"total": 0, "by_status": {}},
    }
    text_files = ["02_task_memory/task_log.jsonl", "02_task_memory/recent_context.md", "04_skill_memory/learned_skills.jsonl", "04_skill_memory/skill_candidates.jsonl", "04_skill_memory/skill_library.md", "05_workflows/workflow_runs.jsonl", "05_workflows/automation_queue.jsonl", "06_error_lessons/error_log.jsonl", "06_error_lessons/lessons_learned.md", "06_error_lessons/failed_commands.jsonl"]
    for rel, content in files.items():
        p = STORE_ROOT / rel
        if p.exists() and not force:
            print(f"已存在: {p}")
        else:
            write_json(p, content); print(f"已创建: {p}")
    for rel in text_files:
        p = STORE_ROOT / rel
        if p.exists() and not force: print(f"已存在: {p}")
        else: p.write_text("", encoding="utf-8"); print(f"已创建: {p}")


def classify_error(err: str):
    m = err.lower()
    pairs = [("not a git repository", "not a git repository"), ("module not found", "Python ModuleNotFoundError"), ("404", "404 raw 文件不存在"), ("401", "401 API Key"), ("402", "402 余额/额度"), ("429", "429 限流"), ("timeout", "timeout")]
    for k, v in pairs:
        if k in m: return v
    return "Path not found" if "not found" in m else "unknown"


def cmd_remember(args):
    init_store(False)
    item = {"ts": now_str("%Y-%m-%d %H:%M:%S"), "task": args.task, "tool": args.tool, "status": args.status, "summary": args.summary, "output": args.output or "", "error": args.error or "", "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()]}
    append_jsonl(STORE_ROOT / "02_task_memory/task_log.jsonl", item)
    idx = read_json(STORE_ROOT / "02_task_memory/task_index.json", {"total": 0, "by_status": {}})
    idx["total"] += 1; idx["by_status"][args.status] = idx["by_status"].get(args.status, 0) + 1
    write_json(STORE_ROOT / "02_task_memory/task_index.json", idx)
    if args.status == "fail" or args.error:
        et = classify_error(args.error or args.summary)
        append_jsonl(STORE_ROOT / "06_error_lessons/error_log.jsonl", {"ts": item["ts"], "error": args.error or args.summary, "type": et, "task": args.task})
    rc = STORE_ROOT / "02_task_memory/recent_context.md"
    rc.write_text(f"- {item['ts']} | {args.tool} | {args.status} | {args.task}\n", encoding="utf-8")
    stats = read_json(STORE_ROOT / "03_tool_registry/tool_usage_stats.json", {})
    stats[args.tool] = stats.get(args.tool, 0) + 1
    write_json(STORE_ROOT / "03_tool_registry/tool_usage_stats.json", stats)
    print(f"任务已记录: {STORE_ROOT / '02_task_memory/task_log.jsonl'}")

def cmd_review(args):
    logs = read_jsonl(STORE_ROOT / "02_task_memory/task_log.jsonl")[-args.limit:]
    succ = [x for x in logs if x.get("status") == "success"][-5:]
    fail = [x for x in logs if x.get("status") == "fail"][-5:]
    tools = Counter([x.get("tool", "") for x in logs]).most_common(5)
    errs = Counter([classify_error(x.get("error", "")) for x in logs if x.get("error")]).most_common(5)
    md = ["# Review", f"时间: {now_str('%Y-%m-%d %H:%M:%S')}", "## 最近成功任务"]
    md += [f"- {x['task']} ({x['tool']})" for x in succ] or ["- 无"]
    md += ["## 最近失败任务"] + ([f"- {x['task']} | {x.get('error','')[:80]}" for x in fail] or ["- 无"]) + ["## 最常用工具"]
    md += [f"- {k}: {v}" for k, v in tools] + ["## 重复错误"] + [f"- {k}: {v}" for k, v in errs] + ["## 建议下一步", "- 每日执行 learn / skill-health / daily-ops"]
    p = STORE_ROOT / f"07_outputs/summaries/review_{now_str()}.md"; p.write_text("\n".join(md), encoding="utf-8")
    print(f"已保存: {p}")

# 简化其余命令

def write_report(name, content):
    p = STORE_ROOT / name
    ensure_dir(p.parent); p.write_text(content, encoding="utf-8"); print(f"已保存: {p}")


def cmd_learn(_):
    logs = read_jsonl(STORE_ROOT / "02_task_memory/task_log.jsonl")
    errs = read_jsonl(STORE_ROOT / "06_error_lessons/error_log.jsonl")
    rec = {"ts": now_str("%Y-%m-%d %H:%M:%S"), "common_tasks": Counter([x.get('task','') for x in logs]).most_common(5), "fail_patterns": Counter([x.get('type','') for x in errs]).most_common(5)}
    append_jsonl(STORE_ROOT / "04_skill_memory/learned_skills.jsonl", rec)
    lessons = STORE_ROOT / "06_error_lessons/lessons_learned.md"
    lessons.write_text(lessons.read_text(encoding='utf-8') + f"\n- {rec['ts']} 学习完成\n", encoding='utf-8')
    write_report(f"07_outputs/summaries/learn_summary_{now_str()}.md", "# Learn\n已总结长期经验。")

def cmd_propose(args):
    idea = args.idea
    mapping = [("博客", "b2b_marketing_tool"), ("图片", "image_analysis_tool"), ("排版", "graphic_design_tool"), ("路由", "agent_control_center"), ("自动", "autopilot_operator"), ("复盘", "self_improving_robot")]
    target = "new_tool"
    for k, t in mapping:
        if k in idea: target = t
    data = {"ts": now_str("%Y-%m-%d %H:%M:%S"), "idea": idea, "recommend": target, "need_new_tool": target == "new_tool"}
    append_jsonl(STORE_ROOT / "04_skill_memory/skill_candidates.jsonl", data)
    prompt = f"# Codex Prompt\n目标: {idea}\n建议: {'扩展 '+target if target!='new_tool' else '创建新工具'}\n"
    write_report(f"04_skill_memory/codex_prompts/{now_str()}_skill_prompt.md", prompt)

def cmd_codex(args):
    files = args.files or "(待确定)"
    txt = f"# Codex任务\n目标: {args.goal}\n风险: {args.risk}\n文件: {files}\n安全: 不删除、不改openclaw.json、不调用付费API\n测试: py \"...\" --help\n"
    write_report(f"04_skill_memory/codex_prompts/{now_str()}_codex_prompt.md", txt)

def cmd_registry(args):
    found = []
    for root in [TOOL_ROOT, TOOLS_ALT_ROOT, STORE_ROOT, WORKSPACE_ROOT, SKILLS_ROOT]:
        found.append({"path": str(root), "exists": root.exists()})
    write_json(STORE_ROOT / "03_tool_registry/tools_registry_suggested.json", {"scan": found})
    write_report(f"07_outputs/maintenance/registry_audit_{now_str()}.md", "# registry audit\n" + "\n".join([f"- {x['path']}: {'存在' if x['exists'] else '不存在'}" for x in found]))
    if args.apply:
        write_json(STORE_ROOT / "03_tool_registry/tools_registry.json", read_json(STORE_ROOT / "03_tool_registry/tools_registry_suggested.json", {}))
        print("已应用建议到 tools_registry.json")

def cmd_health(_):
    reg = read_json(STORE_ROOT / "03_tool_registry/tools_registry.json", {"tools": []}).get("tools", [])
    results = []
    ok = 0
    for t in reg:
        p = Path(t.get("candidate_paths", [""])[0]); e = p.exists(); ok += 1 if e else 0
        results.append({"name": t.get("name"), "main_exists": e})
    score = round((ok / max(1, len(reg))) * 10, 1)
    write_json(STORE_ROOT / "03_tool_registry/tool_health.json", {"score": score, "results": results, "updated_at": now_str("%Y-%m-%d %H:%M:%S")})
    write_report(f"07_outputs/maintenance/skill_health_{now_str()}.md", f"# skill health\n评分: {score}/10")

def cmd_anti(args):
    ans = args.answer
    risks = []
    if re.search(r"已经(创建|安装|完成)", ans): risks.append("声称已完成但无证据")
    if "D:\\" in ans and '"' not in ans: risks.append("路径可能未加引号")
    if any(x.lower() in ans.lower() for x in ["openclaw", "codex", "hermes"]): pass
    if any(tok.lower() in ans.lower() for tok in DANGEROUS_TOKENS): risks.append("包含危险命令")
    content = "# anti-hallucination\n" + "\n".join([f"- 风险: {r}" for r in risks] or ["- 未发现高风险"]) + "\n- 建议: 给出可验证路径与 Test-Path 检查。"
    write_report(f"07_outputs/reports/anti_hallucination_{now_str()}.md", content)

def cmd_error(args):
    t = classify_error(args.error)
    rec = {"ts": now_str("%Y-%m-%d %H:%M:%S"), "error": args.error, "type": t, "context": args.context or ""}
    append_jsonl(STORE_ROOT / "06_error_lessons/error_log.jsonl", rec)
    append_jsonl(STORE_ROOT / "06_error_lessons/failed_commands.jsonl", {"ts": rec["ts"], "error": args.error})
    lessons = STORE_ROOT / "06_error_lessons/lessons_learned.md"
    lessons.write_text(lessons.read_text(encoding="utf-8") + f"\n- {t}: 检查路径/权限/输入格式后重试。\n", encoding="utf-8")
    print(f"错误类型: {t}")

def cmd_daily(args):
    plan = {"date": now_str("%Y-%m-%d"), "brand": args.brand or "", "industry": args.industry or "", "tasks": ["GEO/SEO内容", "图片视频任务", "客户转化跟进", "工具维护"]}
    write_json(STORE_ROOT / "05_workflows/daily_ops_plan.json", plan)
    write_report(f"07_outputs/reports/daily_ops_{now_str()}.md", "# daily ops\n" + "\n".join([f"- {x}" for x in plan["tasks"]]))

def cmd_auto(args):
    item = {"ts": now_str("%Y-%m-%d %H:%M:%S"), "task": args.task, "frequency": args.frequency, "risk": args.risk, "due_at": now_str("%Y-%m-%d"), "command": ""}
    append_jsonl(STORE_ROOT / "05_workflows/automation_queue.jsonl", item)
    print("已写入自动化队列")
    if args.create_task and args.risk == "low":
        print("建议 schtasks 命令: schtasks /Create /SC DAILY /TN \"SelfImprovingRobotTask\" /TR \"py ... daily-ops\"")

def cmd_run_due(_):
    q = read_jsonl(STORE_ROOT / "05_workflows/automation_queue.jsonl")
    today = datetime.now().strftime("%Y-%m-%d")
    for i in q:
        if i.get("risk") != "low":
            print(f"等待确认: {i.get('task')}"); continue
        if i.get("due_at") > today:
            continue
        append_jsonl(STORE_ROOT / "05_workflows/workflow_runs.jsonl", {"ts": now_str("%Y-%m-%d %H:%M:%S"), "task": i.get("task"), "status": "suggested_only"})
        print(f"到期任务建议执行: {i.get('task')}")

def cmd_export(_):
    txt = "# system context\n- 业务: 国际B2B独立站\n- 品牌: Juese Clothing / Veytis\n- 七层记忆: D:\\bot\\store\n- 安全: 不删文件/不付费API/不改openclaw.json\n"
    write_report(f"07_outputs/exports/system_context_{now_str()}.md", txt)

def cmd_snapshot(_):
    files = [p for p in STORE_ROOT.rglob("*") if p.is_file()] if STORE_ROOT.exists() else []
    data = {"time": now_str("%Y-%m-%d %H:%M:%S"), "file_count": len(files), "latest_task": (read_jsonl(STORE_ROOT / "02_task_memory/task_log.jsonl") or [None])[-1], "latest_error": (read_jsonl(STORE_ROOT / "06_error_lessons/error_log.jsonl") or [None])[-1], "latest_skill": (read_jsonl(STORE_ROOT / "04_skill_memory/skill_candidates.jsonl") or [None])[-1]}
    write_json(STORE_ROOT / f"07_outputs/snapshots/snapshot_{now_str()}.json", data); print("快照完成")


def main():
    parser = argparse.ArgumentParser(description="self_improving_robot")
    sp = parser.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init-store"); p.add_argument("--force", action="store_true")
    p = sp.add_parser("remember-task"); p.add_argument("--task", required=True); p.add_argument("--tool", required=True); p.add_argument("--status", required=True, choices=["success", "fail", "partial"]); p.add_argument("--summary", required=True); p.add_argument("--output"); p.add_argument("--error"); p.add_argument("--tags")
    p = sp.add_parser("review"); p.add_argument("--limit", type=int, default=20)
    sp.add_parser("learn")
    p = sp.add_parser("propose-skill"); p.add_argument("--idea", required=True)
    p = sp.add_parser("generate-codex-prompt"); p.add_argument("--goal", required=True); p.add_argument("--files"); p.add_argument("--risk", choices=["low", "medium", "high"], default="low")
    p = sp.add_parser("registry-audit"); p.add_argument("--apply", action="store_true")
    sp.add_parser("skill-health")
    p = sp.add_parser("anti-hallucination-check"); p.add_argument("--answer", required=True)
    p = sp.add_parser("error-learn"); p.add_argument("--error", required=True); p.add_argument("--context")
    p = sp.add_parser("daily-ops"); p.add_argument("--brand"); p.add_argument("--industry")
    p = sp.add_parser("automation-plan"); p.add_argument("--task", required=True); p.add_argument("--frequency", choices=["daily", "weekly", "manual"], default="manual"); p.add_argument("--risk", choices=["low", "medium", "high"], default="medium"); p.add_argument("--create-task", action="store_true")
    sp.add_parser("run-due"); sp.add_parser("export-system-context"); sp.add_parser("snapshot")
    a = parser.parse_args()
    try:
        if a.cmd == "init-store": init_store(a.force)
        elif a.cmd == "remember-task": cmd_remember(a)
        elif a.cmd == "review": cmd_review(a)
        elif a.cmd == "learn": cmd_learn(a)
        elif a.cmd == "propose-skill": cmd_propose(a)
        elif a.cmd == "generate-codex-prompt": cmd_codex(a)
        elif a.cmd == "registry-audit": cmd_registry(a)
        elif a.cmd == "skill-health": cmd_health(a)
        elif a.cmd == "anti-hallucination-check": cmd_anti(a)
        elif a.cmd == "error-learn": cmd_error(a)
        elif a.cmd == "daily-ops": cmd_daily(a)
        elif a.cmd == "automation-plan": cmd_auto(a)
        elif a.cmd == "run-due": cmd_run_due(a)
        elif a.cmd == "export-system-context": cmd_export(a)
        elif a.cmd == "snapshot": cmd_snapshot(a)
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
