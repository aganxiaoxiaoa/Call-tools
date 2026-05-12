# self_improving_robot_skill

## 系统说明
这是一个用于 Windows 本地 OpenClaw Telegram 机器人的“自我改进型机器人系统”，负责长期记忆、任务复盘、错误学习、技能建议、工具注册维护、Codex 提示词生成和自动化计划管理。

## 七层储存架构
根目录：`D:\bot\store`
- `01_identity`
- `02_task_memory`
- `03_tool_registry`
- `04_skill_memory`
- `05_workflows`
- `06_error_lessons`
- `07_outputs`

## 文件结构
- `self_improving_robot.py`：CLI 主程序
- `default_seed.json`：默认种子配置
- `SKILL.md`：OpenClaw 技能触发规则
- `examples.md`：全部子命令示例

## 子命令说明
1. `init-store`：初始化七层目录和默认文件。
2. `remember-task`：记录任务经验并更新索引/工具使用统计。
3. `review`：复盘最近 N 条任务，输出 Markdown。
4. `learn`：总结长期经验并更新 lessons。
5. `propose-skill`：判断是否需新工具，生成建议和 Codex prompt。
6. `generate-codex-prompt`：按目标生成完整 Codex 任务提示词。
7. `registry-audit`：扫描指定路径、文件冲突、candidate_paths 状态；`--apply` 仅在结构合法时应用。
8. `skill-health`：检查脚本/README/SKILL/--help/编码/风险并评分。
9. `anti-hallucination-check`：检查回复风险并输出更稳妥建议。
10. `error-learn`：错误分类、最小修复、写入错误学习库。
11. `daily-ops`：生成每日运营计划。
12. `automation-plan`：生成自动化队列，低风险可给 schtasks 建议。
13. `run-due`：只处理低风险到期任务。
14. `export-system-context`：导出系统上下文。
15. `snapshot`：输出 store 快照索引。

## 安装方式
将本目录文件部署到：
- `D:\bot\tool\self_improving_robot_skill\`
- `C:\Users\Administrator\.openclaw\workspace\skills\self_improving_robot_skill\SKILL.md`

## 测试命令
见 `examples.md` 的完整命令清单。

## Telegram 调用示例
`py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" review --limit 10`

## 如何记录任务经验
使用 `remember-task`，必填 task/tool/status/summary。

## 如何从错误中学习
使用 `error-learn --error "..." --context "..."`。

## 如何生成 Codex prompt
使用 `generate-codex-prompt --goal "..." --files "a.py,b.py" --risk low`。

## 如何维护 registry
先 `registry-audit` 生成建议，再在结构合法时 `registry-audit --apply`。

## 安全规则
- 不删除文件
- 不修改 openclaw.json
- 不调用付费 API
- 不覆盖已有工具代码
- 路径有空格必须加引号

## 验收标准
- 所有子命令可运行并有 stdout 输出。
- 报告/建议/计划写入 `D:\bot\store`。
- `--apply` 不会把 registry 覆盖为错误结构。
