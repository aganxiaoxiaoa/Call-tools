# agent_control_center_skill

## 工具说明
这是一个给 OpenClaw Telegram 机器人使用的“全局自检 + 防幻觉 + 工具路由控制中心”。默认只做检查、路由、报告，不直接执行危险动作。

## 文件结构
- `agent_control_center.py`：主程序（含 8 个子命令）。
- `tool_registry.json`：工具注册表与候选路径。
- `README.md`：使用说明。
- `C:\Users\Administrator\.openclaw\workspace\skills\agent_control_center_skill\SKILL.md`：Skill 行为规则。

## 安装方式
1. 复制目录到：`D:\bot\tools\agent_control_center_skill`
2. 确认 Skill 文件在：`C:\Users\Administrator\.openclaw\workspace\skills\agent_control_center_skill\SKILL.md`
3. 使用 UTF-8 终端执行命令。

## 测试命令
```powershell
py "D:\bot\tools\agent_control_center_skill\agent_control_center.py" list-tools
py "D:\bot\tools\agent_control_center_skill\agent_control_center.py" check-tool --tool disk_cleaner
py "D:\bot\tools\agent_control_center_skill\agent_control_center.py" route --intent "分析这张图的平面设计和文字排版"
py "D:\bot\tools\agent_control_center_skill\agent_control_center.py" validate-command --command "powershell -ExecutionPolicy Bypass -File \"D:\bot\tool\Cleaning tools\disk_cleaner.ps1\" -CleanSafe -Top 20"
py "D:\bot\tools\agent_control_center_skill\agent_control_center.py" error-explain --log "fatal: not a git repository"
py "D:\bot\tools\agent_control_center_skill\agent_control_center.py" project-map
```

## Telegram 调用示例
- 用户：`帮我分析这张图的平面设计和文字排版`
- 机器人流程：
  1) `route --intent "分析这张图的平面设计和文字排版"`
  2) `check-tool --tool graphic_design_analyzer`
  3) `preflight --task "分析设计图"`
  4) 输出建议命令并等待确认。

## 如何添加新工具到 registry
1. 在 `tool_registry.json` 的 `tools` 数组追加对象。
2. 必填字段：
   - `name`
   - `description`
   - `intents`
   - `command_template`
   - `candidate_paths`
   - `safe_by_default`
   - `requires_media`
   - `requires_api_key`
   - `paid_api_risk`
   - `destructive_risk`
   - `notes`
3. 至少提供 1 个候选路径，路径有空格时命令中必须加引号。

## 安全规则
- 禁止默认删除文件；清理任务默认 dry-run。
- 禁止危险命令直执行（Remove-Item/del/rmdir/format/kill/Stop-Process）。
- 不修改系统配置，除非用户明确要求。
- API 请求必须提示可能收费。
- 若路径不存在，明确输出“不存在”。
- 信息不足时输出“需要确认的信息”。

## 常见错误解释
- `Path not found`：路径写错或文件不存在，先 `Test-Path`。
- `Module not found`：Python 依赖缺失，先安装依赖再重试。
- `401`：API Key 错误或失效。
- `402`：余额/额度不足。
- `404`：路径、模型或接口不存在。
- `429`：请求过快被限流。
- `timeout`：网络超时或服务未启动。
- `JSON parse error`：参数格式不合法。
- `fatal: not a git repository`：当前目录不是 Git 仓库。
