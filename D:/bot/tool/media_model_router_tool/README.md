# media_model_router_tool

支持自然语言模型路由（OpenRouter 动态模型表，不写死单一模型）。

- 动态查询：`https://openrouter.ai/api/v1/models`
- 支持 exact model id / provider prefix / free / cheap / best
- 可验证输入输出模态（text/image/video/audio/generation）
- 不修改 `openclaw.json`
- 不切换全局模型
- 不打印 API key

命令：
- `list-openrouter-models`
- `resolve-model`
- `recommend-openrouter-model`
- `call-openrouter-vision`
