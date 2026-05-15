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
- OpenRouter is used for medium images, cheap images, free models, video generation, and model recommendation.
- Video/audio transcription is already handled by existing Qwen-Omni watcher script (`D:/bot/openclaw_data/.openclaw/scripts/video_audio_auto.py`).
- `media_model_router_tool` only routes/recommends that existing video/audio watcher workflow.
- Do not duplicate transcription logic. Do not add a second watcher. Do not replace Qwen-Omni transcription path unless explicitly requested later.
- User-specified model override is supported and validated for compatibility.
- Paid generation requires `--yes`.
- API keys come only from environment variables (`OPENAI_API_KEY`, `OPENROUTER_API_KEY`, existing watcher key `DASHSCOPE_API_KEY`).
- Final generated images require QC.
- Product/realism QC: `image_analysis_skill`.
- Layout/banner/ad QC: `graphic_design_analyzer_skill`.
- Qwen-VL visual analysis should be called through `image_analysis_skill`, not by changing global model.

## Official command examples
- `py "D:/bot/tool/media_model_router_tool/media_model_router_tool.py" --help`
- `py "D:/bot/tool/media_model_router_tool/media_model_router_tool.py" test-keys`
- `py "D:/bot/tool/media_model_router_tool/media_model_router_tool.py" recommend --task "{{UserMessage}}" --quality medium --media-type mixed`
- `py "D:/bot/tool/media_model_router_tool/media_model_router_tool.py" video-audio-status`

## Guardrails
- Do not modify `openclaw.json`.
- Do not switch the global model.
- Global chat model remains DeepSeek official V4 Pro.
- Video/audio transcription routes to existing Qwen-Omni watcher: `D:/bot/openclaw_data/.openclaw/scripts/video_audio_auto.py`.
- OpenAI is for high-quality images/video.
- OpenRouter is for medium images, video generation, and model recommendation.
- Final images require QC via `image_analysis_skill` and `graphic_design_analyzer_skill`.
