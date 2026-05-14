---
name: agent-reach-safe-research-skill
description: Safe read-only web research skill using Jina Reader, RSS, YouTube metadata/subtitles, GitHub CLI public repo reading, and Reddit read-only CLI.
---

# agent_reach_safe_research_skill

## Mission
A safe, read-only research skill for Agent Reach focused on collecting public information only.

## Hard Safety Constraints (Must Follow)
1. Read-only only: no write/actions on external platforms.
2. No Chinese app platforms.
3. No cookies.
4. No logged-in browser sessions.
5. No posting/commenting/liking/following/sharing/messaging.
6. Do not run `agent-reach install --env=auto`.
7. Do not install `mcporter`, `Exa`, `bilibili-cli`, `xiaohongshu`, `douyin`, `weibo`, `xueqiu`, `twitter` tools, or `linkedin` tools.
8. Do not modify Agent-Reach source code.

## Allowed Tools (Only)
1. Web page reading via Jina Reader
2. RSS reading
3. YouTube metadata/subtitle reading via yt-dlp
4. GitHub public repo reading via gh
5. Reddit read-only via rdt-cli

## Approved Command Patterns (Absolute, Read-Only)
### Web page reading
```bash
curl.exe "https://r.jina.ai/http://example.com"
```

### YouTube metadata/subtitles
```bash
"D:\bot\venvs\agent-reach\Scripts\yt-dlp.exe" --dump-json "URL"
```

### GitHub public repo reading
```bash
"D:\bot\github\gh.exe" repo view owner/repo --json name,description,url,stargazerCount,updatedAt
```

### Reddit read-only
```bash
"D:\bot\venvs\agent-reach\Scripts\rdt.exe" search "query"
"D:\bot\venvs\agent-reach\Scripts\rdt.exe" read "url"
```

### RSS reading
Use Python `feedparser` in read-only mode only. Do not require login/cookies.

## Default Usage
- Web research
- GitHub public repo reading
- YouTube transcript/info extraction
- Reddit read-only browsing
- RSS-only monitoring

## Refusal Rule
If a user asks for Chinese app platforms, cookies, posting, commenting, liking, following, messaging, or account automation, refuse and offer a safe read-only alternative.
