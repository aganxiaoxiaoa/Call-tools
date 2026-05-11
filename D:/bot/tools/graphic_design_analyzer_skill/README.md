# graphic_design_analyzer_skill

## 文件说明
- `graphic_design_tool.py`：本地图片分析脚本，输出结构化 Markdown + JSON 报告。
- `SKILL.md`（放在 OpenClaw skills 目录）：触发词与 Telegram 调用规则。

## 依赖安装
```bash
py -m pip install pillow numpy
```
可选（用于更准确清晰度检测）：
```bash
py -m pip install opencv-python
```

## 手动测试命令
```bash
py "D:\bot\tools\graphic_design_analyzer_skill\graphic_design_tool.py" --image "D:\bot\samples\test_banner.jpg" --brand "Generic" --use-case "homepage hero" --mode full
```

```bash
py "D:\bot\tools\graphic_design_analyzer_skill\graphic_design_tool.py" --image "D:\bot\samples\veytis_product.jpg" --brand "Veytis" --industry "essential oils wholesale" --use-case "product page" --mode full --text "植物精油原料批发。支持 private label。MOQ 友好，快速打样。"
```

```bash
py "D:\bot\tools\graphic_design_analyzer_skill\graphic_design_tool.py" --image "D:\bot\samples\garment_factory.jpg" --brand "Juese Clothing" --industry "custom garment factory" --use-case "website banner" --mode typography
```

## Telegram 调用示例
- 用户发送图片并说“分析这张广告图高级吗”：
```bash
py "D:\bot\tools\graphic_design_analyzer_skill\graphic_design_tool.py" --image "{{MediaPath}}" --brand "Generic" --use-case "ad creative" --mode ad-review
```

- 用户发送图片并说“分析文字排版”：
```bash
py "D:\bot\tools\graphic_design_analyzer_skill\graphic_design_tool.py" --image "{{MediaPath}}" --mode typography --brand "Generic"
```

## 输出目录
- Markdown：`D:\bot\outputs\graphic_design_analyzer\YYYYMMDD-HHMMSS\graphic_design_report.md`
- JSON：`D:\bot\outputs\graphic_design_analyzer\YYYYMMDD-HHMMSS\graphic_design_report.json`
- stdout 最后一行：`FILE:file:///D:/bot/outputs/graphic_design_analyzer/.../graphic_design_report.md`

## 常见错误
- `图片不存在`：检查 `--image` 绝对路径。
- `No module named PIL`：执行 `py -m pip install pillow numpy`。
- 无 `cv2`：脚本仍可运行，仅清晰度检测降级。

## 安全说明
- 不删除文件。
- 不调用付费 API。
- 不上传图片到外部。
- 仅在本地进行启发式分析与建议生成。
