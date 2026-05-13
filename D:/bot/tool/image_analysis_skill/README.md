# image_analysis_skill

## 本地模式（默认，不调用 API）
可分析：几何、色彩、主体比例、裁切、留白、风格一致性、品牌适配、平面排版、商业适配度。

## 视觉模型模式（可选）
场景语义、人物细节、物体识别、标签文字建议使用 `--use-vision`。
若 Gemini/Qwen/OpenAI 接口失败或配额不足（401/429/timeout），会自动回退本地分析。
> 注意：Gemini/Qwen/OpenAI API 可能有费用或配额限制；本工具默认不调用 API。

## 品牌规则
- Veytis：neutral cool tone、避免黄/红/橙偏色、瓶型与标签真实。
- Juese Clothing：工厂纪实感、整洁明亮、流程真实、避免假设备/脏乱。

## 命令示例
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\scene.jpg" --mode semantic-full --scene-type "factory_scene" --detect-people
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\veytis.png" --brand "Veytis" --mode full --object-type bottle
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\banner.jpg" --mode graphic-design --use-case "homepage hero"
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\new.png" --reference-dir "D:\bot\references\veytis" --brand "Veytis" --mode style-consistency
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus
```
