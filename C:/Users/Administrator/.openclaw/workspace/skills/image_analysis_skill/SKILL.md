---
name: image-analysis-skill
description: Unified local and optional vision-model image analysis for product photos, factory scenes, brand visuals, people/scene details, graphic design, and style consistency.
---

当用户发送图片并提出以下需求时，优先调用：
- 全面分析图片
- 分析产品比例
- 分析瓶子高度
- 分析 Veytis 产品图
- 分析 Juese 工厂图
- 分析平面设计 / 文字排版
- 分析人物 / 场景细节
- reference 对比（例如“只矮25%不是砍半”）
- 生成修改提示词

默认调用（本地模式）：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full`

Veytis：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --mode full --object-type bottle`

Juese Clothing 工厂图：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep`

平面设计：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode graphic-design --use-case "homepage hero"`

人物/场景语义深度分析：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus`

说明：
- 默认本地分析，不调用 API。
- 人物细节、标签文字、场景语义、物体清单建议开启 `--use-vision`。
- 视觉模型失败时自动回退本地分析。
