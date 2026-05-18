# image_analysis_skill

正式路径：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py"`

## 能力分层
1. **local-basic**（默认）：本地规则分析（尺寸/色彩/bbox/比例/裁切）
2. **qwen**：DashScope 语义视觉（需 `DASHSCOPE_API_KEY`）
3. **local-vlm**：本地 OpenAI-compatible 语义视觉（LM Studio/Ollama/vLLM 等服务）

> 本地基础分析 ≠ 本地视觉大模型语义分析。

## 默认行为
- 默认不调用 Qwen
- 默认不调用付费 API
- 语义失败会明确标记并 fallback 到 local-basic

## 环境变量
### Qwen
- `DASHSCOPE_API_KEY`
- `DASHSCOPE_BASE_URL`（默认 `https://dashscope.aliyuncs.com/compatible-mode/v1`）

### local-vlm
- `LOCAL_VISION_BASE_URL`（默认 `http://127.0.0.1:1234/v1`）
- `LOCAL_VISION_API_KEY`（默认 `lm-studio`）
- `LOCAL_VISION_MODEL`（必填，或通过 `--vision-model` 指定）

## local-vlm 调用说明
- `--vision-provider local` 时会请求：`$LOCAL_VISION_BASE_URL/chat/completions`
- 以 OpenAI Chat Completions 格式发送 `image_url`（base64 data URL）
- 返回值优先解析 JSON；解析失败保留 `raw_text`
- endpoint 不可用/模型未配置时，不会假装语义成功，而是保留错误并回退 local-basic

## install-local-vlm 说明
- `install-local-vlm` 仅负责模型下载（可 dry-run）
- **下载模型不等于已经可以推理**
- 推理仍需你自行启动本地兼容服务（LM Studio/Ollama/vLLM 等）并配置上述环境变量

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
  `py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py" --image "D:\bot\samples\test.jpg" --mode semantic-full --use-vision --vision-provider local --vision-model "qwen2.5-vl-7b-instruct" --no-external-vision`

## 输出
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.md`
- `D:\bot\outputs\image_analysis\YYYYMMDD-HHMMSS\image_analysis_report.json`
- stdout 末行：`FILE:file:///.../image_analysis_report.md`
