# agent_control_center_skill

## Single source of truth
`agent_control_center_skill` is the single master registry and governance layer for local tools.
All routing, preflight checks, safety checks, and install readiness checks must use:
`D:\bot\tool\agent_control_center_skill\tool_registry.json`

Other tools should not create separate registries.

## Official paths
- Script: `D:\bot\tool\agent_control_center_skill\agent_control_center.py`
- Registry: `D:\bot\tool\agent_control_center_skill\tool_registry.json`
- README: `D:\bot\tool\agent_control_center_skill\README.md`
- Skill: `C:\Users\Administrator\.openclaw\workspace\skills\agent_control_center_skill\SKILL.md`

## Commands
- list-tools
- registry-summary
- status
- check-tool
- route
- preflight
- validate-command
- self-check
- error-explain
- project-map
- verify-openclaw-skills
- doctor
- verify-command
- generate-verification

## Output rule
Every command must end with:
`FILE:file:///D:/bot/outputs/agent_control_center/YYYYMMDD_HHMMSS/<command>.md`

## Routing policy
- Tool status, install checks, PowerShell output checks, and Codex verification route to `agent_control_center_skill`.
- Automatic low-risk execution routes to `autopilot_operator_skill`, but only after `agent_control_center` route + preflight.
- International public web research routes to `agent_reach_safe_research`.
- Chinese app/social platform requests are blocked for safe research routing.
- Marketing content after research should follow:
  `agent_reach_safe_research -> b2b_marketing_tool`

## Safety policy
- Read-only checks by default.
- Do not claim a tool is installed without registry + Test-Path + `--help` where applicable.
- `agent_reach_safe_research` is read-only and limited to international public web sources.
- Do not use cookies, logged-in sessions, posting, commenting, account automation, or disallowed platform automation.

## Autopilot integration note
`autopilot_operator_skill` must consume route/preflight results from this tool before any execution.


## Readiness levels
- core: required for baseline operation
- recommended: useful default additions
- optional: install only when that workflow is needed
- dependency: binary/runtime dependency status

Doctor separates core vs optional readiness to avoid misleading urgent repair advice.
