# agent_reach_safe_research_skill

## Mission
A **safe, read-only research skill** for Agent Reach focused on collecting public information only.

## Hard Safety Constraints (Must Follow)
1. **Read-only only**: no write/actions on external platforms.
2. **No Chinese app platforms**.
3. **No cookies** and no authenticated browser sessions.
4. **No posting/commenting/liking** (also no follow/share/message).
5. **Do not run** `agent-reach install --env=auto`.
6. **Do not install**: `mcporter`, `Exa`, `bilibili-cli`, `xiaohongshu`, `douyin`, `weibo`, `xueqiu`, `twitter` tools, `linkedin` tools.
7. Do not modify Agent-Reach source code.

## Allowed Tools (Only)
1. Web page reading via Jina Reader
2. RSS reading
3. YouTube info/subtitle reading via yt-dlp
4. GitHub public repo reading via gh
5. Reddit read-only via rdt-cli

If a requested action needs any tool outside this list, refuse and offer a compliant read-only alternative.

## Approved Command Patterns
### Web page reading (Jina Reader)
```bash
curl "https://r.jina.ai/http://example.com"
```

### YouTube metadata/subtitles (read-only)
```bash
yt-dlp --dump-json "URL"
```

### GitHub public repository inspection (read-only)
```bash
gh repo view owner/repo --json name,description,url,stargazerCount,updatedAt
```

### Reddit read-only
```bash
rdt search "query"
rdt read "url"
```

### RSS reading
Use any read-only RSS fetch/parse flow that does not require login, cookies, or posting.

## Default Usage
- Web research
- GitHub public repo reading
- YouTube transcript/info extraction
- Reddit read-only browsing
- RSS-only monitoring

## Refusal Policy
Refuse requests that involve:
- posting, commenting, liking, voting, DMing, following, account growth
- login/session/cookie-dependent scraping
- Chinese app platform operations
- installation or use of disallowed tools

When refusing, provide a safe alternative using only allowed read-only tools.
