# image_analysis_skill

支持视觉 provider：`none,qwen,dashscope,openrouter,openai,gemini,local`。

- 外部视觉调用必须显式 `--use-vision`
- `--no-external-vision` 会阻止 qwen/dashscope/openrouter/openai/gemini
- qwen 与 dashscope 都使用 `DASHSCOPE_API_KEY`
- openrouter 使用 `OPENROUTER_API_KEY`
- openai 使用 `OPENAI_API_KEY`
- local 使用 `LOCAL_VISION_BASE_URL` / `LOCAL_VISION_API_KEY` / `LOCAL_VISION_MODEL`
- 失败自动 fallback local-basic，且保留详细 local-basic 报告
- 不修改 openclaw.json，不切换全局模型，不打印 API key
