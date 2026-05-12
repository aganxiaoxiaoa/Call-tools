---
name: self-improving-robot
description: Long-term memory, task learning, skill maintenance, Codex prompt generation, and safe self-improvement for a Windows OpenClaw Telegram bot.
---

# self_improving_robot_skill

## 触发规则
当用户提到以下意图时，优先调用：
- 记录这次任务
- 从这次错误里学习
- 以后不要再犯这个错误
- 复盘最近任务
- 生成长期记忆
- 检查所有工具健康
- 维护技能
- 是否需要新建工具
- 生成 Codex 提示词
- 自动维护工具
- 生成今天自动运营任务
- 自我改进
- 总结当前机器人系统
- 导出上下文给 Grok
- 七层储存架构
- D:\bot\store

## 调用命令
`py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" <subcommand>`

## 运行策略
1. 任务前可调用 `agent_control_center` 或 `autopilot_operator` 进行路由/自检。
2. 任务后调用 `remember-task` 记录经验。
3. 任务失败后调用 `error-learn` 记录错误。
4. 每日/每周调用 `review`、`learn`、`skill-health`、`daily-ops`。
5. 用户问“是否需要新工具”时先执行 `propose-skill`。
6. 用户明确“让 Codex 写”时，仅输出 Codex prompt，不直接写完整代码。
7. 高风险操作只生成建议，不执行。

## 安全规则
- 不删除文件。
- 不修改 `openclaw.json`。
- 不调用付费 API。
- 不覆盖已有工具代码。
- 路径包含空格时必须加引号。
