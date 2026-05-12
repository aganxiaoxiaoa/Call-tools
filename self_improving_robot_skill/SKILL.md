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
