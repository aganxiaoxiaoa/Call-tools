#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = BASE_DIR / "tool_registry.json"
DANGEROUS_KEYWORDS = [
    "cleansafe", "remove-item", " del ", " rmdir", "format", "stop-process", "taskkill", "git reset", "git clean"
]


def print_json(data: Dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def load_registry() -> List[Dict[str, Any]]:
    if not REGISTRY_FILE.exists():
        raise FileNotFoundError(f"未找到工具注册表: {REGISTRY_FILE}")
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8")).get("tools", [])


def detect_tool_path(tool: Dict[str, Any]) -> Optional[str]:
    for p in tool.get("candidate_paths", []):
        if Path(p).exists():
            return p
    return None


def match_tools_by_intent(text: str, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    hits = []
    s = text.lower()
    for t in tools:
        blob = " ".join(t.get("intents", [])).lower() + " " + t.get("name", "").lower() + " " + t.get("description", "").lower()
        if any(k.lower() in s for k in t.get("intents", [])) or t.get("name", "").lower() in s:
            hits.append(t)
        elif any(k in blob for k in s.split() if len(k) >= 2):
            hits.append(t)
    return hits[:3]


def get_risk(tool: Dict[str, Any]) -> str:
    risk = tool.get("risk", "medium")
    if isinstance(risk, dict):
        return "medium"
    return str(risk)


def need_confirm_by_task(task: str) -> Tuple[bool, str]:
    t = task.lower()
    for k in DANGEROUS_KEYWORDS:
        if k in t:
            return True, f"包含危险关键词: {k}"
    risky = ["删除", "覆盖", "安装", "下载", "api", "换脸", "pixelle", "runninghub", "视频生成", "清理"]
    if any(k in task for k in risky):
        return True, "任务可能涉及付费/破坏性/隐私风险"
    return False, "低风险候选"


def cmd_plan(args: argparse.Namespace) -> None:
    tools = load_registry()
    task = args.task.strip()
    matched = match_tools_by_intent(task, tools)
    risky, reason = need_confirm_by_task(task)
    output = {
        "任务理解": task,
        "推荐工具": [t["name"] for t in matched] or ["b2b_marketing"],
        "需要的输入": ["任务描述"] + (["{{MediaPath}}"] if any(t.get("requires_media") for t in matched) else []),
        "风险等级": "medium" if risky else "low",
        "是否可自动执行": "否" if risky else "是（仅低风险）",
        "需要用户确认的步骤": [reason] if risky else [],
        "下一步命令": f"py \"{BASE_DIR / 'autopilot_operator.py'}\" run-low-risk --task \"{task}\""
    }
    print_json(output)


def safe_exec(command: str) -> Dict[str, Any]:
    lc = command.lower()
    if any(k in lc for k in DANGEROUS_KEYWORDS):
        return {"ok": False, "msg": "拦截危险命令", "command": command}
    try:
        cp = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=180)
        return {"ok": cp.returncode == 0, "code": cp.returncode, "stdout": cp.stdout[-2000:], "stderr": cp.stderr[-2000:], "command": command}
    except Exception as e:
        return {"ok": False, "msg": f"执行异常: {e}", "command": command}


def cmd_run_low_risk(args: argparse.Namespace) -> None:
    task = args.task.strip()
    tools = load_registry()
    matched = match_tools_by_intent(task, tools)
    risky, reason = need_confirm_by_task(task)
    if risky:
        print_json({"状态": "需要确认", "原因": reason, "未执行": True})
        return
    allowed = {"b2b_marketing", "image_style_analyzer", "graphic_design_analyzer", "disk_cleaner", "agent_control_center"}
    executions = []
    for t in matched:
        if t["name"] not in allowed:
            continue
        tool_path = detect_tool_path(t)
        if not tool_path:
            executions.append({"工具": t["name"], "状态": "未找到路径", "需要修复": True})
            continue
        if t["name"] == "disk_cleaner":
            cmd = t["command_templates"]["scan"].format(tool_path=tool_path)
        elif t["name"] == "agent_control_center":
            cmd = t["command_templates"]["list-tools"].format(tool_path=tool_path)
        else:
            cmd = t["command_templates"][list(t["command_templates"].keys())[0]].format(tool_path=tool_path, task=task)
        executions.append({"工具": t["name"], "执行": safe_exec(cmd)})
    if not executions:
        print_json({"状态": "需要确认", "原因": "当前任务未匹配到可自动执行的低风险动作", "未执行": True})
        return
    print_json({"状态": "已执行低风险步骤", "结果": executions})


def cmd_check(_: argparse.Namespace) -> None:
    tools = load_registry()
    rows = []
    for t in tools:
        found = detect_tool_path(t)
        base = Path(found).parent if found else Path(t.get("candidate_paths", ["."])[0]).parent
        rows.append({
            "工具名称": t["name"],
            "是否存在": bool(found),
            "主脚本路径": found or "未找到",
            "README是否存在": (base / "README.md").exists(),
            "Skill/Workspace文件是否存在": any("skill" in str(p).lower() for p in t.get("candidate_paths", [])),
            "风险等级": get_risk(t),
            "推荐修复方式": "检查 candidate_paths 是否正确，确认脚本已部署" if not found else "正常"
        })
    print_json({"检查时间": datetime.now().isoformat(), "工具状态": rows})


def cmd_route(args: argparse.Namespace) -> None:
    tools = load_registry()
    intent = args.intent.strip()
    matched = match_tools_by_intent(intent, tools)
    if not matched:
        print_json({"推荐工具": "agent_control_center", "推荐命令模板": "route --intent", "缺失参数": ["intent"], "风险等级": "low", "是否需要确认": "否"})
        return
    t = matched[0]
    need_confirm = get_risk(t) in {"medium", "high"} or t.get("paid_api_risk") or t.get("destructive_risk")
    tpl = next(iter(t.get("command_templates", {}).values()), "")
    missing = []
    if "{{MediaPath}}" in tpl:
        missing.append("MediaPath")
    print_json({"推荐工具": t["name"], "推荐命令模板": tpl, "缺失参数": missing, "风险等级": get_risk(t), "是否需要确认": "是" if need_confirm else "否"})


def cmd_execute_plan(args: argparse.Namespace) -> None:
    plan_path = Path(args.plan_file)
    if not plan_path.exists():
        print_json({"错误": "计划文件不存在", "path": str(plan_path)})
        return
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    steps = plan.get("steps", [])
    results = []
    for idx, s in enumerate(steps, start=1):
        risk = s.get("risk", "medium")
        cmd = s.get("command", "")
        print(f"[LOG] step={idx} risk={risk} cmd={cmd}")
        if risk != "low":
            results.append({"step": idx, "状态": "需要确认", "risk": risk, "command": cmd})
            continue
        res = safe_exec(cmd)
        out_file = s.get("output_file")
        if out_file:
            res["output_exists"] = Path(out_file).exists()
        results.append({"step": idx, "结果": res})
    print_json({"执行结果": results})


def cmd_daily_ops(args: argparse.Namespace) -> None:
    brand = args.brand or "你的品牌"
    industry = args.industry or "你的行业"
    print_json({
        "品牌": brand,
        "行业": industry,
        "今日运营任务": [
            "GEO：更新3个地区落地页关键词与FAQ",
            "SEO：检查2篇旧博客的标题、内链与结构化数据",
            "内容：产出1篇博客提纲+1条30秒短视频脚本+3条图片提示词",
            "客户回复：整理今日询盘的报价模板与交期话术"
        ],
        "工具调用建议": [
            "b2b_marketing: 生成博客/FAQ/客户回复",
            "image_style_analyzer: 分析竞品图片风格",
            "agent_control_center: 路由与错误解释"
        ],
        "安全说明": "不自动调用任何付费API，不自动执行中高风险任务"
    })


def cmd_explain_result(args: argparse.Namespace) -> None:
    text = args.log or ""
    if args.file:
        p = Path(args.file)
        if not p.exists():
            print_json({"错误类型": "路径不存在", "原因": str(p), "修复步骤": ["确认文件路径", "重新执行"], "不要重复的错误操作": ["不要在路径不存在时继续调用"]})
            return
        text = p.read_text(encoding="utf-8", errors="ignore")[:4000]
    patterns = {
        "路径不存在": ["not found", "no such file", "路径不存在"],
        "依赖缺失": ["modulenotfounderror", "cannot import", "command not found"],
        "API Key错误": ["api key", "unauthorized", "invalid key"],
        "额度/费用错误": ["quota", "billing", "insufficient balance"],
        "JSON解析错误": ["jsondecodeerror", "expecting value"],
        "PowerShell引号错误": ["unexpected token", "powershell", "引号"],
        "编码乱码": ["unicode", "codec", "乱码"],
        "Git clone失败": ["fatal:", "not a git repository", "clone failed"],
        "OpenClaw gateway不可达": ["gateway", "connection refused", "timeout"]
    }
    low = text.lower()
    found = "未知错误"
    for k, vals in patterns.items():
        if any(v in low for v in vals):
            found = k
            break
    fixes = {
        "路径不存在": ["先用 Test-Path 或 Path.exists 检查", "修正绝对路径后重试"],
        "依赖缺失": ["在虚拟环境安装依赖", "确认 py/pip 指向同一解释器"],
        "API Key错误": ["检查环境变量", "确认 key 未过期且权限正确"],
        "额度/费用错误": ["检查API账单与配额", "避免自动重试付费调用"],
        "JSON解析错误": ["用 jsonlint 检查逗号/引号", "保证 UTF-8 编码"],
        "PowerShell引号错误": ["统一使用双引号包裹路径", "带空格路径必须转义"],
        "编码乱码": ["文件统一 UTF-8", "读取时加 errors='ignore'"],
        "Git clone失败": ["先进入正确仓库目录", "检查网络与仓库地址"],
        "OpenClaw gateway不可达": ["检查 gateway 进程与端口", "检查防火墙与代理"]
    }
    print_json({"错误类型": found, "原因": text[:160], "修复步骤": fixes.get(found, ["提供更完整日志", "先执行 check 再排查"]), "不要重复的错误操作": ["不要在未确认风险时自动执行危险命令"]})


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Autopilot Operator - 安全分级自动化任务管家")
    sp = p.add_subparsers(dest="cmd", required=True)

    p1 = sp.add_parser("plan", help="规划任务")
    p1.add_argument("--task", required=True)
    p1.set_defaults(func=cmd_plan)

    p2 = sp.add_parser("run-low-risk", help="执行低风险任务")
    p2.add_argument("--task", required=True)
    p2.set_defaults(func=cmd_run_low_risk)

    p3 = sp.add_parser("check", help="检查工具")
    p3.set_defaults(func=cmd_check)

    p4 = sp.add_parser("route", help="意图路由")
    p4.add_argument("--intent", required=True)
    p4.set_defaults(func=cmd_route)

    p5 = sp.add_parser("execute-plan", help="执行计划")
    p5.add_argument("--plan-file", required=True)
    p5.set_defaults(func=cmd_execute_plan)

    p6 = sp.add_parser("daily-ops", help="每日运营任务")
    p6.add_argument("--brand")
    p6.add_argument("--industry")
    p6.set_defaults(func=cmd_daily_ops)

    p7 = sp.add_parser("explain-result", help="解释执行结果")
    p7.add_argument("--log")
    p7.add_argument("--file")
    p7.set_defaults(func=cmd_explain_result)
    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
