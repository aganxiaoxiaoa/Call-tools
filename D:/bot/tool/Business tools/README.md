# B2B Marketing Tool (Local)

本工具用于 OpenClaw Telegram 机器人本地调用，不依赖付费 API。

## 运行
```bash
python "D:\bot\tool\Business tools\b2b_marketing_tool.py" --help
python "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> --help
```

## 子命令
- geo-plan
- blog-brief
- blog-draft
- landing-page
- video-script
- image-prompt
- inquiry-reply
- faq
- content-calendar
- prompt-pack

## 输出
默认输出 Markdown / JSON / TXT 到：
`D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\`

脚本特性：
- Windows 路径兼容
- UTF-8 中文输出
- 错误处理与输出路径提示
- 不删除文件
- 不自动调用付费 API
