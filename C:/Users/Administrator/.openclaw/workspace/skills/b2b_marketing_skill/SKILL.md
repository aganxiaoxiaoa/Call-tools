---
name: b2b-marketing-skill
description: Local B2B independent-site marketing tool for GEO/SEO, blogs, landing pages, product pages, service pages, video scripts, image prompts, inquiry replies, FAQ, content calendar, and Google Ads keyword planning.
---

## Trigger rules
When user asks any of the following, call the local CLI directly:
- 写博客 / 博客简报 -> `blog-brief`
- 写博客初稿 / B2B SEO 博客 -> `blog-draft`
- GEO 内容计划 / GEO+SEO -> `geo-plan --geo-type both`
- 写落地页 -> `landing-page`
- 写产品页 -> `product-page`
- 写服务页 -> `service-page`
- 短视频脚本 -> `video-script`
- 图片提示词 -> `image-prompt`
- 客户询盘回复 / 英文回复 -> `inquiry-reply`
- FAQ -> `faq`
- 30天内容计划 -> `content-calendar`
- 广告关键词计划 -> `ad-keyword-plan`
- 否定关键词 -> `negative-keywords`
- SEO title/meta -> `seo-meta`
- 一键全套内容 -> `prompt-pack`

## Preferred call pattern
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> ...`

## Safety notes
- No paid API calls.
- Do not fabricate certifications, price, lead time, capacity, or client cases.
- Use `[verify]` / `available upon request` / `depending on order details` for uncertain items.
