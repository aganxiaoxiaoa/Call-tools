---
name: media-model-router-tool
description: Routes image, video, audio, and media understanding tasks to OpenAI, OpenRouter, and local QC tools without changing the OpenClaw global model.
---

# media_model_router_tool (Optional Skill)

This is an optional skill, not a core skill.

- Do not modify `openclaw.json`.
- Do not switch the global model.
- Global chat model remains DeepSeek official V4 Pro.
- OpenAI is used for high-quality images and high-quality video when available.
- OpenRouter is used for medium images, cheap images, free models, video generation, and video/audio understanding.
- User-specified model override is supported and validated for compatibility.
- Paid generation requires `--yes`.
- API keys come only from environment variables (`OPENAI_API_KEY`, `OPENROUTER_API_KEY`).
- Final generated images require QC.
- Product/realism QC: `image_analysis_skill`.
- Layout/banner/ad QC: `graphic_design_analyzer_skill`.
- Qwen-VL visual analysis should be called through `image_analysis_skill`, not by changing global model.
