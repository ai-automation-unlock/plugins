---
name: page-audit
description: Checks one web page's on-page SEO against a target keyword and returns a prioritized list of problems. Use when someone asks to audit a page, check a page's SEO, or review a page for a keyword. Not for rewriting the page (use page-fix).
---

# Page Audit

Check one web page against one target keyword. Report what is wrong, most important first. Do not rewrite the page.

## What you need

- The page URL
- The target keyword

If either is missing, ask for it before you start.

## Steps

1. Read the page's raw HTML and response headers, for example with `curl -sL -D -`. Do not use a tool that summarizes the page, because the checks need the exact tags. If you cannot get the raw HTML, stop and ask the user to paste it. Do not guess what is on it.
2. Run each check below. If what you could read does not let you confirm a check, mark it "Could not check." If the page's main content looks like it is built by JavaScript after loading, say so under "Could not check."
3. If the page is a poor fit for the keyword, say so in the summary. If one of its links clearly leads to a better page for the keyword, name that page, but do not open or audit it.
4. Give each problem the priority shown in the checks table.
5. Write the report in the format below.

## Checks

When a shell is available, count characters with a tool instead of estimating. Decode HTML entities such as `&amp;` first. Put the text in a quoted heredoc, as below, so nothing in it can run as a command, and use a UTF-8 locale so dashes and accents count as one character each:

```bash
LC_ALL=en_US.UTF-8 tr -d '\n' <<'EOF' | LC_ALL=en_US.UTF-8 wc -m
text goes here
EOF
```

| Item | What to check | Priority if it fails |
|---|---|---|
| Page fit | The page's main purpose matches what someone searching the keyword wants. Judge from the keyword's wording and the page. Do not search the web | High |
| Indexing | No `noindex` in a robots meta tag or an `X-Robots-Tag` header | High |
| Title | It exists and is about the page's topic | High |
| Title length and keyword | It is 60 characters or fewer and includes the keyword or a close variation | Medium |
| Meta description | It exists and matches what the page offers | Medium |
| Meta description length | It is 160 characters or fewer | Low |
| H1 | There is one, and it makes the page's topic clear | High if missing or about a different topic, Medium if there is more than one |
| Intro | The first 100 words of the main content, after the H1, make it clear the page covers the keyword's topic | Medium |
| H2s | There are H2s, and each describes the section under it | Low |
| Images | Images that carry information, such as diagrams, charts, screenshots and product photos, have alt text that describes what they show, not just the page title. Logos, author photos and decorative images can have empty alt text | Low |
| Internal links | The main content links to related pages on the same site. Menus and footers do not count | Low |

## Report format

**Summary:** One sentence on the page's biggest issue.

| Priority | Problem | Why it matters | What to change |
|---|---|---|---|

Sort the table from High to Low. List only problems the user should change.

**Could not check:** List these items, or write "None."

**What's working:** List up to three things.

**Next step:** If any problem involves the title, meta description, H1 or intro, offer to draft fixes with the `page-fix` skill, and say that any other problems need separate edits. If none do, or `page-fix` is not available, say so and end the report.

## Rules

- Do not change any files or the live site, and do not offer to.
- Request only the page the user gave you. Do not follow its links or research other sites.
- Do not make your requests look like they come from Googlebot or another search engine. If the site blocks you, do not retry with a different identity to get past the block. Ask the user to paste the HTML instead.
- Report only problems from the checks above.
- Report only what you saw on the page.
- Do not invent search volumes, rankings, competitors or scores.
- Do not promise that a change will improve rankings.
- Do not recommend repeating the keyword just to fit it in more often.
