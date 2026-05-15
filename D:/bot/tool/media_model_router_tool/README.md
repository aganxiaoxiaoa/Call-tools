# media_model_router_tool

## Purpose
Task-level media model routing and execution for image generation/editing, video generation, media understanding routing, and model recommendation.

This tool **does not switch the global OpenClaw model**. Global chat model remains **DeepSeek official V4 Pro** (`deepseek/deepseek-v4-pro`).

## Official paths
- `D:/bot/tool/media_model_router_tool/media_model_router_tool.py`
- `D:/bot/tool/media_model_router_tool/README.md`
- `C:/Users/Administrator/.openclaw/workspace/skills/media_model_router_tool/SKILL.md`

## Environment variables
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- Existing watcher related: `DASHSCOPE_API_KEY`, optional `QWEN_OMNI_MODEL`

Never print or store API keys.

## Proxy use
Uses standard environment proxy variables automatically:
- `HTTP_PROXY`
- `HTTPS_PROXY`

## Routing policy
- OpenAI: high-quality image generation/editing and high-quality video when available.
- OpenRouter: medium/cheap/free exploratory images, video generation fallback, and model recommendation.
- Existing local Qwen-Omni watcher: video/audio transcription + translation + summary workflow.
- User-specified model override: validate availability + modality compatibility; no silent fallback.

## Important: existing transcription workflow
Video/audio transcription is already handled by:
- `D:/bot/openclaw_data/.openclaw/scripts/video_audio_auto.py`
- clean reference: `D:/bot/video_audio_auto_clean/video_audio_auto.py`

`media_model_router_tool` only routes/recommends this workflow and provides status checks. It does **not** duplicate transcription logic, create a new watcher, or replace this path with OpenRouter unless explicitly requested later.

## OpenAI high-quality rule
OpenAI image priority: `gpt-image-2 > gpt-image-1.5 > gpt-image-1-mini > chatgpt-image-latest`.
OpenAI video priority: `sora-2-pro > sora-2`.
Dynamic discovery via `/v1/models`.

## OpenRouter medium/cheap/free rule
Dynamic discovery via `/api/v1/models` and filters for modality/pricing/frontier restriction.
Default excludes `openai/*`, `anthropic/*`, `google/*` from recommendations unless explicitly requested and validated.

## User override rule
`--model` forces compatibility checks. If unavailable/incompatible, tool returns error + alternatives intent.

## Paid API safety
Paid generation commands require `--yes`. Without it, dry-run only.

## QC workflow
- Final image: run `image_analysis_skill`.
- Banner/layout/ad: also run `graphic_design_analyzer_skill`.

## Examples
- `py "D:/bot/tool/media_model_router_tool/media_model_router_tool.py" test-keys`
- `py "D:/bot/tool/media_model_router_tool/media_model_router_tool.py" recommend --task "high quality website hero image" --quality high --media-type image`
- `py "D:/bot/tool/media_model_router_tool/media_model_router_tool.py" video-audio-status`

## Acceptance tests
Run the command set in your task spec (Test-Path, --help, test-keys, refresh-model-cache, list-models, recommend, `video-audio-status`, qc-plan). All report-producing commands end with `FILE:file:///...`.

## Troubleshooting
- Missing key: set env vars before running.
- API unavailable: run `test-keys` and inspect generated report.
- Existing video/audio watcher issues: run `video-audio-status` and inspect script path/log availability.
