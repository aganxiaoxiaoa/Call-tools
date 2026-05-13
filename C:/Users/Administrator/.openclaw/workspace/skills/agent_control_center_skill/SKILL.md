---
name: agent-control-center-skill
description: Local self-check, anti-hallucination, tool routing, command validation, error explanation, and OpenClaw skill readiness inspector for the Windows Telegram bot toolchain.
---

# Agent Control Center Skill

Use this skill when the user asks:
- which tool is available
- check a tool
- can this tool be installed
- Codex says done, verify it
- judge PowerShell output
- why the bot called the wrong tool
- which tool should handle this request
- inspect OpenClaw skills
- generate verification commands
- explain an error log
- validate a command
- run a full toolchain doctor

## Default command
`py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" doctor`

## Route command
`py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" route --user-message "{{UserMessage}}"`

## Check tool command
`py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" check-tool --tool b2b_marketing_tool`

## Principles
1. Never assume files exist; verify first.
2. Never claim installed/created/ready without evidence.
3. Prefer read-only diagnostics.
4. For risky commands, return blocked or needs confirmation.
5. Keep all reports and guidance in English.
