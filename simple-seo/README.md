# Simple SEO

Simple SEO checks one web page's on-page SEO against a target keyword, then drafts fixes for you to review. It works in Claude Code and in Codex.

To install it, follow the steps at https://github.com/ai-automation-unlock/plugins.

## What's inside

| Skill | What it does |
|---|---|
| Page Audit (`page-audit`) | Checks the page's fit for the keyword, indexing, title, meta description, H1, intro, H2s, image alt text and internal links, then lists the problems from most to least important |
| Page Fix (`page-fix`) | Drafts a better title, meta description, H1 and intro. It leaves alone any part that's already fine |

## What it won't do

- Change your website or any files
- Research competitors or other sites
- Pull search volumes, rankings or scores from paid SEO tools
- Make up facts. If a draft needs a detail it doesn't have, it writes `[NEEDS REAL DETAIL]` and asks you

You don't need any paid accounts or API keys.

## How to use it

Ask in plain English, for example:

```text
Check the SEO of https://example.com/your-page for the keyword "your keyword"
```

After the audit, ask it to fix the problems. In Claude Code, you can also run a skill by name with `/simple-seo:page-audit` or `/simple-seo:page-fix`.

## Limits

- It checks one page at a time.
- It reads the page's HTML, not what a browser shows after it runs the page's scripts. If the content is added by JavaScript, it may miss it.
- If a site blocks automated requests, it asks you to paste the page's HTML instead of getting around the block.
- "No `noindex` tag" doesn't prove Google has indexed the page.
- It counts characters with a tool when it can. Recheck the final title and meta description before you publish them, especially if your site adds its name to every title.
