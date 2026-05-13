# B2B Marketing Tool (Stage 2)

## Paths
- `D:\bot\tool\Business tools\b2b_marketing_tool.py`
- `D:\bot\tool\Business tools\README.md`
- `C:\Users\Administrator\.openclaw\workspace\skills\b2b_marketing_skill\SKILL.md`

## Commands
geo-plan, blog-brief, blog-draft, landing-page, video-script, image-prompt, inquiry-reply, faq, content-calendar, prompt-pack, product-page, service-page, ad-keyword-plan, negative-keywords, seo-meta

## Stage-2 enhancements
- `product-page`: SEO/meta/slug, hero, overview, use cases, specs table, MOQ/lead time, custom options, docs, FAQ, CTA, image prompts, internal links.
- `service-page`: positioning, audience, workflow, buyer inputs, QC checkpoints, deliverables, risks, FAQ, CTA.
- `negative-keywords`: must_exclude/review_before_excluding/keep_or_monitor and risk groups.
- `ad-keyword-plan`: campaign structure, match types, ad groups, keyword tiers, LP mapping, ad angles, tracking notes.
- `inquiry-reply`: parses quantity/product/customization/material/destination/packaging/deadline/docs.
- `.md` output is human-readable report (`# Title / ## Summary / ## Sections / ## Next Steps`).

## Output
- Saves `.md/.json/.txt` to `D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\`
- Last stdout line: `FILE:file:///...`

## Example
`py "D:\bot\tool\Business tools\b2b_marketing_tool.py" product-page --brand "Veytis" --industry "essential oils wholesale" --product "bulk lavender essential oil" --country "United States" --language "English"`
