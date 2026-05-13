# B2B Marketing Tool (Stage 3)

## 正式路径
- `D:\bot\tool\Business tools\b2b_marketing_tool.py`
- `D:\bot\tool\Business tools\README.md`
- `C:\Users\Administrator\.openclaw\workspace\skills\b2b_marketing_skill\SKILL.md`

> 正式入口是上面 3 个文件；不要使用 `BUSINESS_TOOLS.md` 作为正式入口。

## 15 个命令与用途
1. `geo-plan`：Generative GEO + Geographic SEO 计划
2. `blog-brief`：B2B SEO 博客简报
3. `blog-draft`：可编辑英文博客初稿
4. `landing-page`：落地页完整结构
5. `product-page`：产品页（Veytis/Juese差异化）
6. `service-page`：服务页结构
7. `video-script`：15/20/30/45/60s 分镜脚本
8. `image-prompt`：品牌一致性图片提示词
9. `inquiry-reply`：询盘解析 + 英文回复
10. `faq`：20-30 条 FAQ 分组
11. `content-calendar`：30 天内容计划
12. `prompt-pack`：一键整合全套输出
13. `ad-keyword-plan`：Google Ads 账户结构
14. `negative-keywords`：否定关键词分层策略
15. `seo-meta`：SEO/OG 元数据包

## 输出规则
每次运行输出到：
- `D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\<command>.md`
- `D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\<command>.json`
- `D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\<command>.txt`

stdout 最后一行固定：
- `FILE:file:///D:/bot/outputs/business_tools/YYYYMMDD_HHMMSS/<command>.md`

## OpenClaw / Telegram 调用方式
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> ...`

## 示例（每个命令）
```bash
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" geo-plan --brand "Veytis" --industry "essential oils wholesale" --country "United States" --language "English" --product "bulk essential oils" --keywords "bulk essential oils, private label essential oils" --geo-type both
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" blog-brief --brand "Veytis" --industry "essential oils wholesale" --topic "How to choose an essential oil supplier" --intent "commercial"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" blog-draft --brand "Veytis" --industry "essential oils wholesale" --topic "Private Label Essential Oils Guide" --intent "commercial"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" landing-page --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies" --country "United States" --language "English"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" product-page --brand "Veytis" --industry "essential oils wholesale" --product "bulk lavender essential oil" --country "United States" --language "English"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" service-page --brand "Juese Clothing" --industry "apparel OEM/ODM" --product "custom hoodie sampling and production" --country "United States" --language "English"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" video-script --brand "Juese Clothing" --topic "custom hoodie production process" --platform "TikTok" --duration "30s" --style "documentary" --no-subtitles false
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" image-prompt --brand "Veytis" --scene "premium essential oil product photo" --product "4 oz amber dropper bottle" --style "premium natural" --ratio "1:1"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" inquiry-reply --brand "Juese Clothing" --industry "custom garment factory" --customer-message "Hi, can you make 1000 t-shirts with embroidery and custom packaging, ship to UK before July 10?" --tone "professional"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" faq --brand "Veytis" --industry "essential oils wholesale" --product "hydrosols"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" content-calendar --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies" --country "United States" --language "English"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" ad-keyword-plan --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies" --country "United States" --language "English"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" negative-keywords --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies" --country "United States" --language "English"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" seo-meta --brand "Veytis" --industry "essential oils wholesale" --product "bulk lavender essential oil"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" prompt-pack --brand "Veytis" --industry "essential oils wholesale" --topic "Private Label Essential Oils" --country "United States" --language "English" --product "bulk essential oils"
```

## 验收命令
使用上面的 `Test-Path` + `--help` + 全命令示例进行验收，重点确认：
- 15 个命令都在 `--help`
- 每个命令最后一行为 `FILE:file:///...`
- `prompt-pack` 无 `AttributeError`
