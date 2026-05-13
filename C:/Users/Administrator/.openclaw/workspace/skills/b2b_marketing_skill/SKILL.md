---
name: b2b-marketing-skill
description: Local B2B independent-site marketing tool for GEO/SEO, blogs, landing pages, product pages, service pages, video scripts, image prompts, inquiry replies, FAQ, content calendar, and Google Ads keyword planning.
---

## Trigger rules
- 写博客 -> `blog-draft` / `blog-brief`
- GEO -> `geo-plan`
- 落地页 -> `landing-page`
- 产品页 -> `product-page`
- 服务页 -> `service-page`
- 视频脚本 -> `video-script`
- 图片提示词 -> `image-prompt`
- 询盘回复 -> `inquiry-reply`
- FAQ -> `faq`
- 内容日历 -> `content-calendar`
- 广告关键词 -> `ad-keyword-plan`
- 否定关键词 -> `negative-keywords`
- SEO meta -> `seo-meta`
- 一键全套 -> `prompt-pack`
- 产品短描述/产品卡片 -> `product-description`
- 品类页/集合页 -> `category-page`
- 关于我们 -> `about-us`
- 开发信/跟进邮件 -> `email-template`
- LinkedIn/社媒帖子 -> `social-post`

## Preferred command
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> ...`

## Safety
- 不编造认证、产能、价格、交期、客户案例。
- 不确定信息标记 `[verify]` / `available upon request` / `depending on order details`。
- 以最终 `FILE:file:///...` 输出为准。
