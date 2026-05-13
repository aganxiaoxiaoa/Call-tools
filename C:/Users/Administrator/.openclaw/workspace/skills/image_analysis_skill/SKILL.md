# image_analysis_skill

## 触发词（用户发图时优先调用）
- 分析场景细节
- 分析人物细节
- 分析画面里有什么
- 分析产品和人物关系
- 分析工厂场景是否真实
- 分析这个场景是否适合B2B
- 分析设计风格是否统一
- 全面分析这张图
- 深度分析这张图
- 分析产品比例 / 瓶子高度 / 标签比例

## 推荐命令
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full --analysis-depth deep
```

Veytis：
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --scene-type "product_photo" --mode full --object-type bottle
```

Juese 工厂：
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Juese Clothing" --scene-type "factory_scene" --mode semantic-full --analysis-depth deep
```

风格统一：
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode style-consistency --reference-dir "D:\bot\references\veytis" --brand "Veytis"
```

视觉模型增强（可选）：
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus
```

若视觉模型失败，工具会自动回退本地分析并继续输出报告。
