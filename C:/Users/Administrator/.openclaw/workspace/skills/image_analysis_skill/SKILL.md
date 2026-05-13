---
name: image-analysis-skill
description: Unified local and optional vision-model image analysis for product photos, factory scenes, brand visuals, people/scene details, graphic design, and style consistency.
---

这是图片分析 Skill，不是 self-improving-robot。

当用户要求分析图片、产品图、场景图、人物细节、品牌设计、平面设计、风格统一、Veytis 产品图、Juese 工厂图时，调用：

`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full`

默认本地分析；深度语义/人物细节/标签文字/场景物体识别需要 `--use-vision`。
视觉模型失败时自动回退本地分析并继续输出 Markdown + JSON。
