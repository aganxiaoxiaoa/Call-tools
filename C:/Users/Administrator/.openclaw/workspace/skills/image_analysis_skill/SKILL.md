---
name: image-analysis-skill
description: Unified local and optional vision-model image analysis for product photos, factory scenes, brand visuals, people/scene details, graphic design, and style consistency.
---

这是图片分析 Skill（不是 self-improving-robot）。

当用户需要分析图片、产品图、场景图、人物细节、品牌设计、平面设计、风格统一、Veytis 产品图、Juese 工厂图时，调用：

`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full`

默认不调用 API。仅当用户明确需要语义/人物/场景深度识别或传入 `--use-vision` 时，才调用视觉模型。
若视觉模型失败，必须回退本地分析并继续输出报告。
