#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import re
import shutil
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = BASE_DIR / "tool_registry.json"
SKILL_MD_PATH = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\agent_control_center_skill\SKILL.md")

DANGEROUS_PATTERNS = [r"\bremove-item\b", r"\bdel\b", r"\brmdir\b", r"\bformat\b", r"\bclean\b", r"\bkill\b", r"\bstop-process\b"]
PROTECTED_DELETE = ["openclaw.json", "credentials", "telegram", "scripts", "workspace"]


def load_registry():
    with REGISTRY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def path_exists(p: str) -> bool:
    return Path(p).exists()


def pick_existing_path(candidates):
    for p in candidates:
        if path_exists(p):
            return p
    return candidates[0] if candidates else ""


def format_md(title, rows):
    lines = [f"# {title}"]
    lines.extend(rows)
    return "\n".join(lines)


def cmd_list_tools(reg):
    rows = []
    for t in reg["tools"]:
        main_path = pick_existing_path(t["candidate_paths"])
        exists = path_exists(main_path)
        risk = "高" if (t["destructive_risk"] or t["paid_api_risk"] or (not t["safe_by_default"])) else "低"
        rows += [
            f"## {t['name']}",
            f"- 用途：{t['description']}",
            f"- 主脚本路径：`{main_path}`",
            f"- 是否存在：{'是' if exists else '不存在'}",
            f"- 推荐调用命令：`{t['command_template']}`",
            f"- 风险级别：{risk}",
        ]
    print(f"已列出 {len(reg['tools'])} 个工具。")
    print(format_md("工具清单", rows))


def cmd_check_tool(reg, tool_name):
    tool = next((x for x in reg["tools"] if x["name"] == tool_name), None)
    if not tool:
        print("工具不存在。")
        return
    selected = pick_existing_path(tool["candidate_paths"])
    script_exists = path_exists(selected)
    readme_exists = (BASE_DIR / "README.md").exists()
    skill_exists = SKILL_MD_PATH.exists()
    py_ok = shutil.which("py") is not None or shutil.which("python") is not None
    ps_ok = shutil.which("powershell") is not None or shutil.which("pwsh") is not None
    dep = "可能缺失（需在目标工具目录执行其 --help 或最小测试）"
    rows = [
        f"- 脚本路径：`{selected}`",
        f"- 脚本是否存在：{'是' if script_exists else '不存在'}",
        f"- README 是否存在：{'是' if readme_exists else '不存在'}",
        f"- workspace/SKILL.md 是否存在：{'是' if skill_exists else '不存在'}",
        f"- Python 可执行：{'是' if py_ok else '否'}",
        f"- PowerShell 可执行：{'是' if ps_ok else '否'}",
        f"- 依赖状态：{dep}",
        "- 建议：先运行 `Test-Path` 与最小参数 dry-run，再进入正式流程。",
    ]
    print(f"工具检查完成：{tool_name}")
    print(format_md(f"工具检查 - {tool_name}", rows))


def route_tool(reg, intent):
    intent_l = intent.lower()
    scored = []
    for t in reg["tools"]:
        score = sum(1 for kw in t["intents"] if kw.lower() in intent_l)
        if score > 0:
            scored.append((score, t))
    if not scored:
        print("未找到匹配工具。")
        print("# 路由结果\n- 需要确认的信息：任务目标、输入文件路径、期望输出。")
        return
    scored.sort(key=lambda x: x[0], reverse=True)
    t = scored[0][1]
    selected = pick_existing_path(t["candidate_paths"])
    missing = []
    if t["requires_media"]:
        missing.append("媒体输入路径")
    if "{task}" in t["command_template"]:
        missing.append("task")
    rows = [
        f"- 推荐工具：`{t['name']}`",
        f"- 推荐命令：`{t['command_template'].replace('{path}', selected)}`",
        f"- 需要的参数：{', '.join(missing) if missing else '无'}",
        f"- 缺失信息：{', '.join(missing) if missing else '无'}",
        f"- 是否需要用户确认：{'是' if (t['destructive_risk'] or t['paid_api_risk'] or not t['safe_by_default']) else '否'}",
    ]
    print(f"已推荐工具：{t['name']}")
    print(format_md("路由结果", rows))


