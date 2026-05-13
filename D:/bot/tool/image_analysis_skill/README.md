# image_analysis_skill（唯一正式路径）

- 工具路径：`D:\bot\tool\image_analysis_skill\image_analysis_tool.py`
- Skill 路径：`C:\Users\Administrator\.openclaw\workspace\skills\image_analysis_skill\SKILL.md`

## 本地模式可分析
几何、色彩、主体比例、裁切、留白、品牌规则、平面设计建议、商业适配、参考高度对比。

## 视觉模式可分析（`--use-vision`）
场景语义、人物细节、物体清单、标签文字、产品语义。

## 视觉模型说明
- 已实现：`qwen`（需 `DASHSCOPE_API_KEY`，可选 `DASHSCOPE_BASE_URL`，默认 `https://dashscope.aliyuncs.com/compatible-mode/v1`）。
- 待扩展：`gemini` / `openai` / `local`。
- 默认不调用 API；API 可能有费用或配额限制。
- 若 401/429/timeout/配额不足，自动回退本地分析，不中断。

## 命令
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --help
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\veytis.png" --brand "Veytis" --mode full --object-type bottle
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\banner.jpg" --mode graphic-design --use-case "homepage hero"
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\new.png" --reference "D:\bot\test\old.png" --expected-height-change "-25%" --mode product-geometry --object-type bottle
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus
```
