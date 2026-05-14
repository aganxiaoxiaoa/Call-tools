---
name: self-improving-robot
description: Long-term memory, autonomous code writing, code validation, self-fixing, skill maintenance, task learning, and safe self-improvement for a Windows OpenClaw Telegram bot.
---

触发场景：写工具、修工具、检查代码、自动修复、长期记忆、复盘、导出上下文。

优先命令：
- 写代码：`code-cycle` / `create-skill`
- 修工具：`upgrade-tool`
- 检查：`code-check` / `skill-health`
- 复盘：`review` / `learn`

安全规则：
1. 不删除文件。
2. 不修改 openclaw.json。
3. 不调用付费 API。
4. 高风险操作仅建议并要求确认。
5. 路径有空格必须加引号。

能力边界：本 Skill 不是独立大模型；负责计划、落盘、备份、检查、修复常见错误、写入长期记忆。复杂业务逻辑代码需 OpenClaw 主模型/Codex 生成核心内容。

Registry boundary:
- agent_control_center is the only master registry.
- `D:\bot\store\03_tool_registry\tools_registry.json` is local memory cache only.
- Never directly edit `D:\bot\tool\agent_control_center_skill\tool_registry.json`.