def validate_command_text(command):
    issues = []
    lc = command.lower()
    if any(re.search(p, lc) for p in DANGEROUS_PATTERNS):
        issues.append("检测到危险操作关键词。")
    if "-cleansafe" in lc:
        issues.append("检测到 -CleanSafe，仍需用户确认。")
    if any(k in lc for k in PROTECTED_DELETE) and any(x in lc for x in ["del ", "remove-item", "rmdir"]):
        issues.append("命中受保护目录/文件删除规则，必须阻止。")
    if re.search(r"(api[_-]?key\s*[=:]\s*\S+)", command, re.IGNORECASE):
        issues.append("疑似包含 API Key 明文，请勿公开发送。")
    for token in re.findall(r"[A-Za-z]:\\[^\s\"]+(?:\s+[^\s\"]+)+", command):
        issues.append(f"路径包含空格但缺少引号：{token}")
    for p in re.findall(r'"([A-Za-z]:\\[^\"]+)"', command):
        if p.endswith((".py", ".ps1", ".bat")) and not path_exists(p):
            issues.append(f"引用脚本不存在：{p}")
    return issues


def cmd_validate_command(command):
    issues = validate_command_text(command)
    status = "可以执行" if not issues else "不建议执行"
    rows = [f"- 结论：{status}"] + [f"- 风险：{i}" for i in issues]
    if not issues:
        rows.append("- 建议：仍建议先 dry-run 并保留日志。")
    print(f"命令安全检查：{status}")
    print(format_md("命令校验", rows))


def cmd_preflight(task, command):
    reasons = []
    next_steps = []
    if any(k in task.lower() for k in ["删除", "清理", "覆盖"]):
        reasons.append("任务可能涉及删除/覆盖，默认仅 dry-run。")
    if any(k in task.lower() for k in ["api", "openai", "claude", "gemini"]):
        reasons.append("任务可能调用 API，需提醒潜在收费。")
    if command:
        reasons.extend(validate_command_text(command))
    status = "可以执行" if not reasons else "需要补充信息"
    if any("危险" in r or "阻止" in r for r in reasons):
        status = "不建议执行"
    next_steps.append("先确认输入/输出路径并执行 Test-Path。")
    next_steps.append("如含清理动作，先提供 dry-run 命令并等待确认。")
    rows = [f"- 结论：{status}", "- 理由："] + [f"  - {r}" for r in reasons] + ["- 建议下一步:"] + [f"  - {x}" for x in next_steps]
    print(f"预检结果：{status}")
    print(format_md("Preflight 自检", rows))


def cmd_self_check(answer):
    answer = answer or ""
    risks = []
    if "已经完成" in answer:
        risks.append("可能存在无证据完成声明。")
    if any(x in answer for x in ["del ", "Remove-Item", "rmdir"]):
        risks.append("回复中包含删除命令，存在高风险。")
    if "D:\\" in answer and "C:\\" in answer:
        risks.append("同时出现 C 盘/D 盘路径，需确认是否混淆。")
    safer = "先运行 check-tool/Test-Path，再给出执行命令；涉及 API 先提醒收费，涉及清理先 dry-run。"
    rows = ["- 风险点："] + [f"  - {r}" for r in risks] + [f"- 建议修改后的更安全回复：{safer}"]
    print("回答自检完成。")
    print(format_md("Self-check", rows))


