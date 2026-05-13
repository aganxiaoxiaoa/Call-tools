# B2B Marketing Tool (Stage 2 Enhanced)

## Official paths
- `D:\bot\tool\Business tools\b2b_marketing_tool.py`
- `D:\bot\tool\Business tools\README.md`
- `C:\Users\Administrator\.openclaw\workspace\skills\b2b_marketing_skill\SKILL.md`

## Commands
- geo-plan
- blog-brief
- blog-draft
- landing-page
- product-page
- service-page
- video-script
- image-prompt
- inquiry-reply
- faq
- content-calendar
- prompt-pack
- ad-keyword-plan
- negative-keywords
- seo-meta

## Output rule
Every run writes:
- `D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\<command>.md`
- `D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\<command>.json`
- `D:\bot\outputs\business_tools\YYYYMMDD_HHMMSS\<command>.txt`

Last stdout line is always:
- `FILE:file:///.../<command>.md`

## Examples (all commands)
```bash
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" geo-plan --brand "Veytis" --industry "essential oils wholesale" --country "United States" --language "English" --product "bulk essential oils" --keywords "bulk essential oils, private label essential oils" --geo-type both
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" blog-brief --brand "Veytis" --industry "essential oils wholesale" --topic "How to choose an essential oil supplier" --intent "commercial"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" blog-draft --brand "Veytis" --industry "essential oils wholesale" --topic "Private label essential oils guide" --intent "commercial"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" landing-page --brand "Juese Clothing" --industry "apparel OEM/ODM" --product "custom hoodies"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" product-page --brand "Veytis" --industry "essential oils wholesale" --product "bulk lavender essential oil"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" service-page --brand "Juese Clothing" --industry "apparel OEM/ODM" --product "custom hoodie sampling and production"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" video-script --brand "Juese Clothing" --topic "custom hoodie process" --platform "TikTok" --duration "30s" --style "documentary"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" image-prompt --brand "Veytis" --scene "premium essential oil product photo" --product "4 oz amber dropper" --style "premium" --ratio "1:1"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" inquiry-reply --brand "Juese Clothing" --industry "custom garment factory" --customer-message "Hi, can you make 500 custom hoodies with puff print?" --tone "professional"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" faq --brand "Veytis" --industry "essential oils wholesale" --product "hydrosols"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" content-calendar --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" prompt-pack --brand "Veytis" --industry "essential oils wholesale" --topic "Private Label Essential Oils" --country "United States" --language "English" --product "bulk essential oils"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" ad-keyword-plan --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" negative-keywords --brand "Juese Clothing" --industry "custom garment factory" --product "custom hoodies" --country "United States" --language "English"
py "D:\bot\tool\Business tools\b2b_marketing_tool.py" seo-meta --brand "Veytis" --product "bulk lavender essential oil"
```
