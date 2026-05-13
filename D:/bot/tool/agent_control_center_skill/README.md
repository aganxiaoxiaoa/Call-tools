# agent_control_center_skill

## Purpose
Global self-check, anti-hallucination, tool routing, command validation, and diagnostics for a local Windows OpenClaw + Telegram bot workflow.

## Official paths
- Script: `D:\bot\tool\agent_control_center_skill\agent_control_center.py`
- Registry: `D:\bot\tool\agent_control_center_skill\tool_registry.json`
- README: `D:\bot\tool\agent_control_center_skill\README.md`
- Skill: `C:\Users\Administrator\.openclaw\workspace\skills\agent_control_center_skill\SKILL.md`

## Command list
- list-tools
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

## Examples
```powershell
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" --help
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" list-tools
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" status --deep
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" check-tool --tool b2b_marketing_tool --deep
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" check-tool --tool image_analysis_skill --run-help
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" route --user-message "Create a Veytis bulk lavender essential oil product page"
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" preflight --task "scan disk usage" --command "powershell -ExecutionPolicy Bypass -File \"D:\bot\tool\Cleaning tools\disk_cleaner.ps1\" -Scan -Top 20"
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" validate-command --command "powershell -ExecutionPolicy Bypass -File \"D:\bot\tool\Cleaning tools\disk_cleaner.ps1\" -CleanSafe -Top 20"
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" self-check --answer "The file has been installed and the bot is ready."
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" error-explain --log "fatal: not a git repository"
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" project-map
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" verify-openclaw-skills
py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" doctor
```

## Output rules
Every command writes three files under:
`D:\bot\outputs\agent_control_center\YYYYMMDD_HHMMSS`
- `<command>.md`
- `<command>.json`
- `<command>.txt`

The final stdout line is always:
`FILE:file:///D:/bot/outputs/agent_control_center/YYYYMMDD_HHMMSS/<command>.md`

## Safety rules
- Read-only inspection by default.
- No file deletion, overwrite, or system configuration changes.
- Disk cleanup is scan-only unless explicit confirmation is provided.
- Paths with spaces must be quoted.
- Never print full API keys or secrets.

## How to add tools to tool_registry.json
Add a new JSON object with required fields:
`name, category, description, intents, command_template, candidate_paths, official_script_path, readme_path, skill_path, expected_help_terms, safe_by_default, requires_media, requires_api_key, paid_api_risk, destructive_risk, notes`.

## How to check b2b_marketing_tool
1. `check-tool --tool b2b_marketing_tool --deep`
2. `generate-verification --tool b2b_marketing_tool`

## How to check image_analysis_skill
1. `check-tool --tool image_analysis_skill --run-help`
2. `generate-verification --tool image_analysis_skill`

## How to run doctor
`py "D:\bot\tool\agent_control_center_skill\agent_control_center.py" doctor`

## Common error explanations
- `Path not found`: invalid path or file missing.
- `ModuleNotFoundError`: missing Python dependency.
- `401`: API key issue.
- `402`: quota or balance issue.
- `404`: path/model/endpoint missing.
- `429`: rate limit.
- `fatal: not a git repository`: wrong directory context.
