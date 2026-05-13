---
name: image-analysis-skill
description: Unified local and optional vision-model image analysis for product photos, factory scenes, brand visuals, people/scene details, graphic design, and style consistency.
---

正式入口仅使用：`D:\bot\tool\image_analysis_skill\image_analysis_tool.py`

默认本地：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full`

Qwen 视觉（可选）：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus`
