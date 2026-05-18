# image_analysis_skill

正式路径：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py"`

## 能力分层
1. **local-basic**（默认）：本地规则分析（尺寸/色彩/bbox/比例/裁切）
2. **qwen**：DashScope 语义视觉（需 `DASHSCOPE_API_KEY`）
3. **local-vlm**：本地开源视觉模型（OpenAI-compatible endpoint）

> 本地基础分析 ≠ 本地视觉大模型语义分析。

## 默认行为
- 默认不调用 Qwen
- 默认不调用付费 API
- 语义失败自动回退 local-basic

## 环境变量
### Qwen
- `DASHSCOPE_API_KEY`
- `DASHSCOPE_BASE_URL`（默认 `https://dashscope.aliyuncs.com/compatible-mode/v1`）

### local-vlm
- `LOCAL_VISION_BASE_URL`（默认 `http://127.0.0.1:1234/v1`）
- `LOCAL_VISION_API_KEY`（默认 `lm-studio`）
- `LOCAL_VISION_MODEL`（默认 `qwen2.5-vl-7b-instruct`）

## 关键命令
- 状态检查：
  `py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" status`
- 安装计划（dry-run）：
  `py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" install-local-vlm --backend smolvlm2 --model "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"`
- 真下载（需 --yes）：
  `py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" install-local-vlm --backend smolvlm2 --model "HuggingFaceTB/SmolVLM2-500M-Video-Instruct" --yes`
- 本地基础分析：
  `py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\samples\test.jpg" --mode full --no-external-vision`
- 语义优先 local-vlm：
  `py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\samples\test.jpg" --mode semantic-full --use-vision --vision-provider local --no-external-vision`

## 输出
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.md`
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.json`
- stdout 末行：`FILE:file:///.../image_analysis_report.md`
