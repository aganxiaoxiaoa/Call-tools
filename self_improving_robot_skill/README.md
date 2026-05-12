# self_improving_robot_skill

面向 Windows + OpenClaw Telegram 的“自编码 + 长期记忆”系统。

## 七层长期记忆
根目录固定：`D:\bot\store`，包含 `01_identity` 到 `07_outputs`，并扩展 `code_plans`、`code_cycles`、`code_error_log.jsonl`、`fix_history.jsonl`、`code_reports`、`archives`。

## 核心命令
- 长期记忆：`init-store` `remember-task` `review` `learn` `snapshot`
- 工程执行：`code-plan` `code-generate` `code-check` `code-fix` `code-cycle`
- 资产维护：`create-skill` `upgrade-tool` `registry-audit` `skill-health`

## 验收命令
```bash
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" init-store
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-cycle --request "创建一个测试用 hello world Python CLI 工具，支持 --name 参数，输出 Hello name" --target-dir "D:\bot\tool\hello_world_tool" --tool-name "hello_world_tool" --language python --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-check --path "D:\bot\tool\hello_world_tool"
```

## 安全规则
- 不删除文件
- 不改 openclaw.json
- 不调用付费 API
- 高风险只建议，不自动执行
