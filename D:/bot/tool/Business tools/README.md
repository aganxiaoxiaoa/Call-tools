# B2B Marketing Tool (Stage 3.1+)

## Official paths
- `D:\bot\tool\Business tools\b2b_marketing_tool.py`
- `D:\bot\tool\Business tools\README.md`
- `C:\Users\Administrator\.openclaw\workspace\skills\b2b_marketing_skill\SKILL.md`

Do **not** use `BUSINESS_TOOLS.md` as official entry.

## 20 commands
geo-plan, blog-brief, blog-draft, landing-page, product-page, service-page, video-script, image-prompt, inquiry-reply, faq, content-calendar, prompt-pack, ad-keyword-plan, negative-keywords, seo-meta, product-description, category-page, about-us, email-template, social-post

## Output rules
- Output folder: `D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\`
- Files: `.md`, `.json`, `.txt`
- Last stdout line always: `FILE:file:///...`

## Invocation
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" <subcommand> ...`

## Acceptance examples
Use the command set from your validation checklist for:
- `--help` (20 commands)
- core: `geo-plan`, `product-page`, `service-page`, `content-calendar`, `inquiry-reply`
- new: `product-description`, `category-page`, `about-us`, `email-template`, `social-post`
