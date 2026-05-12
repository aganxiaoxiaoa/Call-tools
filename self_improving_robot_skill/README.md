# self_improving_robot_skill

自编码工程控制器（不是独立大模型）：
- 可生成模板代码、落盘、备份、检查、修复常见问题、写入长期记忆。
- 复杂专业业务逻辑代码需要 OpenClaw 主模型 / Codex 参与生成核心逻辑。

## Seed 与初始化
`init-store` 会优先读取：
1. `D:\bot\tool\self_improving_robot_skill\default_seed.json`
2. 当前目录 `default_seed.json`
3. 内置 fallback seed

## 关键能力
- `code-plan`：结构化计划（包含 template_type、files、acceptance、memory_writes）
- `code-generate`：按模板落盘并备份
- `code-check`：`py_compile`、`--help`、JSON、SKILL frontmatter 检查
- `code-fix`：修复常见结构化 issue
- `code-cycle`：计划→生成→检查→修复→复检→报告
- `registry-audit`：扫描工具根目录并输出建议
- `skill-health`：检查所有 candidate_paths

## Hello World 验收
```bash
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" init-store
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-cycle --request "创建一个测试用 hello world Python CLI 工具，支持 --name 参数，输出 Hello name" --target-dir "D:\bot\tool\hello_world_tool" --tool-name "hello_world_tool" --language python --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-check --path "D:\bot\tool\hello_world_tool"
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" registry-audit
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" skill-health
```

## 查看长期记忆
- `D:\bot\store\02_task_memory`
- `D:\bot\store\05_workflows`
- `D:\bot\store\06_error_lessons`
- `D:\bot\store\07_outputs`
