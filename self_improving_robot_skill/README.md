# Self Improving Robot Skill

这是一个面向 Windows + OpenClaw + Telegram 的自我改进型机器人系统。

## 七层储存架构
根目录：`D:\bot\store`
- 01_identity
- 02_task_memory
- 03_tool_registry
- 04_skill_memory
- 05_workflows
- 06_error_lessons
- 07_outputs

## 安装
将 `self_improving_robot.py` 放置到：
`D:\bot\tool\self_improving_robot_skill\self_improving_robot.py`

## 子命令
支持：init-store / remember-task / review / learn / propose-skill / generate-codex-prompt / registry-audit / skill-health / anti-hallucination-check / error-learn / daily-ops / automation-plan / run-due / export-system-context / snapshot

## Telegram 调用示例
`py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" review --limit 20`

## 安全规则
- 不删除文件
- 不改 openclaw.json
- 不调用付费 API
- 默认只写入 `D:\bot\store`
