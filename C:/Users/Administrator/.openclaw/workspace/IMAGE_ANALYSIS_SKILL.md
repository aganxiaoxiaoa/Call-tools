# IMAGE_ANALYSIS_SKILL

当用户发送图片并出现以下意图时，优先调用本地图片分析工具：
- 分析这张图
- 看看这张图哪里有AI感
- 分析图片风格
- 分析图片色彩
- 分析图片构图
- 这张图适合放网站吗
- 帮我分析产品图
- 帮我分析工厂图
- 生成这张图的提示词
- 根据这张图写图片提示词
- 分析图片是否适合首页

## 默认调用（Generic）
```bash
py "D:\bot\tool\Image analysis tools\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Generic" --use-case "website image" --mode full
```

## Veytis 调用
```bash
py "D:\bot\tool\Image analysis tools\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --industry "essential oils wholesale" --use-case "product photo" --mode full
```

## Juese Clothing / 服装工厂调用
```bash
py "D:\bot\tool\Image analysis tools\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Juese Clothing" --industry "custom garment factory" --use-case "factory scene" --mode full
```

## 返回约定
工具会输出：
1. 分析摘要
2. Markdown 报告路径
3. 最后一行：
`FILE:file:///D:/bot/outputs/image_analysis/YYYYMMDD-HHMMSS/image_analysis_report.md`

如用户只要提示词，可使用：`--mode prompt`。
如用户只要质检，可使用：`--mode qc`。
