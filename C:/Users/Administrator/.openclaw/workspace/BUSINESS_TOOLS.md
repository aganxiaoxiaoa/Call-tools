# BUSINESS_TOOLS 机器人触发说明

当 Telegram 用户发送以下意图时，调用：
`python "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> ...`

## 触发映射
- 生成博客大纲 / 写B2B博客 -> `blog-brief` 或 `blog-draft`
- GEO优化 -> `geo-plan`
- 生成短视频脚本 -> `video-script`
- 生成图片提示词 -> `image-prompt`
- 写客户回复 -> `inquiry-reply`
- 生成产品页 -> `landing-page`
- 生成FAQ -> `faq`
- 生成内容日历 -> `content-calendar`
- 一键生成内容包 -> `prompt-pack`

## 示例命令
```bash
python "D:\bot\tool\Business tools\b2b_marketing_tool.py" geo-plan --brand "Veytis" --industry "essential oils and hydrosols wholesale" --country "United States" --language "English" --product "bulk essential oils" --audience "B2B buyers" --keywords "bulk essential oils, private label essential oils, hydrosol supplier"

python "D:\bot\tool\Business tools\b2b_marketing_tool.py" video-script --brand "Juese Clothing" --industry "custom garment factory" --topic "custom hoodie production process" --platform "TikTok" --duration "30s" --language "English" --style "realistic B2B factory"
```

## 输出目录
每次运行在以下目录生成 Markdown / JSON / TXT：
`D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\`
