# truthful_research_and_tool_governor_skill

## Purpose
用于 OpenClaw Telegram 机器人的主控治理：减少幻觉、避免随机调用、提升可审计性、支持合法公开网页研究。

## Why tools cannot be added without limit
工具无限叠加会导致：
1. 路由冲突与重名冲突；
2. 维护成本飙升；
3. 高风险命令误触发；
4. 输出不一致、机器人“变笨/变慢”。

## How to reduce tool conflicts
- 一工具一目录，统一命名。
- 所有工具登记到 `tool_policy_registry.json`。
- 默认先跑 `preflight` 与 `intent-router`。
- 所有高风险操作必须用户确认。

## Add a new tool to registry
1. 在 JSON 中新增完整条目（name/paths/intents/risk/template 等）。
2. 明确 `blocked_actions` 与 `paid_api_risk`。
3. 为新工具提供 README 与可执行模板。
4. 运行 `tool-audit` 检查冲突。

## Boundaries for web search and crawling
- 仅公开网页，且 http/https。
- 禁止 .onion。
- 遵守 robots.txt。
- 小规模、限速、限深、限页。
- 默认仅产出报告，不下载大文件。

## Dark-web and full-site-download support
不支持。涉及暗网、全站批量下载、绕过限制等请求将被阻止，并返回合规替代方案。

## Test commands
1. `py "D:\bot\tools\truthful_research_and_tool_governor_skill\truthful_governor.py" truth-check --answer "I have already installed the plugin for you"`
2. `py "D:\bot\tools\truthful_research_and_tool_governor_skill\truthful_governor.py" intent-router --intent "Analyze the graphic design and text layout of this image"`
3. `py "D:\bot\tools\truthful_research_and_tool_governor_skill\truthful_governor.py" tool-audit`
4. `py "D:\bot\tools\truthful_research_and_tool_governor_skill\truthful_governor.py" preflight --task "Perform safe cleanup of the C drive" --command "powershell -ExecutionPolicy Bypass -File \"D:\bot\tool\Cleaning tools\disk_cleaner.ps1\" -CleanSafe -Top 20"`
5. `py "D:\bot\tools\truthful_research_and_tool_governor_skill\truthful_governor.py" research-plan --topic "bulk essential oils wholesale USA GEO strategy" --country "United States" --language "English" --industry "essential oils wholesale" --purpose "GEO SEO blog planning"`
6. `py "D:\bot\tools\truthful_research_and_tool_governor_skill\truthful_governor.py" public-web-fetch --url "https://example.com"`
7. `py "D:\bot\tools\truthful_research_and_tool_governor_skill\truthful_governor.py" blocked-task-explain --task "Search the dark web and download leaked data"`

## Telegram usage examples
- “先自检，不要幻觉，再告诉我该用哪个工具。”
- “请做美国精油批发 GEO/SEO 公开信息研究计划。”
- “先检查这个命令是否安全、是否可能产生费用。”
- “分析这个竞品页面结构，给我原创内容方向。”
