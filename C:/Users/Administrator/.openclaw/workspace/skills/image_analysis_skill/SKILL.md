---
name: image-analysis-skill
description: Unified local and optional vision-model image analysis for product photos, factory scenes, brand visuals, graphic design, people/scene details, and style consistency.
---

触发词：分析场景细节、分析人物细节、分析画面里有什么、分析产品和人物关系、分析工厂场景是否真实、分析这个场景是否适合B2B、分析设计风格是否统一、全面分析这张图、深度分析这张图。

默认（本地）
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full --analysis-depth deep
```

视觉模型（可选）
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus
```

如果视觉模型失败（401/429/timeout/配额），工具会自动回退本地分析并继续输出 Markdown/JSON。
