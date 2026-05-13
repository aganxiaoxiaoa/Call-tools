# B2B Marketing Tool Stage 3.1

## 正式路径
- `D:\bot\tool\Business tools\b2b_marketing_tool.py`
- `D:\bot\tool\Business tools\README.md`
- `C:\Users\Administrator\.openclaw\workspace\skills\b2b_marketing_skill\SKILL.md`

> 不使用 `BUSINESS_TOOLS.md` 作为正式入口。

## 命令（20个）
`geo-plan, blog-brief, blog-draft, landing-page, product-page, service-page, video-script, image-prompt, inquiry-reply, faq, content-calendar, prompt-pack, ad-keyword-plan, negative-keywords, seo-meta, product-description, category-page, about-us, email-template, social-post`

## 输出规则
- 输出目录：`D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\`
- 文件：`.md/.json/.txt`
- 最后一行：`FILE:file:///...`

## 示例
- `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" --help`
- `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" product-page --brand "Veytis" --industry "essential oils wholesale" --product "bulk lavender essential oil" --features "private label, bulk supply" --specs "4 fl oz / 120 mL" --moq "[verify]"`
- `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" video-script --brand "Juese Clothing" --topic "custom hoodie production process" --platform "TikTok" --duration "30s" --style "documentary" --no-subtitles false`
- `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" inquiry-reply --brand "Veytis" --industry "essential oils wholesale" --customer-message "We need 25kg lavender essential oil with COA and MSDS for private label, ship to Germany" --tone "professional"`
- `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" product-description --brand "Veytis" --industry "essential oils wholesale" --product "bulk lavender essential oil" --features "private label, bulk supply, COA available upon request" --specs "25kg bulk option [verify]" --style "premium B2B"`
- `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" category-page --brand "Veytis" --industry "essential oils wholesale" --category "Hydrosols" --product-count "12" --target-keyword "private label hydrosol supplier" --country "United States" --language "English"`
- `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" about-us --brand "Juese Clothing" --industry "custom garment factory" --mission "help apparel brands manage sampling and bulk production with clearer communication"`
- `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" email-template --brand "Juese Clothing" --industry "custom garment factory" --scenario "quote info request" --product "custom hoodies" --tone "professional"`
- `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" social-post --brand "Veytis" --industry "essential oils wholesale" --platform "LinkedIn" --topic "private label essential oils" --product "bulk essential oils" --tone "professional"`

## OpenClaw / Telegram
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> ...`
