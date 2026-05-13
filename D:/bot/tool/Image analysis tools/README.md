# Image Analysis Tool（OpenClaw 本地图片分析）

## 依赖安装
```bash
pip install pillow numpy
# 可选
pip install opencv-python
```

## 手动测试命令（Windows）
```bash
py "D:\bot\tool\Image analysis tools\image_analysis_tool.py" --image "D:\test\sample.jpg" --brand "Veytis" --use-case "homepage hero" --industry "essential oils wholesale" --mode full
```

## Telegram / OpenClaw 调用示例
```bash
py "D:\bot\tool\Image analysis tools\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Generic" --use-case "website image" --mode full
```

Veytis：
```bash
py "D:\bot\tool\Image analysis tools\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Veytis" --industry "essential oils wholesale" --use-case "product photo" --mode full
```

Juese Clothing：
```bash
py "D:\bot\tool\Image analysis tools\image_analysis_tool.py" --image "{{MediaPath}}" --brand "Juese Clothing" --industry "custom garment factory" --use-case "factory scene" --mode full
```

## 输出目录
- Markdown：`D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.md`
- JSON：`D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.json`
- stdout 最后一行：`FILE:file:///D:/bot/outputs/image_analysis/YYYYMMDD-HHMMSS/image_analysis_report.md`

## 常见错误
1. 图片不存在：检查 `--image` 路径是否正确。
2. 缺少依赖：执行 `pip install pillow numpy`。
3. `opencv-python` 未安装：不影响基础分析，脚本会自动降级到 Pillow。
4. 路径有空格：命令中必须加双引号，例如：`"D:\bot\tool\Image analysis tools\image_analysis_tool.py"`。

## 安全说明
- 不删除任何文件。
- 不调用付费 API。
- 不上传图片到外部服务。
- 仅做本地规则分析与报告生成。
