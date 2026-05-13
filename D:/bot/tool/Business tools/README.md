# B2B Marketing Tool (Upgraded)

## 工具用途
本地生成国际 B2B 独立站运营内容：GEO/SEO、博客、落地页、产品页、服务页、短视频脚本、图片提示词、询盘回复、FAQ、内容日历、Google Ads 关键词/否词。

## 正式路径
- `D:\bot\tool\Business tools\b2b_marketing_tool.py`
- `D:\bot\tool\Business tools\README.md`
- `C:\Users\Administrator\.openclaw\workspace\skills\b2b_marketing_skill\SKILL.md`

## 子命令
geo-plan, blog-brief, blog-draft, landing-page, video-script, image-prompt, inquiry-reply, faq, content-calendar, prompt-pack, product-page, service-page, ad-keyword-plan, negative-keywords, seo-meta

## 通用规则
- 不调用付费 API
- 不编造认证/产能/价格/交期
- 不确定信息标注 `[verify]` / `available upon request` / `depending on order details`
- stdout 最后一行输出 `FILE:file:///.../<command>.md`

## 调用方式（OpenClaw/Telegram）
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> ...`

## 示例（Veytis）
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" blog-draft --brand "Veytis" --industry "essential oils wholesale" --topic "How to Choose a Private Label Essential Oil Supplier" --country "United States" --language "English" --keywords "private label essential oils, bulk essential oils supplier" --intent "commercial"`

## 示例（Juese Clothing）
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" video-script --brand "Juese Clothing" --industry "custom garment factory" --topic "custom hoodie production process" --platform "TikTok" --duration "30s" --language "English" --style "realistic B2B factory"`

## 每个子命令示例
- geo-plan: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" geo-plan --brand "Veytis" --industry "essential oils wholesale" --country "United States" --language "English" --product "bulk essential oils" --audience "B2B buyers" --keywords "bulk essential oils, private label essential oils" --geo-type both`
- blog-brief: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" blog-brief --brand "Veytis" --industry "essential oils wholesale" --topic "Hydrosol Supplier Checklist" --country "United States" --language "English" --keywords "hydrosol supplier, private label hydrosol" --intent commercial`
- blog-draft: 同上改为 `blog-draft`
- landing-page: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" landing-page --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies" --country "United States" --language "English"`
- product-page: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" product-page --brand "Veytis" --industry "essential oils wholesale" --product "bulk lavender essential oil"`
- service-page: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" service-page --brand "Juese Clothing" --industry "apparel OEM/ODM" --product "sampling and bulk production"`
- video-script: 见上
- image-prompt: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" image-prompt --brand "Veytis" --industry "essential oils wholesale" --scene "premium essential oil product photo" --product "4 fl oz amber dropper bottle" --style "neutral cool premium natural" --ratio "1:1" --language "English"`
- inquiry-reply: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" inquiry-reply --brand "Juese Clothing" --industry "custom garment factory" --customer-message "Hi, can you make 500 custom hoodies with puff print?" --tone "professional" --language "English"`
- faq: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" faq --brand "Veytis" --industry "essential oils wholesale" --product "hydrosol"`
- content-calendar: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" content-calendar --brand "Juese Clothing" --industry "custom garment factory" --country "United States" --language "English"`
- prompt-pack: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" prompt-pack --brand "Veytis" --industry "essential oils wholesale" --topic "Private Label Essential Oils" --country "United States" --language "English" --product "bulk essential oils"`
- ad-keyword-plan: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" ad-keyword-plan --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies"`
- negative-keywords: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" negative-keywords --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies" --country "United States" --language "English"`
- seo-meta: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" seo-meta --brand "Veytis" --industry "essential oils wholesale" --product "bulk essential oils"`

## 输出目录
`D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\` 下生成 `.md/.json/.txt`。
