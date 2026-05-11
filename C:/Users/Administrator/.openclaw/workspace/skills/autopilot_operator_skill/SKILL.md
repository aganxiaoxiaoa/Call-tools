# autopilot_operator_skill

## 触发优先级
当用户出现以下表达时，**优先调用 autopilot_operator_skill**：
- 自动帮我处理
- 你自己看着办
- 不用我操心
- 自动调用工具
- 自动完成这个任务
- 检查并运行合适的工具
- 生成今天运营任务
- 帮我自动做独立站运营
- 帮我自动写博客/分镜/图片提示词/客户回复
- 帮我分析图片/设计/视频/错误日志

## 核心行为
1. 先执行 `plan`，再决定是否执行。
2. 仅 `low risk` 可自动执行。
3. `medium/high risk` 必须输出“需要用户确认”。
4. 即使用户说“自动”，也不得跳过安全分级。
5. 调用工具前先检查路径存在（Test-Path / Path.exists）。
6. 用户上传图片、视频、文件时，统一使用 `{{MediaPath}}`。
7. 用户要求写代码或创建插件且明确说“让 Codex 写”时：
   - 不直接写完整代码；
   - 只输出 Codex 任务提示词 + 测试步骤。
8. 磁盘清理仅允许自动 `-Scan`，禁止自动 `-CleanSafe`。
9. 涉及视频生成 API、RunningHub、Pixelle、FaceFusion：必须提示费用/隐私/确认。
10. 输出简洁：已执行什么、结果在哪里、下一步是什么。

## 默认安全红线
- 不删除文件
- 不调用付费 API
- 不修改 `openclaw.json`
- 不安装未知依赖
- 不覆盖已有脚本
- 不执行危险命令：CleanSafe / Remove-Item / del / rmdir / format / Stop-Process / taskkill / git reset / git clean

## 推荐调用顺序
1. `check`（可选，首次部署建议执行）
2. `plan --task "..."`
3. 若低风险：`run-low-risk --task "..."`
4. 若有计划文件：`execute-plan --plan-file ...`
5. 失败时：`explain-result --log "..."` 或 `--file ...`

## 输出规范
- 不确定就明确说不确定。
- 未检查通过前，不说“已完成/已创建/已安装”。
- 需要确认时固定提示：`需要用户确认`。
