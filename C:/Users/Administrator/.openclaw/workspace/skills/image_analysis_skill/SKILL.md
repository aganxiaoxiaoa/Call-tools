---
name: image-analysis-skill
description: Unified local and optional vision-model image analysis for product photos, factory scenes, brand visuals, people/scene details, graphic design, and style consistency.
---

触发词：全面分析这张图、分析产品比例、分析瓶子高度、分析标签比例、这张图是不是砍半了、只矮25%不是砍半、分析场景细节、分析人物细节、分析画面里有什么、分析品牌设计、分析平面设计、分析文字排版、分析风格统一、分析 Veytis 产品图、分析 Juese Clothing 工厂图、看这张图适不适合独立站、生成这张图的修改提示词。

默认调用：
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full

Veytis：
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --mode full --object-type bottle

Juese：
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep

平面设计：
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode graphic-design --use-case "homepage hero"

语义深度：
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus

默认本地分析不调用 API；人物/标签/物体语义需 --use-vision；视觉失败自动回退本地分析。
不识别真实人物身份，不猜姓名，只分析动作、服装、姿势、手部、真实感和商业合理性。
