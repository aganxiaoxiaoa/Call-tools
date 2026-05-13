# image_analysis_skill（唯一正式路径）

唯一正式工具：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py"`

## 本地模式（默认，不调用 API）
可分析：基础信息、Top5 主色(HEX)、亮度/对比/饱和、色偏风险、主体 bbox 与占比、裁切风险、产品比例、Veytis/Juese 规则、平面设计建议、商业适配、reference 高度对比。

## 视觉模式（可选）
用于场景语义、人物细节、物体清单、标签文字、产品语义。

### qwen 配置（已实现）
- `DASHSCOPE_API_KEY`
- `DASHSCOPE_BASE_URL`（可选，默认 `https://dashscope.aliyuncs.com/compatible-mode/v1`）

`gemini/openai/local` 当前待扩展。默认不调用 API；API 可能有费用/配额。失败(401/429/timeout/配额)自动回退本地分析。

## Telegram/OpenClaw 调用
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full`

## 验收命令
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --help
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\veytis.png" --brand "Veytis" --mode full --object-type bottle
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\banner.jpg" --mode graphic-design --use-case "homepage hero"
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\new.png" --reference "D:\bot\test\old.png" --expected-height-change "-25%" --mode product-geometry --object-type bottle
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus
```
