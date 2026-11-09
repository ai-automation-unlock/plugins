---
name: ai-search-check
description: Checks whether one web page is ready to be found and quoted by AI search, such as ChatGPT search, Claude, Perplexity and Google's AI Overviews, then drafts the fixes. Checks which AI crawlers robots.txt lets in, whether the text is in the page's HTML, whether it answers its question up front, and its structured data. Use when someone asks about AI search, GEO, AI Overviews, showing up in ChatGPT or Claude, or AI crawlers. Not for regular on-page SEO against a keyword (use page-audit) or finding which pages to work on (use quick-wins).
---

# AI Search Check

Check whether one web page is ready to be found and quoted by AI search tools, then draft the fixes for the user to review. Do not change anything.

No one can guarantee that an AI tool will quote a page. This check covers what the site owner controls: whether the AI tools can reach the page, read it, understand who it's from and quote a clear answer.

## What you need

- The page URL
- The main question the page answers, or its target keyword. If the user didn't give one, work it out from the page's title and H1, and say what you assumed

If the URL is missing, ask for it.

## Steps

1. **Run the checker.** Run `scripts/ai_search_check.py` from this skill's folder by its full path, without changing directory first:

   ```bash
   python3 "/full/path/to/this/skill/scripts/ai_search_check.py" "URL"
   ```

   It fetches the page and the site's `robots.txt` once each, identifying itself honestly, and prints a JSON summary. Do not fetch the page in other ways, and do not repeat requests while pretending to be a crawler.
   - If the command can't reach the internet, ask the user to allow it and run it again.
   - If it can't run at all, say so and stop. Do not guess the results.
   - If `page.status` is 401, 403, 405, 429 or 503, the site refused the check. Say so, and ask the user to paste the page's HTML if they want the content checked. Still report the `robots.txt` results.
   - If `robots_txt.status` starts with "refused," "error" or "unreachable," `crawlers` is empty. Mark the crawler checks "Could not check," and tell the user to open their `robots.txt` in a browser and check it themselves.

2. **Run each check** in the table below, using the checker's output. Mark each one Pass, Needs work or Could not check.

3. **Judge the writing.** Read `first_150_words_after_h1` and `main_content_excerpt`:
   - **Answer first:** do the first 2 to 4 sentences of the main content directly answer the page's main question, in a way that makes sense if quoted alone? It passes only if there's at least one complete sentence that names the subject and answers the question. Menus, bylines, buttons and a list of facts with no sentence don't count.
   - **Specific facts:** does the content give real details someone could quote, such as prices, hours, areas served, numbers, names, steps or dates? Vague marketing lines don't count.

4. **Draft the fixes** described under "Fixes."

5. **Write the report** in the format below.

## Checks

| Area | Check | Pass when | Priority if it fails |
|---|---|---|---|
| Reach | The page loads | `page.status` is 200 and `final_url` is the same page. A change only to `https`, `www` or a final `/` is the same page | High |
| Reach | Search engines may index it | `noindex` is false in `robots_meta` and `x_robots_tag` | High |
| Reach | This is the main version | `canonical` is empty or points to this page. If it points elsewhere, search engines and AI answers use the other page instead | High |
| Reach | AI answers may quote it | `nosnippet` is false and `max_snippet` isn't 0. Google says these, and `noindex`, also limit AI Overviews and AI Mode | High |
| Reach | Copilot may use it | `bing_noarchive` is false and `bing_ai_grounding` isn't "disallow" or "disallowextended". Bing says `noarchive` keeps a page out of Copilot answers, and `nocache` limits Copilot to the title, address and snippet. Bing is replacing these with page-level `ai-grounding` and `ai-training` settings by March 1, 2027 | Medium |
| Reach | AI search crawlers are allowed | Every crawler with `job: "search"` has `page_allowed: true` | High |
| Reach | `robots.txt` works | `robots_txt.status` is "found" or "missing." A server error can make crawlers stay away from the whole site | High |
| Read | The text is in the HTML | `likely_needs_javascript` is false. AI crawlers generally don't run JavaScript. If `almost_empty` is true on a page that should have content, the text probably needs JavaScript. A short contact page can be almost empty and still be fine | High |
| Read | Answer first | Your judgment from step 3 | Medium |
| Read | Specific facts | Your judgment from step 3 | Medium |
| Read | Easy to pull apart | It has H2s that describe their sections, and lists or a table where they help. Headings phrased as the questions people ask are a plus | Low |
| Identity | Structured data is valid | `structured_data_errors` is empty. An error about line breaks inside text is minor | Medium |
| Identity | Structured data fits the page | There is structured data of a type that fits: a `LocalBusiness` type, or a more specific one like `Plumber`, for a business page; `Article` or `BlogPosting` for a post; `Product` or `ProductGroup` for a product; `Organization` for a company's main pages | Medium |
| Identity | Structured data matches the page | Every value in `found_on_page` is true. If one is false, look at the page text before reporting it. "St." and "Street," or a slightly longer business name, still match | Medium |
| Freshness | Shows when it was updated | A `dateModified` in the structured data, a date in `dates`, or a visible "updated" date in the text | Low |

**Report, but don't mark as a problem:**

