#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin
from urllib import robotparser

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None

BASE = Path(__file__).resolve().parent
REGISTRY = BASE / "tool_policy_registry.json"
BLOCKED = BASE / "blocked_tasks.md"


def jprint(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def load_registry():
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {"tools": []}


def truth_check(answer: str):
    issues = []
    a = answer.lower()
    patterns = {
        "无证据声称已完成": [r"already completed", r"i have already", r"已经完成", r"已为你安装"],
        "可能虚构路径/文件存在": [r"file exists", r"文件已存在", r"路径已存在"],
        "无依据宣称免费": [r"free api", r"api is free", r"完全免费"],
        "危险删除提示": [r"rm -rf", r"del /f /s /q", r"remove-item.+-recurse.+-force"],
        "暗网相关": [r"dark web", r"\.onion", r"tor"],
        "全网批量下载": [r"crawl all", r"batch download", r"全网抓取", r"批量下载全网"],
    }
    for k, plist in patterns.items():
        if any(re.search(p, a) for p in plist):
            issues.append(k)

    if "\"" not in answer and re.search(r"[A-Za-z]:\\[^\n]+\s+[^\n]+", answer):
        issues.append("路径含空格但未加引号")
    if not any(x in a for x in ["不确定", "not sure", "可能", "建议先提供", "日志", "截图"]):
        issues.append("缺少不确定性或证据请求提示")

    blocked_hit = any(i in issues for i in ["暗网相关", "全网批量下载"])
    risk = "low"
    if blocked_hit:
        risk = "blocked"
    elif len(issues) >= 4:
        risk = "high"
    elif len(issues) >= 2:
        risk = "medium"

    revised = "结论：我目前无法确认已完成该操作。请先提供日志/截图/文件路径，我再做可验证判断。"
    can_send = risk in ("low", "medium")
    jprint({"risk_level": risk, "issues": issues, "suggested_reply": revised, "can_send": can_send})


def intent_router(intent: str):
    reg = load_registry().get("tools", [])
    hit = []
    intent_l = intent.lower()
    for t in reg:
        if any(k.lower() in intent_l for k in t.get("intents", [])):
            hit.append(t)
    if not hit:
        hit = [t for t in reg if t["name"] == "truthful_research_and_tool_governor"]
    recommended = [t["name"] for t in hit]
    not_rec = [t["name"] for t in reg if t["name"] not in recommended]
    reasons = {t["name"]: f"匹配意图关键词: {', '.join([k for k in t.get('intents', []) if k.lower() in intent_l]) or '默认治理优先'}" for t in hit}
    templates = {t["name"]: (t.get("command_templates") or [""])[0] for t in hit}
    jprint({
        "recommended_tools": recommended,
        "not_recommended_tools": not_rec,
        "reasons": reasons,
        "required_parameters": {"intent": "用户任务描述"},
        "risk_level": "medium" if any(t.get("destructive_risk") == "high" for t in hit) else "low",
        "user_confirmation_required": any(t.get("destructive_risk") in ["medium", "high"] for t in hit),
        "recommended_command_template": templates,
    })


def tool_audit():
    scan_paths = [
        Path("D:/bot/tools"), Path("D:/bot/tool"), Path("D:/bot/outputs"),
        Path("C:/Users/Administrator/.openclaw/workspace"),
        Path("C:/Users/Administrator/.openclaw/workspace/skills"),
    ]
    discovered = []
    readmes, skills = {}, {}
    for base in scan_paths:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_dir():
                discovered.append(str(p))
            if p.name.lower() == "readme.md":
                readmes.setdefault(p.name.lower(), []).append(str(p))
            if p.name.upper() == "SKILL.MD":
                skills.setdefault(p.name.upper(), []).append(str(p))
    jprint({
        "discovered_skills": [d for d in discovered if "skill" in d.lower()],
        "duplicate_readme_files": readmes.get("readme.md", []),
        "duplicate_skill_files": skills.get("SKILL.MD", []),
        "inconsistent_paths": ["发现 D:/bot/tool 与 D:/bot/tools 并存，建议统一"],
        "suspicious_conflicts": ["同名工具分布在多个目录可能导致路由冲突"],
        "recommended_organization": "统一工具根目录，保持一工具一目录，README+SKILL 必备",
        "may_cause_bot_confusion": True,
    })


def preflight(task: str, command: str | None):
    text = (task + " " + (command or "")).lower()
    reasons = []
    blocked = any(x in text for x in ["dark web", ".onion", "leaked", "bypass captcha", "bypass paywall"])
    if blocked:
        reasons.append("涉及禁止行为（暗网/绕过限制/泄露数据）")
    if any(x in text for x in ["delete", "remove-item", "del ", "rm "]):
        reasons.append("可能删除文件")
    if any(x in text for x in ["api", "openai", "claude", "gemini"]):
        reasons.append("可能调用付费 API")
    if any(x in text for x in ["crawl", "scan", "download", "fetch"]):
        reasons.append("涉及网络抓取/下载，需限速和范围约束")

    status = "can_execute"
    if blocked:
        status = "blocked"
    elif reasons:
        status = "confirmation_required"
    jprint({"status": status, "reasons": reasons or ["未发现明显风险"], "next_steps": "blocked 时改用 blocked-task-explain；其余先 dry-run 并让用户确认。"})


def research_plan(args):
    kw = [
        args.topic,
        f"{args.industry or ''} competitor pricing",
        f"{args.country or ''} import policy {args.industry or ''}",
        f"{args.language or ''} long-tail keywords {args.topic}",
    ]
    jprint({
        "recommended_search_keywords": kw,
        "recommended_public_source_types": ["官方机构网站", "竞争对手产品页", "博客/FAQ", "行业新闻"],
        "official_source_priority": [".gov/.edu/.org 官方站", "监管机构", "海关/贸易公开数据"],
        "competitor_page_types": ["产品页", "价格页", "案例页", "博客页", "FAQ"],
        "geo_seo_angles": ["地区术语差异", "搜索意图分层", "本地化问答结构"],
        "sources_to_access": ["公开可访问页面（无需登录）"],
        "source_types_to_cite": ["官网 URL", "新闻 URL", "文档发布时间"],
        "search_result_template": {"query": "", "url": "", "title": "", "notes": "", "citation": ""}
    })


def _extract_page(url):
    if requests is None or BeautifulSoup is None:
        raise RuntimeError("缺少 requests/bs4 依赖")
    u = urlparse(url)
    if u.scheme not in ("http", "https") or ".onion" in u.netloc:
        raise ValueError("仅允许 http/https 且禁止 .onion")
    rp = robotparser.RobotFileParser()
    rp.set_url(f"{u.scheme}://{u.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        pass
    if not rp.can_fetch("*", url):
        raise PermissionError("robots.txt 不允许抓取")
    r = requests.get(url, timeout=20, headers={"User-Agent": "truthful-governor/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else ""
    meta = ""
    m = soup.find("meta", attrs={"name": "description"})
    if m and m.get("content"):
        meta = m["content"].strip()
    h1 = [x.get_text(" ", strip=True) for x in soup.find_all("h1")][:5]
    h2 = [x.get_text(" ", strip=True) for x in soup.find_all("h2")][:10]
    body = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))[:8000]
    return {"url": url, "fetch_time": datetime.now(timezone.utc).isoformat(), "title": title, "meta_description": meta, "h1": h1, "h2": h2, "body_summary": body[:1200], "body_text": body}


def public_web_fetch(url, output_dir=None):
    data = _extract_page(url)
    out = Path(output_dir) if output_dir else BASE / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    stamp = str(int(time.time()))
    jpath = out / f"fetch_{stamp}.json"
    mpath = out / f"fetch_{stamp}.md"
    jpath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    mpath.write_text(f"# {data['title']}\n\n- URL: {data['url']}\n- Time: {data['fetch_time']}\n\n## Meta\n{data['meta_description']}\n\n## H1\n" + "\n".join(f"- {x}" for x in data['h1']) + "\n\n## H2\n" + "\n".join(f"- {x}" for x in data['h2']) + f"\n\n## Summary\n{data['body_summary']}\n", encoding="utf-8")
    jprint({"status": "ok", "json": str(jpath), "markdown": str(mpath)})


def blocked_task_explain(task):
    jprint({
        "task": task,
        "alternatives": ["改为公开网页 OSINT", "改为官方站点与合规数据源研究"],
        "osint_directions": ["企业官网", "公开新闻", "监管公告", "行业报告"],
        "public_source_suggestions": ["政府/协会官网", "竞品公开产品页", "公开 FAQ/博客"]
    })


def answer_style():
    jprint({"rules": ["先给结论", "不确定就说我不确定", "需要文件就明确索要", "不能做就直接说明", "能做就给最小步骤", "避免冗长", "不假装已完成", "不伪造来源", "不隐瞒费用风险"]})


def source_summarize(file):
    p = Path(file)
    text = p.read_text(encoding="utf-8", errors="ignore")
    jprint({"key_facts": text[:300], "page_structure": "基于标题/段落整理", "seo_geo_opportunities": ["补充地区词", "构建 FAQ"], "reference_points": ["标题与元描述", "H1/H2 结构"], "copyright_reminder": "不得直接复制原文", "original_content_directions": ["重写观点", "加入自有案例"]})


def main():
    ap = argparse.ArgumentParser(description="truthful governor")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("truth-check"); p.add_argument("--answer", required=True)
    p = sub.add_parser("intent-router"); p.add_argument("--intent", required=True)
    sub.add_parser("tool-audit")
    p = sub.add_parser("preflight"); p.add_argument("--task", required=True); p.add_argument("--command")
    p = sub.add_parser("research-plan"); p.add_argument("--topic", required=True); p.add_argument("--country"); p.add_argument("--language"); p.add_argument("--industry"); p.add_argument("--purpose")
    p = sub.add_parser("public-web-fetch"); p.add_argument("--url", required=True); p.add_argument("--output-dir")
    p = sub.add_parser("public-site-scan"); p.add_argument("--url", required=True); p.add_argument("--max-pages", type=int, default=10); p.add_argument("--depth", type=int, default=1); p.add_argument("--output-dir")
    p = sub.add_parser("source-summarize"); p.add_argument("--file", required=True)
    p = sub.add_parser("blocked-task-explain"); p.add_argument("--task", required=True)
    sub.add_parser("answer-style")

    args = ap.parse_args()
    if args.cmd == "truth-check": truth_check(args.answer)
    elif args.cmd == "intent-router": intent_router(args.intent)
    elif args.cmd == "tool-audit": tool_audit()
    elif args.cmd == "preflight": preflight(args.task, args.command)
    elif args.cmd == "research-plan": research_plan(args)
    elif args.cmd == "public-web-fetch": public_web_fetch(args.url, args.output_dir)
    elif args.cmd == "public-site-scan":
        max_pages = max(1, min(args.max_pages, 30)); depth = max(1, min(args.depth, 2))
        jprint({"status": "planned", "url": args.url, "max_pages": max_pages, "depth": depth, "rate_limit_seconds": 2, "note": "默认仅输出计划，避免危险或过量抓取"})
    elif args.cmd == "source-summarize": source_summarize(args.file)
    elif args.cmd == "blocked-task-explain": blocked_task_explain(args.task)
    elif args.cmd == "answer-style": answer_style()

if __name__ == "__main__":
    main()
