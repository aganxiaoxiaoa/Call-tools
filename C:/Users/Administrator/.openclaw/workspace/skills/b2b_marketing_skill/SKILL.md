---
name: b2b-marketing-skill
description: Local B2B independent-site marketing tool for GEO/SEO, blogs, landing pages, product pages, service pages, video scripts, image prompts, inquiry replies, FAQ, content calendar, and Google Ads keyword planning.
---

## Trigger rules (20 commands)
- 写博客: `blog-draft` / `blog-brief`
- GEO: `geo-plan`
- 落地页: `landing-page`
- 产品页: `product-page`
- 服务页: `service-page`
- 视频脚本: `video-script`
- 图片提示词: `image-prompt`
- 客户询盘回复: `inquiry-reply`
- FAQ: `faq`
- 内容日历: `content-calendar`
- 广告关键词: `ad-keyword-plan`
- 否定关键词: `negative-keywords`
- SEO title/meta: `seo-meta`
- 一键全套: `prompt-pack`
- 产品短描述: `product-description`
- 品类页: `category-page`
- 关于我们: `about-us`
- 开发信/跟进邮件: `email-template`
- 社媒帖子: `social-post`

If user intent is unclear, choose the closest command instead of generic response.

## Safety
- Do not fabricate certifications, capacity, price, lead time, or customer cases.
- Use `[verify]` for uncertain details.
- Prefer FILE:file output markdown artifact by default.
- Command format: `py "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> ...`
