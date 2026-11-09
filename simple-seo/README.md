# Simple SEO

Simple SEO finds the pages on your site that are closest to getting more clicks from Google, checks a page's on-page SEO against a target keyword, checks whether a page is ready for AI search like ChatGPT and Claude, then drafts fixes for you to review. It works in Claude Code and in Codex.

To install it, follow the steps at https://github.com/ai-automation-unlock/plugins.

## What's inside

| Skill | What it does |
|---|---|
| Quick Wins (`quick-wins`) | Reads your Google Search Console data through Composio and lists the pages closest to getting more clicks, with the search term to work on for each. It also flags pages competing for the same search |
| Page Audit (`page-audit`) | Checks the page's fit for the keyword, indexing, title, meta description, H1, intro, H2s, image alt text and internal links, then lists the problems from most to least important |
| Page Fix (`page-fix`) | Drafts a better title, meta description, H1 and intro. It leaves alone any part that's already fine |
| AI Search Check (`ai-search-check`) | Shows which AI crawlers, such as ChatGPT's, Claude's and Perplexity's, can reach a page. Checks whether the page's text is easy for AI search to read and quote, and whether its structured data is valid and matches the page. Drafts an answer block, structured data and any `robots.txt` lines |

## What it won't do

- Change your website, your `robots.txt`, your Search Console or any files
- Research competitors or other sites
- Pull search volumes, rankings or scores from paid SEO tools
- Make up facts. If a draft needs a detail it doesn't have, it writes `[NEEDS REAL DETAIL]` and asks you

Page Audit, Page Fix and AI Search Check don't need any accounts. Quick Wins needs a free Composio account with your Google Search Console linked to it. Your Search Console data passes through Composio to reach Claude or Codex.

## How to use it

Ask in plain English, for example:

```text
Check the SEO of https://example.com/your-page for the keyword "your keyword"
```

To find where to start, ask:

```text
Find my SEO quick wins
```

To check a page for AI search, ask:

```text
Is https://example.com/your-page ready for AI search like ChatGPT and Claude?
```

After the audit, ask it to fix the problems. In Claude Code, you can also run a skill by name with `/simple-seo:page-audit` or `/simple-seo:page-fix`.

## Limits

- Quick Wins uses the last 90 days of Search Console data. A new site, or one with little search traffic, may not have enough data. Positions are averages, and Google hides rare searches for privacy.
- Its "extra clicks" numbers are rough estimates from your site's own click rates, not promises.
- Page Audit, Page Fix and AI Search Check check one page at a time.
- AI Search Check can't see settings outside `robots.txt`, such as Cloudflare's AI crawler blocking. No one can guarantee that an AI tool will quote a page.
- It reads the page's HTML, not what a browser shows after it runs the page's scripts. If the content is added by JavaScript, it may miss it.
- If a site blocks automated requests, it asks you to paste the page's HTML instead of getting around the block.
- "No `noindex` tag" doesn't prove Google has indexed the page.
- It counts characters with a tool when it can. Recheck the final title and meta description before you publish them, especially if your site adds its name to every title.
