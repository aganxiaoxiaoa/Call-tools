# image_analysis_skill（唯一正式路径）

唯一正式命令：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py"`

> 不再使用旧路径 `D:\bot\tool\Image analysis tools\...`

## 本地模式能做什么（默认不调用 API）
- 基础信息：文件名/尺寸/方向/大小
- 色彩：Top 5 HEX、亮度、对比度、饱和度、偏黄/偏红/偏橙/偏灰风险
- 几何：subject_bbox、主体比例、margins、crop_risk、置信度
- 产品比例：aspect ratio、label/cap 比例估算
- 参考图高度对比（含“只矮25%/接近砍半/变化不足”）
- Veytis/Juese 规则、品牌分析、平面设计建议、风格一致性统计、AI 质检

## 视觉模式能做什么（`--use-vision`）
- 场景语义、人物细节、物体清单、标签文字观察、产品语义分析。
- 当前正式实现：`qwen`
- `gemini/openai/local`：待扩展

### qwen 配置
- `DASHSCOPE_API_KEY`
- `DASHSCOPE_BASE_URL`（可选，默认 `https://dashscope.aliyuncs.com/compatible-mode/v1`）

默认不调用 API。API 可能有费用/配额。若失败（401/429/timeout/配额），自动回退本地分析。

## Telegram / OpenClaw 调用
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "{{MediaPath}}" --mode full`

## 常用命令
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --help
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\veytis.png" --brand "Veytis" --mode full --object-type bottle
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\banner.jpg" --mode graphic-design --use-case "homepage hero"
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\new.png" --reference "D:\bot\test\old.png" --expected-height-change "-25%" --mode product-geometry --object-type bottle
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --mode semantic-full --use-vision --vision-provider qwen --vision-model qwen-vl-plus
```

## 输出报告位置
`D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.md`
`D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.json`
stdout 最后一行：`FILE:file:///.../image_analysis_report.md`
