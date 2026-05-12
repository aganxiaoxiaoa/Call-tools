# self_improving_robot_skill

触发关键词包含：记录这次任务、从错误里学习、复盘最近任务、生成长期记忆、检查工具健康、维护技能、是否需要新建工具、生成 Codex 提示词、自动维护工具、生成今天自动运营任务、自我改进、总结当前机器人系统、导出上下文给 Grok、七层储存架构、D:\bot\store。

优先调用：
`py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" <子命令>`

规则：
1. 任务前可先调用 `agent_control_center` 或 `autopilot_operator`。
2. 任务后调用 `remember-task` 记录经验。
3. 失败后调用 `error-learn` 记录错误。
4. 每天/每周调用 `review`、`learn`、`skill-health`、`daily-ops`。
5. 询问是否需要新工具时先执行 `propose-skill`。
6. 用户明确“让 Codex 写”时，仅生成 Codex prompt，不直接写完整代码。
7. 高风险操作只生成建议，不执行。
