# image_analysis_skill（统一视觉分析工具）

本工具**不只是基础图片分析**，还支持：
- 通用图片分析
- 产品主体几何比例分析（bbox、高度占比、裁切风险）
- Veytis 精油/纯露产品图分析
- Juese Clothing 工厂图分析
- 品牌设计分析
- 平面设计/文字排版分析
- 多图风格统一分析（`--reference-dir`）
- 参考图高度对比（`--reference` + `--expected-height-change`）
- AI 质检与提示词生成

## 安装依赖
```bash
pip install pillow numpy
# 可选增强
pip install opencv-python
```

## 说明
- 默认完全本地运行，不上传图片，不调用付费 API。
- 默认不调用视觉模型（`--use-vision` 默认为 false，`--vision-provider none`）。
- 即使 Gemini 配额用完，也可继续做本地几何分析（bbox/高度占比/裁切风险等）。
- 视觉模型仅作为可选增强，不是必需路径。

## 命令示例（路径与真实路径一致）

Veytis 产品几何：
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --mode product-geometry --object-type bottle
```

Veytis 全面分析：
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --industry "essential oils wholesale" --use-case "product photo" --mode full --object-type bottle
```

平面设计分析：
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Generic" --use-case "ad creative" --mode graphic-design
```

风格统一：
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --reference-dir "D:\bot\references\veytis" --brand "Veytis" --mode style-consistency
```

参考图高度对比：
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --reference "D:\bot\test\reference.png" --brand "Veytis" --mode product-geometry --object-type bottle --expected-height-change "-25%"
```

## 输出目录
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.md`
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.json`
- stdout 末行：`FILE:file:///D:/bot/outputs/image_analysis/YYYYMMDD-HHMMSS/image_analysis_report.md`

## 常见错误
- 图片不存在：检查 `--image` 路径。
- 缺少依赖：`pip install pillow numpy`。
- `opencv-python` 缺失：会自动降级，不影响基础与几何分析。