- **Training crawlers** (`job: "training"`): blocking these keeps the site's content out of AI training. It doesn't remove the site from ChatGPT, Claude or Perplexity search, or from Google Search and AI Overviews. One exception: `Google-Extended` also controls whether Google's Gemini apps may use the page when answering. This is the owner's choice. List which ones are blocked.
- **User fetchers** (`job: "user"`): these fetch a page when someone asks an AI tool about it. Perplexity says its fetcher generally ignores `robots.txt`, OpenAI says `robots.txt` may not apply to its fetcher, and Meta says its fetcher may bypass it. List which ones are blocked.
- **Different rules for different visitors:** some sites show `robots.txt` differently to different visitors. If a result looks surprising, such as Googlebot blocked on a site that gets search traffic, say so.
- **Cloudflare:** if `behind_cloudflare` is true, Cloudflare can also block AI crawlers in its own settings, separate from `robots.txt`. Tell the user to check the bot and AI crawler settings in their Cloudflare dashboard. This check can't see those settings.

## Crawlers this checks

| Job | Crawler | Used for |
|---|---|---|
| Search | `Googlebot` | Google Search, including AI Overviews and AI Mode |
| Search | `Bingbot` | Bing, which also feeds Microsoft Copilot |
| Search | `OAI-SearchBot` | ChatGPT search |
| Search | `Claude-SearchBot` | Claude's search |
| Search | `PerplexityBot` | Perplexity |
| Search | `Applebot` | Siri, Spotlight and Safari. If `robots.txt` doesn't name it, Apple follows the Googlebot rules |
| Search | `DuckAssistBot` | DuckDuckGo's AI answers |
| Search | `Meta-WebIndexer` | Meta AI's search |
| User fetch | `ChatGPT-User`, `Claude-User`, `Perplexity-User`, `Meta-ExternalFetcher` | Fetch a page when a user asks |
| Training | `GPTBot`, `ClaudeBot`, `Google-Extended`, `Applebot-Extended`, `Meta-ExternalAgent`, `CCBot` | Collect content for AI training. `Google-Extended` also covers Gemini apps' answers, but doesn't affect Google Search |

## Fixes

Draft a fix only for checks marked Needs work.

- **Answer block:** 2 to 4 sentences to put right after the H1. They should answer the page's main question directly, using only facts from the page or from the user. If a good answer needs a fact you don't have, write `[NEEDS REAL DETAIL]` and list it under "Needs your input." Match the page's tone.
- **Structured data:** a complete JSON-LD block for the page's `<head>`, using a type from the Checks table. Use only facts that appear on the page. Leave out any field you can't fill from the page rather than guessing. Don't turn marketing claims into facts: "serving Florida since 1963" isn't a founding date, and "24/7 service" isn't opening hours. Ask the user instead. Before you show it, check that it's valid JSON, for example with `python3 -m json.tool`. Tell the user to test it with Google's Rich Results Test or the Schema Markup Validator before publishing.
- **Structured data that doesn't match:** say which value differs from the page, and which one the user should correct.
- **`robots.txt`:** if a search crawler is blocked, write the lines that would allow it, and say where they go. Don't change the training crawler rules. If the user wants to change those, give them both options and let them choose.
- **`noindex`, `nosnippet`, `noarchive` or a canonical to another page:** say where it was found, and that a developer or the site's SEO plugin settings can change it, if it's there by mistake.
- **Text that needs JavaScript:** say the page's main text should be in the HTML the server sends. This is a job for the site's developer or website builder settings.
- **Freshness:** suggest showing a "Last updated" date on the page, and adding `dateModified` to the structured data when the page is updated.

Do not suggest these. Google says AI features need no special files or structured data, and the other tools above don't say they use them:

- an `llms.txt` file
- FAQ structured data. Google stopped showing FAQ results in Search in 2026
- repeating the keyword or question many times

## Report format

**Summary:** One sentence on the page's biggest issue for AI search, and the question you checked it against.

**AI crawlers:** A short table with one row per company in the crawler list: whether its search crawler can reach the page, and whether its training crawler is blocked. Write "None in this check" where the list has no crawler of that kind for the company. Then the Cloudflare note, if it applies.

| Priority | Problem | Why it matters for AI search | What to change |
|---|---|---|---|

Sort from High to Low. List only checks marked Needs work. If there are none, write "No problems found" instead of the table.

**Could not check:** List these, or write "None."

**What's working:** Up to three things.

**Drafts to review:** The answer block, the structured data and any `robots.txt` lines, each in its own code block, with where it goes.

**Needs your input:** Facts you need from the user, or "None."

**Next step:** If the title, meta description or H1 also need work, offer `page-fix`. Remind the user to recheck the page with this skill after publishing changes.

## Rules

- Read only. Do not change any files, the website or `robots.txt`.
- Request only the page the user gave you and its site's `robots.txt`. Do not follow links or research other sites.
- Never pretend to be a search engine or AI crawler. Do not test what a crawler sees by sending its name.
- Do not invent facts, prices, reviews, hours, addresses or dates.
- Do not promise that a change will get the page quoted, ranked or shown in AI answers.
- Report only what the checker returned and what you read on the page.
