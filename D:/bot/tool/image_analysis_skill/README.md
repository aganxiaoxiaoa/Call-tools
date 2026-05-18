# image_analysis_skill

默认执行 **local-basic** 详细分析（不调用外部视觉）。

可选外部视觉 provider：`dashscope/openrouter/openai/local`（以及兼容位 `qwen`, `gemini`）。

- 不默认调用 Qwen。
- OpenRouter 可用模型示例：`z-ai/glm-4.5v`
- DashScope 可用模型示例：`qwen-vl-plus`
- 外部调用必须显式 `--use-vision`
- `--no-external-vision` 会阻止 `qwen/dashscope/openrouter/openai/gemini`
- 失败会 fallback 到 local-basic
- 不修改 openclaw.json / 不切换全局模型 / 不打印 API key
