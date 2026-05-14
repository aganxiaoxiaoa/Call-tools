---
name: agent-control-center-skill
description: Single-source registry lookup, tool routing, install readiness checks, safety checks, and doctor diagnostics for the local Windows OpenClaw Telegram toolchain.
---

# Agent Control Center Skill

Use this skill for:
- tool routing
- registry lookup
- install checks
- safety checks
- doctor reports

## Rules
1. Use `tool_registry.json` as the single source of truth.
2. Do not claim a tool is installed without checking registry + Test-Path + `--help` where applicable.
3. Use route and preflight before running execution-oriented tools.
4. For automatic execution requests, require autopilot to consume route/preflight output first.
5. For international public web research, route to `agent_reach_safe_research` only.
6. Block Chinese app/social platform research requests under safe research policy.

## Default command
`py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" doctor`

## Route command
`py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" route --user-message "{{UserMessage}}"`
