---
name: image-analysis-skill
description: Unified local and optional vision-model image analysis for product photos, factory scenes, brand visuals, people/scene details, graphic design, and style consistency.
---

默认本地分析（local-basic）：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full`

用户不想用千问时：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full --no-external-vision`

深度识图优先 local_vlm：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode semantic-full --use-vision --vision-provider local --vision-model "%LOCAL_VISION_MODEL%" --no-external-vision`

若本地 VLM 不可用，先运行：
- `py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" status`
- `py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" install-local-vlm --backend smolvlm2 --model "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"`

如用户已配置 DashScope，可选：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus`

说明：不修改 openclaw.json，不切换全局模型。
