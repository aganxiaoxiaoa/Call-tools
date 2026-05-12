# self_improving_robot_skill

## 系统说明
这是一个面向 Windows + OpenClaw Telegram 的“自我改进 + 自动编码 + 自动检查 + 自动修复”CLI。

## 七层架构
`D:\bot\store\01_identity` 到 `D:\bot\store\07_outputs`。

## 关键命令
- 长期记忆：`init-store` `remember-task` `review` `learn`
- 代码工程：`code-plan` `code-generate` `code-check` `code-fix` `code-cycle` `upgrade-tool` `create-skill`
- 维护：`registry-audit` `skill-health` `export-system-context`

## 安装与运行
```bash
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" --help
```

## 测试命令
```bash
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" init-store
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-plan --request "创建 hello world" --tool-name "hello_world_tool" --language python
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-cycle --request "创建 hello world CLI，支持 --name" --target-dir "D:\bot\tool\hello_world_tool" --tool-name "hello_world_tool" --language python --yes
```

## Telegram 调用建议
- 用户说“写工具”→ `code-cycle`
- 用户说“修复工具”→ `upgrade-tool`
- 用户说“检查代码”→ `code-check`
- 用户说“自动修复”→ `code-fix`

## 验收标准
1. 自动创建工具文件。
2. 自动运行 `py_compile`。
3. `--help` 可运行。
4. 生成 README/examples。
5. create-skill 生成含 YAML frontmatter 的 SKILL.md。
