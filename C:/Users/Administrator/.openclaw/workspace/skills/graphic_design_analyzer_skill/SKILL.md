---
name: graphic_design_analyzer_skill
description: 本地平面设计图片分析与排版建议 Skill（Telegram/OpenClaw）
---

# graphic_design_analyzer_skill

当用户发送图片并表达以下意图时，优先调用本 Skill：
- 分析这个平面设计
- 看看这张海报设计怎么样
- 分析这张图的排版
- 分析文字排版
- 这张广告图高级吗
- 这张图适合独立站首页吗
- 这张图适合产品页吗
- 这张图适合短视频封面吗
- 帮我优化这个 Banner
- 帮我给这张图出设计修改建议
- 分析这张图的色彩和版式

## 默认调用命令

```bash
py "D:\bot\tools\graphic_design_analyzer_skill\graphic_design_tool.py" --image "{{MediaPath}}" --brand "Generic" --use-case "website image" --mode full
```

## 品牌专用调用

### Veytis
```bash
py "D:\bot\tools\graphic_design_analyzer_skill\graphic_design_tool.py" --image "{{MediaPath}}" --brand "Veytis" --industry "essential oils wholesale" --use-case "product page or homepage hero" --mode full
```

### Juese Clothing / 服装工厂
```bash
py "D:\bot\tools\graphic_design_analyzer_skill\graphic_design_tool.py" --image "{{MediaPath}}" --brand "Juese Clothing" --industry "custom garment factory" --use-case "factory image or B2B website visual" --mode full
```

### 用户重点要求“文字排版”
```bash
py "D:\bot\tools\graphic_design_analyzer_skill\graphic_design_tool.py" --image "{{MediaPath}}" --mode typography --brand "Generic"
```

## 行为规则
- 仅本地读取图片，不上传外部服务。
- 不调用付费 API。
- 不删除用户文件。
- 路径包含空格时必须加引号。
- 输出 UTF-8 中文 Markdown 报告。
- 将报告写入：`D:\bot\outputs\graphic_design_analyzer\YYYYMMDD-HHMMSS\graphic_design_report.md`
- 最后一行输出 `FILE:file:///...`，便于 Telegram 回传。