def cmd_error_explain(log):
    patterns = {
        "Path not found": ["path not found", "cannot find path", "no such file"],
        "Module not found": ["module not found", "modulenotfounderror"],
        "401 API Key 错误": ["401", "unauthorized", "invalid api key"],
        "402 余额/额度": ["402", "payment required", "quota"],
        "404 路径/模型/接口不存在": ["404", "not found"],
        "429 限流": ["429", "rate limit"],
        "timeout": ["timeout", "timed out"],
        "JSON parse error": ["json", "parse", "expecting"],
        "PowerShell 字符串缺少终止符": ["string is missing the terminator"],
        "Unicode/乱码": ["unicode", "codec", "乱码"],
        "Git clone early EOF": ["early eof"],
        "gateway not reachable": ["gateway", "unreachable"],
        "fatal: not a git repository": ["not a git repository"]
    }
    ll = log.lower()
    hit = "未知错误"
    for k, v in patterns.items():
        if any(x in ll for x in v):
            hit = k
            break
    rows = [
        f"- 错误类型：{hit}",
        "- 可能原因：路径/依赖/权限/网络或凭证配置问题。",
        "- 最小修复步骤：先复现一次并保留完整命令+日志；再只修改一个变量重试。",
        "- 不要重复无效操作：同一失败命令连续重复前必须先改参数或路径。",
    ]
    print(f"错误解释：{hit}")
    print(format_md("错误解释", rows))


def cmd_project_map():
    scan_dirs = [
        r"D:\bot\tools", r"D:\bot\tool", r"D:\bot\video", r"D:\bot\outputs",
        r"C:\Users\Administrator\.openclaw\workspace", r"C:\Users\Administrator\.openclaw\workspace\skills"
    ]
    discovered, readmes, skills = [], [], []
    by_name = defaultdict(list)
    for d in scan_dirs:
        p = Path(d)
        if not p.exists():
            continue
        for x in p.rglob("*"):
            if x.is_file():
                by_name[x.name.lower()].append(str(x))
                if x.name.lower() == "readme.md":
                    readmes.append(str(x))
                if x.name.lower() == "skill.md":
                    skills.append(str(x))
                if x.suffix.lower() in {".py", ".ps1", ".bat"}:
                    discovered.append(str(x))
    duplicates = {k: v for k, v in by_name.items() if len(v) > 1}
    rows = [
        f"- 已发现工具脚本数：{len(discovered)}",
        f"- 重名文件数：{len(duplicates)}",
        "- README 列表："
    ] + [f"  - {r}" for r in readmes[:50]] + ["- SKILL.md 列表："] + [f"  - {s}" for s in skills[:50]] + [
        f"- 路径冲突：{'有' if duplicates else '无'}",
        "- 建议整理方式：统一以 D:\\bot\\tools\\<tool_name> 存放脚本，并保持 README/SKILL 同步。"
    ]
    print("项目地图扫描完成。")
    print(format_md("Project Map", rows))


def main():
    parser = argparse.ArgumentParser(description="agent_control_center_skill 全局自检 + 防幻觉 + 工具路由控制中心")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list-tools")
    c = sub.add_parser("check-tool")
    c.add_argument("--tool", required=True)
    r = sub.add_parser("route")
    r.add_argument("--intent", required=True)
    p = sub.add_parser("preflight")
    p.add_argument("--task", required=True)
    p.add_argument("--command")
    v = sub.add_parser("validate-command")
    v.add_argument("--command", required=True)
    s = sub.add_parser("self-check")
    s.add_argument("--answer")
    e = sub.add_parser("error-explain")
    e.add_argument("--log", required=True)
    sub.add_parser("project-map")

    args = parser.parse_args()
    reg = load_registry()

    if args.cmd == "list-tools":
        cmd_list_tools(reg)
    elif args.cmd == "check-tool":
        cmd_check_tool(reg, args.tool)
    elif args.cmd == "route":
        route_tool(reg, args.intent)
    elif args.cmd == "preflight":
        cmd_preflight(args.task, args.command)
    elif args.cmd == "validate-command":
        cmd_validate_command(args.command)
    elif args.cmd == "self-check":
        cmd_self_check(args.answer)
    elif args.cmd == "error-explain":
        cmd_error_explain(args.log)
    elif args.cmd == "project-map":
        cmd_project_map()


if __name__ == "__main__":
    main()
