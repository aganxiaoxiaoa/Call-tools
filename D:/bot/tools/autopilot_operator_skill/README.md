# Autopilot Operator Skill

## 功能说明
`autopilot_operator.py` 是面向 OpenClaw Telegram 机器人的“自动化任务管家”。
它会基于任务意图自动规划、工具路由、安全分级，并且只自动执行低风险操作。

## 安装路径
- Skill 文档：`C:\Users\Administrator\.openclaw\workspace\skills\autopilot_operator_skill\SKILL.md`
- 工具脚本：`D:\bot\tools\autopilot_operator_skill\autopilot_operator.py`
- 工具注册表：`D:\bot\tools\autopilot_operator_skill\tool_registry.json`

## 工具注册表说明
`tool_registry.json` 每个工具包含：
- `name`
- `description`
- `intents`
- `candidate_paths`
- `command_templates`
- `safe_actions`
- `blocked_actions`
- `risk`
- `requires_media`
- `requires_api_key`
- `paid_api_risk`
- `destructive_risk`
- `notes`

## 如何添加新工具
1. 在 `tools` 数组新增一个对象，补全以上字段。
2. 至少提供 1 个 `candidate_paths`。
3. 给出 `command_templates`，并标记 `safe_actions` / `blocked_actions`。
4. 正确设置风险：`low` / `medium` / `high`。
5. 运行 `check` 验证路径与状态。

## 测试命令
```powershell
py "D:\bot\tools\autopilot_operator_skill\autopilot_operator.py" check
py "D:\bot\tools\autopilot_operator_skill\autopilot_operator.py" plan --task "给Veytis生成美国市场精油批发GEO内容计划"
py "D:\bot\tools\autopilot_operator_skill\autopilot_operator.py" route --intent "分析这张图的平面设计和文字排版"
py "D:\bot\tools\autopilot_operator_skill\autopilot_operator.py" run-low-risk --task "生成Juese Clothing定制卫衣30秒TikTok短视频脚本"
py "D:\bot\tools\autopilot_operator_skill\autopilot_operator.py" daily-ops --brand "Veytis" --industry "essential oils wholesale"
py "D:\bot\tools\autopilot_operator_skill\autopilot_operator.py" explain-result --log "fatal: not a git repository"
```

## Telegram 调用示例
- 「自动帮我处理今天的独立站内容任务」→ 先 `plan`，再执行 `run-low-risk`。
- 「分析这张图的设计和排版」+ 媒体文件 → 路由 `graphic_design_analyzer`，需要 `{{MediaPath}}`。
- 「帮我启动 Pixelle 生成视频」→ 返回 `需要用户确认`（费用/API 风险）。

## 风险分级说明
- `low`：可自动执行（例如内容生成、路径检查、错误解释、磁盘扫描）。
- `medium`：默认不自动执行，需确认（例如换脸、视频音频 API 分析）。
- `high`：严格需确认（例如可能触发付费视频生成）。

## 常见错误
- 路径不存在：先检查 `candidate_paths`。
- 依赖缺失：确认 Python 环境和 pip 安装。
- API Key 错误/配额不足：核对环境变量与账单。
- PowerShell 引号错误：路径带空格必须加引号。
- JSON 解析错误：检查逗号、引号、UTF-8 编码。
