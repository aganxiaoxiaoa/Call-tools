# Agent Reach Safe Research Skill (Read-Only)

This package defines a **strictly read-only** research skill for Agent Reach.

## Purpose
Provide a safe default workflow for research tasks without any account actions, posting, engagement, or platform automation.

## Safety Rules
- Read-only only.
- No cookies.
- No logged-in workflows.
- No posting, commenting, liking, following, sharing, or messaging.
- No Chinese app platforms.
- Do not modify Agent-Reach source code.
- Do not run `agent-reach install --env=auto`.

## Allowed Tooling (Only)
1. Web page reading via **Jina Reader**
2. RSS reading
3. YouTube info/subtitle reading via **yt-dlp**
4. GitHub public repo reading via **gh**
5. Reddit read-only via **rdt-cli**

## Explicitly Disallowed Installs/Tools
Do **not** install or enable:
- `mcporter`
- `Exa`
- `bilibili-cli`
- `xiaohongshu`
- `douyin`
- `weibo`
- `xueqiu`
- `twitter` tools
- `linkedin` tools

## Example Read-Only Commands
- `curl "https://r.jina.ai/http://example.com"`
- `yt-dlp --dump-json "URL"`
- `gh repo view owner/repo --json name,description,url,stargazerCount,updatedAt`
- `rdt search "query"`
- `rdt read "url"`

## Default Usage Scope
- Web research
- GitHub public repository reading
- YouTube transcript/info reading
- Reddit read-only
- RSS-only ingestion
