---
name: b2b-marketing-skill
description: Local B2B independent-site marketing tool for GEO/SEO, blogs, landing pages, product pages, service pages, video scripts, image prompts, inquiry replies, FAQ, content calendar, and Google Ads keyword planning.
---

## Trigger rules
- 用户说“写博客/博客初稿” -> `blog-draft`
- 用户说“博客大纲/简报” -> `blog-brief`
- 用户说“GEO/地理SEO/AI搜索优化” -> `geo-plan`
- 用户说“落地页” -> `landing-page`
- 用户说“产品页” -> `product-page`
- 用户说“服务页” -> `service-page`
- 用户说“视频脚本/短视频脚本” -> `video-script`
- 用户说“图片提示词” -> `image-prompt`
- 用户说“客户询盘/英文回复” -> `inquiry-reply`
- 用户说“FAQ” -> `faq`
- 用户说“内容日历” -> `content-calendar`
- 用户说“广告关键词/Google Ads关键词” -> `ad-keyword-plan`
- 用户说“否定关键词” -> `negative-keywords`
- 用户说“SEO title/meta” -> `seo-meta`
- 用户说“一键全套” -> `prompt-pack`

## Preferred command
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> ...`

## Safety rules
- 不编造认证、产能、价格、交期、客户案例。
- 不确定信息必须标注 `[verify]`，或使用 `available upon request` / `depending on order details`。
- 文件输出以最后一行 `FILE:file:///...` 为准。
- 不调用付费 API。
