---
name: agent-control-center-skill
description: Local self-check, anti-hallucination, single-source registry lookup, tool routing, command validation, error explanation, install readiness checks, safety checks, and doctor diagnostics for the local Windows OpenClaw Telegram toolchain.
---

# Agent Control Center Skill

## Mission
This skill is the single governance layer for local Windows OpenClaw + Telegram tools.
It prevents hallucinated tool claims, validates local paths and commands, routes user requests, explains errors, and checks install readiness.

## Single Source of Truth
Use:
D:\bot\tool\agent_control_center_skill\tool_registry.json

Other tools should not create separate registries.
All routing, safety checks, preflight checks, install readiness checks, and verification-command generation should be based on this registry.

## Use This Skill When The User Asks
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
- check whether a local tool path exists
- review Test-Path / --help output
- decide whether to restart OpenClaw gateway
- decide whether a Codex-created file can be installed

## Core Commands

Default doctor:
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" doctor

Route:
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" route --user-message "{{UserMessage}}"

Check a tool:
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" check-tool --tool b2b_marketing_tool

Registry summary:
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" registry-summary

Validate a command:
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" validate-command --command "{{Command}}"

Explain an error:
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" error-explain --log "{{LogText}}"

Generate verification commands:
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" generate-verification --tool "{{ToolName}}"

Verify OpenClaw skills:
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" verify-openclaw-skills

## Routing Rules
- Tool status / install checks / PowerShell output / Codex verification -> agent_control_center_skill
- Automatic low-risk execution -> autopilot_operator_skill, but only after agent_control_center route + preflight
- International public web research -> agent_reach_safe_research
- Marketing content after research -> agent_reach_safe_research -> b2b_marketing_tool
- Image analysis / product photo / label / cap / AI artifact issues -> image_analysis_skill
- Graphic design / typography / logo / layout / banner -> graphic_design_analyzer_skill
- Disk scan / C drive / D drive / large files -> disk_cleaner, scan-only by default
- Face swap / FaceFusion -> facefusion_tools, require explicit confirmation

## Safe Research Rules
For agent_reach_safe_research:
- allow international public websites
- allow RSS
- allow YouTube metadata/subtitles
- allow GitHub public repos
- allow Reddit read-only

Block:
- XiaoHongShu
- Douyin
- Weibo
- WeChat
- Bilibili
- Zhihu
- Xueqiu
- V2EX
- Boss Zhipin
- Chinese app/social/community/video platforms
- cookies
- logged-in browser sessions
- posting
- commenting
- liking
- following
- sharing
- messaging
- account automation
- agent-reach install --env=auto
- mcporter
- Exa
- bilibili-cli

## Anti-Hallucination Principles
1. Never assume files exist. Verify with Test-Path first.
2. Never claim installed / created / ready / done without evidence.
3. Never claim OpenClaw can use a skill unless SKILL.md exists in the official skill path.
4. Never claim a Python tool is ready unless the script exists and --help works where applicable.
5. Distinguish between:
   - file exists
   - command help works
   - real subcommand works
   - OpenClaw skill installed
   - Telegram bot can call it
6. If a result is incomplete, say exactly what is missing.
7. If Codex says a task is complete, verify the formal path, not a temporary downloaded path.
8. Do not trust duplicate files such as README (1).md, SKILL (1).md, or tool (1).py as official files.
9. Do not use D:\bot\tools as the official path. Official tool root is D:\bot\tool.
10. Prefer read-only diagnostics by default.

## Safety Principles
1. For risky commands, return blocked or needs confirmation.
2. Disk cleaning must be scan-only unless the user explicitly confirms cleanup.
3. Do not run deletion commands automatically.
4. Do not expose full API keys or secrets.
5. Paths with spaces must be quoted.
6. Do not run paid API or login/cookie workflows unless explicitly requested and risk is explained.
7. For automation requests, require route + preflight before execution.

## PowerShell Review Rules
When the user pastes PowerShell output:
- identify whether Test-Path passed
- identify whether --help passed
- identify invalid choice errors
- identify missing paths
- identify command-not-recognized errors
- identify Python import/module errors
- identify encoding / GBK / Unicode errors
- identify timeout / network / proxy errors
- give the next minimal command, not a full unrelated reinstall

## Error Explanation Rules
Use error-explain when logs include:
- Path not found
- command not recognized
- ModuleNotFoundError
- ImportError
- AttributeError
- invalid choice
- 401 / 402 / 404 / 429
- timeout
- JSON parse error
- Git not a repository
- PowerShell parser errors
- GBK / Unicode codec errors

## Output Expectation
Every agent_control_center command should end with:
FILE:file:///...

If FILE output is missing, treat the run as incomplete.

## Installation Decision Rule
Before saying "can install", verify:
1. official script path exists if script_required=true
2. README exists
3. SKILL.md exists
4. SKILL.md has YAML frontmatter
5. --help works where applicable
6. command-pattern skills have required dependencies
7. no duplicate or wrong-path files are being used


## Readiness Level Guidance
Use registry readiness metadata when reporting:
- core
- recommended
- optional
- dependency

Do not present optional tool gaps as urgent if core tools are ready.
