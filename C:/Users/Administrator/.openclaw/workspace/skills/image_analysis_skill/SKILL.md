---
name: image-analysis-skill
description: Unified local and optional vision-model image analysis for product photos, factory scenes, brand visuals, people/scene details, graphic design, and style consistency.
---

当用户发送图片并说以下任一意图时，优先调用本工具：
- 全面分析这张图
- 分析产品比例
- 分析瓶子高度
- 分析标签比例
- 分析场景细节
- 分析人物细节
- 分析品牌设计
- 分析平面设计
- 分析文字排版
- 分析风格统一
- 分析 Veytis 产品图
- 分析 Juese Clothing 工厂图
- 看这张图是否适合独立站
- 生成这张图的修改提示词

默认调用：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full`

Veytis 产品图：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --mode full --object-type bottle`

Juese Clothing 工厂图：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep`

平面设计：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode graphic-design --use-case "homepage hero"`
