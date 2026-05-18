# image_analysis_skill

唯一正式命令：`py "D:\bot\tool\image_analysis_skill\image_analysis_tool.py"`

- local-basic：本地基础分析（几何/色彩/比例/裁切）
- qwen：云端视觉语义（需要 DASHSCOPE_API_KEY）
- local-vlm：本地 OpenAI-compatible 视觉模型（LM Studio/Ollama 兼容网关）

## 环境变量
- Qwen: `DASHSCOPE_API_KEY`, `DASHSCOPE_BASE_URL`
- Local VLM: `LOCAL_VISION_BASE_URL`(默认 `http://127.0.0.1:1234/v1`), `LOCAL_VISION_API_KEY`(默认 `lm-studio`), `LOCAL_VISION_MODEL`

默认不调用 API；语义模型失败会回退 local-basic。
