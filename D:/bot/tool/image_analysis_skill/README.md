# image_analysis_skill 使用说明

唯一正式路径：
`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py"`

## 本地模式能力（默认，不调用 API）
- 图片基础信息：尺寸、方向、文件大小
- 色彩分析：Top5 HEX、亮度、对比度、饱和度、偏色风险
- 主体几何：bbox、主体占比、边距、裁切风险、置信度
- 产品比例：aspect ratio、label/cap 估算、瘦高/偏胖判断
- reference 高度对比：支持 `--expected-height-change "-25%"` 判定
- 品牌规则提示：Veytis / Juese Clothing
- 平面设计建议：标题区/CTA/Logo/安全区基础建议

## Qwen 视觉模式能力（可选）
启用参数：`--use-vision --vision-provider qwen --vision-model qwen-vl-plus`
- 场景语义补充
- 人物细节补充
- 物体清单/标签观察补充
- 工厂逻辑与商业适配补充

### 环境变量配置
- `DASHSCOPE_API_KEY`（必需）
- `DASHSCOPE_BASE_URL`（可选，默认 `https://dashscope.aliyuncs.com/compatible-mode/v1`）

> 默认不调用 API；API 可能存在费用或配额限制。失败时工具会回退本地分析。

## 常用命令

### Veytis 产品图
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\veytis.png" --brand "Veytis" --mode full --object-type bottle
```

### Juese Clothing 工厂图
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\factory.jpg" --brand "Juese Clothing" --scene-type "factory_scene" --mode full --analysis-depth deep
```

### 平面设计
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\banner.jpg" --mode graphic-design --use-case "homepage hero"
```

### reference 高度对比
```bash
py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\test\new.png" --reference "D:\bot\test\old.png" --expected-height-change "-25%" --mode product-geometry --object-type bottle
```

## 输出报告位置
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.md`
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.json`
- stdout 最后一行：`FILE:file:///.../image_analysis_report.md`

## 说明
- `style-consistency` 目前是基础版统计（亮度/对比/饱和/主体高度均值与差异）。
