# Agent Reach Safe Research Skill (Read-Only)

This package defines a strictly read-only research skill for Agent Reach.

## Purpose
Provide a safe default workflow for public-data research without account actions or social engagement.

## Hard Safety Constraints
- Read-only only.
- No Chinese app platforms.
- No cookies.
- No logged-in browser sessions.
- No posting/commenting/liking/following/sharing/messaging.
- Do not run `agent-reach install --env=auto`.
- Do not install `mcporter`, `Exa`, `bilibili-cli`, `xiaohongshu`, `douyin`, `weibo`, `xueqiu`, `twitter` tools, or `linkedin` tools.
- Do not modify Agent-Reach source code.

## Allowed Tools (Only)
1. Web page reading via Jina Reader
2. RSS reading
3. YouTube metadata/subtitle reading via yt-dlp
4. GitHub public repo reading via gh
5. Reddit read-only via rdt-cli

## Absolute Read-Only Command Examples
- `curl.exe "https://r.jina.ai/http://example.com"`
- `"D:\bot\venvs\agent-reach\Scripts\yt-dlp.exe" --dump-json "URL"`
- `"D:\bot\github\gh.exe" repo view owner/repo --json name,description,url,stargazerCount,updatedAt`
- `"D:\bot\venvs\agent-reach\Scripts\rdt.exe" search "query"`
- `"D:\bot\venvs\agent-reach\Scripts\rdt.exe" read "url"`
- RSS: use Python `feedparser` in read-only mode only; no login/cookies.

## Default Usage Scope
- Web research
- GitHub public repository reading
- YouTube transcript/info reading
- Reddit read-only
- RSS-only ingestion

## Refusal Rule
If a user asks for Chinese app platforms, cookies, posting, commenting, liking, following, messaging, or account automation, refuse and offer a safe read-only alternative.
