# self_improving_robot_skill

自编码工程控制器（不是独立大模型）：
- 负责计划、落盘、备份、检查、修复常见错误、写入长期记忆。
- 复杂业务代码仍需要 OpenClaw 主模型 / Codex 生成核心逻辑。

## Seed 与初始化
`init-store` 会优先读取：
1. `D:\bot\tool\self_improving_robot_skill\default_seed.json`
2. 当前目录 `default_seed.json`
3. 内置 fallback seed

`default_seed.json` 必须包含完整 tools registry（8 个工具 + 完整字段）。

## code-generate 写入控制
- 默认不写入（没有 `--yes` 时仅预览）
- `--yes` 才写入
- `--dry-run` 强制仅预览

## 关键能力
- `code-plan`：结构化计划
- `code-generate`：模板落盘与备份
- `code-check`：py_compile / --help / JSON / SKILL frontmatter
- `code-fix`：多轮修复（受 `--max-rounds` 控制）
- `code-cycle`：计划→生成→检查→修复→复检→报告
- `create-skill`：创建后检查工具目录 + workspace SKILL.md
- `registry-audit` / `skill-health`：注册表审计与健康检测

## Hello World 验收
```bash
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" init-store
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-cycle --request "创建一个测试用 hello world Python CLI 工具，支持 --name 参数，输出 Hello name" --target-dir "D:\bot\tool\hello_world_tool" --tool-name "hello_world_tool" --language python --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-check --path "D:\bot\tool\hello_world_tool"
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" create-skill --name "hello_world_skill" --request "创建 Hello World OpenClaw Skill" --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" registry-audit
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" skill-health
```

## 查看长期记忆
- 代码任务日志：`D:\bot\store\02_task_memory\code_task_log.jsonl`
- 代码报告：`D:\bot\store\07_outputs\code_reports`
- 检查报告：`D:\bot\store\07_outputs\maintenance`
