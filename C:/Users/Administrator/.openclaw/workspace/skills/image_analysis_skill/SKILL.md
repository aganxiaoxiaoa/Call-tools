# image_analysis_skill

当用户提到以下意图并发送图片时，优先调用：
- 分析这张图
- 分析产品比例 / 瓶子高度 / 标签比例
- 这张图是不是砍半了 / 只矮25%不是砍半
- 分析品牌设计 / 平面设计 / 文字排版 / 风格统一
- 分析 Veytis 产品图 / 分析 Juese 工厂图
- 看看这张图适不适合独立站
- 生成这张图的修改提示词

## 默认调用
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Generic" --mode full
```

## Veytis 产品几何
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --mode product-geometry --object-type bottle
```

## Veytis 全面分析
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --industry "essential oils wholesale" --use-case "product photo" --mode full --object-type bottle
```

## 平面设计分析
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Generic" --use-case "ad creative" --mode graphic-design
```

## 风格统一
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --reference-dir "D:\bot\references\veytis" --brand "Veytis" --mode style-consistency
```

## 参考图高度对比
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --reference "D:\bot\test\reference.png" --brand "Veytis" --mode product-geometry --object-type bottle --expected-height-change "-25%"
```

工具返回包含 Markdown/JSON 路径，stdout 最后一行为：
`FILE:file:///D:/bot/outputs/image_analysis/YYYYMMDD-HHMMSS/image_analysis_report.md`
