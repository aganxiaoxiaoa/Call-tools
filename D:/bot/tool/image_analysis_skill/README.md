# image_analysis_skill

唯一正式路径：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py"`
旧路径已弃用（仅保留唯一正式路径）。

## 本地模式
可做几何、色彩、主体比例、裁切、reference 高度对比、品牌规则、平面设计分析。

## 视觉模式
可做场景语义、人物细节、标签文字、物体清单、工厂逻辑。
默认不调用 API；API 可能有费用或配额。失败会回退本地分析。

## Qwen 配置
- `DASHSCOPE_API_KEY`
- `DASHSCOPE_BASE_URL`（默认 `https://dashscope.aliyuncs.com/compatible-mode/v1`）

## 命令
- Veytis：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\veytis.png" --brand "Veytis" --mode full --object-type bottle`
- Juese：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep`
- 平面设计：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\banner.jpg" --mode graphic-design --use-case "homepage hero"`
- reference 高度对比：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\new.png" --reference "D:\bot\test\old.png" --expected-height-change "-25%" --mode product-geometry --object-type bottle`
- style consistency：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\new.png" --reference-dir "D:\bot\references\veytis" --mode style-consistency`

## 输出
`D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.md`
`D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.json`
