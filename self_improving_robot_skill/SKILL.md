---
name: self-improving-robot
description: Long-term memory, autonomous code writing, code validation, self-fixing, skill maintenance, task learning, and safe self-improvement for a Windows OpenClaw Telegram bot.
---

当用户要求写代码、创建工具、修复工具、检查代码、自我改进、长期记忆、从错误学习、自动维护技能时，优先调用本 Skill。

核心调用：
- 写工具：`code-cycle` 或 `create-skill`
- 修复工具：`upgrade-tool`
- 检查代码：`code-check`
- 自动修复：`code-fix`
- 长期记忆：`remember-task` / `review` / `learn`

安全规则：
1. 不删除文件。
2. 不修改 openclaw.json。
3. 不调用付费 API。
4. 高风险操作必须确认。
5. 路径有空格必须加引号。
6. 没有检查证据不得声称“已完成”。
