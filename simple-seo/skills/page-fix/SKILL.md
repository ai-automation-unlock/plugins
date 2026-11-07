---
name: page-fix
description: Rewrites one web page's title, meta description, H1 and intro for a target keyword, as drafts for the user to review. Use when someone asks to fix a page's SEO, rewrite its title or meta description, or fix the problems from a page-audit report. Not for finding problems on a page (use page-audit).
---

# Page Fix

Write better versions of four parts of one web page: the title, meta description, H1 and intro. These are drafts for the user to review. Do not publish them.

## What you need

- The page URL
- The target keyword
- The `page-audit` report, if there is one

If the URL or keyword is missing, ask for it before you start. If there is no report, keep going and work from the page itself. Do not tell the user they must run `page-audit` first.

## Steps

1. Read the page's raw HTML, for example with `curl -sL`. Do not use a tool that summarizes the page, because you need the exact title, meta description and H1. If you cannot get the raw HTML, stop and ask the user to paste the page's HTML. Do not guess what is on it.
2. Decide whether the page fits the keyword. Use the report's "Page fit" finding if there is one. If the page is a poor fit, tell the user before you write anything. If one of the page's links or the report points to a better page, name it. Ask whether to continue with this page anyway.
3. Find what needs to change in the four parts. If there is a report, change only the parts it lists as problems, and leave the rest as they are. If the problem is more than one H1, don't write a new headline. Name the H1 to keep, suggest changing the others to H2s, and list it under "Not changed."
4. Write new versions that meet the standards below. Leave a part as it is if it already meets them, and say so. If none of the four parts needs a change, say so, list any other report problems under "Not changed," and stop without writing the result table.
5. Count the characters in the new title and meta description. Shorten any that are over the limit. If the site seems to add its name to every title, ask the user, because that counts toward the limit.

   When a shell is available, count characters with a tool instead of estimating. Decode HTML entities such as `&amp;` first. Put the text in a quoted heredoc, as below, so nothing in it can run as a command, and use a UTF-8 locale so dashes and accents count as one character each:

   ```bash
   LC_ALL=en_US.UTF-8 tr -d '\n' <<'EOF' | LC_ALL=en_US.UTF-8 wc -m
   text goes here
   EOF
   ```
6. Write the result in the format below.

## Standards

A part needs a change only if it misses its standard. These match `page-audit`'s checks.

| Part | Standard |
|---|---|
| Title | About the page's topic, 60 characters or fewer, and includes the keyword or a close variation |
| Meta description | Matches what the page offers, and 160 characters or fewer |
| H1 | One clear headline that makes the page's topic obvious. It does not have to match the title |
| Intro | The first 100 words of the main content, after the H1, make the topic clear. If they do, leave the intro as it is, even if it is long. A rewrite is about 100 words or fewer, makes the topic clear in the first two sentences, and sounds like the rest of the page |

When you write a new title, put the keyword near the start if that reads naturally. When you write a new meta description, give a reason to click.

## Result format

| Part | Current | New | Why |
|---|---|---|---|

Include the character count for the new title and meta description.

**Not changed:** List any problems from the report that fall outside these four parts, and any H1 you left for the user to change to an H2 (see step 3), or write "None."

**Needs your input:** List any facts you need from the user, or write "None."

**Next step:** Tell the user to review the drafts, put the ones they approve on the page, and run `page-audit` again.

## Rules

- Do not change any files or the live site.
- Request only the page the user gave you. Do not follow its links, research other sites or write new sections. Work only from the page, the report and what the user tells you.
- Do not invent facts, including prices, reviews, results, awards, locations or years. If a good rewrite needs a fact you do not have, write `[NEEDS REAL DETAIL]` and list it under "Needs your input."
- Do not claim anything the page does not actually offer.
- Do not repeat the keyword just to fit it in more often.
- Do not promise that a change will improve rankings.
- Do not make your requests look like they come from Googlebot or another search engine. If the site blocks you, do not retry with a different identity to get past the block. Ask the user to paste the HTML instead.
