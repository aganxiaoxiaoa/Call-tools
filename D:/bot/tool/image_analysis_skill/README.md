# image_analysis_skill README

这是**统一视觉分析工具**（不是仅基础分析）。

## 本地模式可做（默认）
- 几何：subject_bbox、主体高宽占比、边距、裁切风险
- 色彩：主色、亮度、对比度、饱和度、偏色
- 比例：产品宽高比、瓶型估算、label/cap 估算
- 留白/构图/商业适配度
- 多图风格一致性评分（`--reference-dir`）

## 语义能力说明
- 场景语义、人物细节、物体识别、标签文字语义，建议使用 `--use-vision`。
- 默认不调用视觉模型（不上传图片）。
- 开启视觉模型后，如 gemini/qwen/openai/local 调用失败（401/429/timeout/配额），会**自动回退本地分析**，不中断。

## 品牌规则
- Veytis：neutral cool tone、避免黄/红/橙偏色、瓶型接近 4oz/120mL Boston round、标签真实。
- Juese Clothing：factory documentary realism、工厂整洁明亮、流程真实、避免假设备和过度 AI 感。

## 典型用法
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep

py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\scene.jpg" --mode semantic-full --scene-type "factory_scene" --detect-people

py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\veytis.png" --brand "Veytis" --mode full --object-type bottle

py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\banner.jpg" --mode graphic-design --use-case "homepage hero"

py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus
```

## 输出
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.md`
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.json`
- stdout 最后一行：`FILE:file:///.../image_analysis_report.md`
