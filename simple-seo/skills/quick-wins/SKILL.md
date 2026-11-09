---
name: quick-wins
description: Finds the pages on a website that are closest to getting more clicks from Google, using the site's own Google Search Console data through Composio. Use when someone asks for SEO quick wins, low-hanging fruit, which pages to improve first, or pages that almost rank on page one. Not for checking one page against a keyword (use page-audit), rewriting a page (use page-fix) or checking readiness for AI search (use ai-search-check).
---

# Quick Wins

Find the pages on one website that are closest to getting more clicks from Google, and say which to work on first. Use the site's real Google Search Console data, reached through Composio. Do not change anything.

## What you need

- Composio, connected to this app, with the user's Google Search Console linked inside it
- The website, if the user's Search Console has more than one

## Steps

1. **Check for Composio.** Look for Composio's tools, such as `COMPOSIO_SEARCH_TOOLS` and `COMPOSIO_REMOTE_WORKBENCH`. If they are not available, stop and tell the user how to connect Composio:
   - **Claude desktop app:** Settings, then Connectors, then Add custom connector. Name it Composio, use the URL `https://connect.composio.dev/mcp`, and sign in with a free Composio account. Then start a new session.
   - **Claude Code in Terminal:** connectors added in the Claude app also work in Claude Code when you're signed in with the same Claude account.
   - **Codex in the ChatGPT app:** click the gear at the bottom left, then MCP Servers, then Add server, then Streamable HTTP. Name it `composio`, use the URL `https://connect.composio.dev/mcp`, and add a header named `x-consumer-api-key` whose value is the Composio API key from https://dashboard.composio.dev. Then start a new chat.

2. **Check the Search Console connection.** Call `COMPOSIO_SEARCH_TOOLS` with the use case "query Google Search Console search analytics by page and query", and start a new session. Keep the session ID for every Composio call that follows. The response says whether `google_search_console` has an active connection, and lists the connected Google accounts.
   - If there is no active connection, call `COMPOSIO_MANAGE_CONNECTIONS` to add `google_search_console`. Show the user the sign-in link as a clickable link, and ask them to sign in with the Google account that owns their Search Console and reply when done. Then list the connections to confirm it is active before you continue.
   - If more than one Google account is connected and you can't tell which one owns the site, ask.

3. **Pick the website.** Let the script list the sites: run step 4 with `SITE` empty. Do not take the site from Composio's connection details, because they can be incomplete. Then use the property that matches the site the user named, exactly as Search Console lists it, such as `https://www.example.com/` or `sc-domain:example.com`.
   - If both kinds are listed for the same site, use the `sc-domain:` one. It covers every version of the address.
   - If the user's site isn't listed, tell them it isn't in this Search Console account and stop.
   - If the user didn't name a site and there is only one, the script uses it. If there are several, ask which one, even if one seems likely.

4. **Run the analysis.** Read `scripts/quick_wins.py` in this skill's folder. Fill in only the four settings at the top:
   - `SITE`: the property from step 3, or `""` to let the script list them
   - `ACCOUNT`: the account ID from step 2, or `""` if only one Google account is connected
   - `BRAND_TERMS`: the business's name, if the user gave it, such as `["acme plumbing"]`. Otherwise leave it empty
   - `SKIP_DOMAIN`: leave it `True`

   Send the whole file, with no other changes, as one `COMPOSIO_REMOTE_WORKBENCH` call. Do not call the Search Console tools yourself, write your own analysis or change the thresholds. The script pulls the last 90 days of Search Console data, up to 3 days ago, and does all the math. It prints one JSON result:
   - `"status": "ok"`: continue to step 5
   - `"status": "choose_site"`: ask the user which of the listed sites to use, then run it again with `SITE` set
   - `"status": "no_sites"`: this Google account has no verified Search Console sites. Ask the user to link the Google account that owns their Search Console, or to add and verify their site in Search Console themselves, then stop
   - `"status": "no_data"`: tell the user Search Console has no search data for that site in those dates, and stop
   - An error: tell the user what failed and stop. Do not guess any numbers

   **Check what was left out as brand searches.** The script leaves out searches containing the business's name or the domain name, and lists the top ones in `top_brand_searches_left_out`. If those look like searches for the service or place rather than the business's name, run it again with `SKIP_DOMAIN = False` and only the business's name in `BRAND_TERMS`. This matters for domains made of ordinary search words, like `orlandoplumbing.com`.

5. **Check the top pages.** Go down the candidates in order until 5 pass or you run out. For each one, request the page once, honestly, for example:

   ```bash
   curl -sL -A 'Mozilla/5.0 (compatible; QuickWins/1.0)' -D - -w '\n%{http_code} %{url_effective}\n' URL
   ```

   Read the headers and the page's `<head>`. Leave a page out of the table, and list it under "Left out" with the reason, if:
   - it returns 404, 410 or a 5xx error
   - it redirects to a different page. A redirect that only changes `http` to `https`, adds or removes `www`, or adds or removes a final `/` is the same page
   - it has `noindex` in a robots meta tag or an `X-Robots-Tag` header
   - its `rel="canonical"` points to a different page

   A 403, 405 or 429 means the site blocked the check, not that the page is broken. Keep the page and say the check was blocked. Do not retry with a different identity. If your own shell can't reach the internet, you may run the same request with Composio's `COMPOSIO_REMOTE_BASH_TOOL`. If you can't make requests at all, keep the pages and say so under "Left out."

   For each `also_at` address on the pages you keep, check it the same way. If it already redirects to the main address, say it looks fixed and the data may be from before the fix.

6. **Judge each candidate.** The script finds candidates with math. Before you recommend one, read its search term and page:
   - **A different business's name:** the searcher probably wants that business's own website or map listing, so more clicks may never come. Keep it, but say so in "Why" and move it below the others.
   - **Local and "near me" searches:** the position is an average across searchers in many places, and map results usually sit above it. Say that the business's Google Business Profile often matters more for these searches than this page.
   - **Question searches,** starting with how, what, why, can, does or cost, on a service or product page: say the question may need its own article rather than a rewrite of this page.
   - **The page doesn't match what the search is looking for:** say so.
   - **`top spot, few clicks` or `weak_title`:** tell the user to search the term in a private browser window first. An AI Overview, map results or an answer box above the page can take the clicks, and a new title won't fix that.
   - Do not drop a candidate just because you think it's hard. Say why instead.

7. **Write the report** in the format below.

## What the result means

| Field | Meaning |
|---|---|
| `kind: "almost top 3"` | The search term's average position is 4 to 10. Moving into the top 3 usually brings the most new clicks. Moving up usually needs a more complete page and links from the site's other pages, not just a new title |
| `kind: "page two"` | Average position 11 to 20. Few people look past page one. Moving up needs the same work as "almost top 3" |
| `kind: "top spot, few clicks"` | Average position 1 to 3, but it gets less than half the clicks the site usually gets in those spots. The title and meta description may be the cause, or something above the page may take the clicks (see step 6) |
| `weak_title: true` | Fewer than half the clicks the site usually gets at that position, with enough data to judge. The title and meta description may not be earning the click |
| `extra_clicks_per_month_all_searches` | A rough estimate of extra clicks a month if the page moved up one position range, added up over all its searches. It uses the site's own click rates. When it is `null`, the site doesn't have enough clicks in the top 3 to estimate, so pages are ranked by impressions |
| `site_totals` | All of the site's clicks and impressions from Google web search in those dates. Always report these as the site's totals. `named_search_totals` counts only the searches Google names, so it differs. If `site_totals` is `null`, report `named_search_totals` and say it leaves out rare searches |
| `competes` | Another page on the site also shows up for the same search. They may be competing, or they may answer different needs |
| `also_at` | The same page also shows up at a second address, such as with and without a final `/` |
| `rows_capped: true` | The site is very large, so only the top 50,000 rows were used. Say so under "About the numbers" |

## Report format

**Summary:** The site and dates, the site's total clicks and impressions, how many candidates the script found, and the single page to start with.

| # | Page | Search term | Average position | Impressions | Clicks | Why it's a quick win | Next step |
|---|---|---|---|---|---|---|---|

- Show up to 5 pages, in the script's order unless step 6 moved one down.
- Use the numbers from the script exactly. Impressions and clicks are for the main search term over the whole 90 days. Round the position to one decimal place.
- If `extra_clicks_per_month_all_searches` has values, add a "Rough extra clicks a month (all its searches)" column. Under the table, say it's a guide based on the site's own click rates, not a promise.
- **Next step:**
  - For `top spot, few clicks`, or when `weak_title` is true: after the private-window check, offer `page-fix` for that search term.
  - Otherwise: offer `page-audit` for that search term. Also suggest linking to the page from the site's most-visited related pages, using the search term in the link text.

**Pages competing for the same search:** List each one from `competes`, with both pages. Tell the user to check whether both pages answer the same need. If they do, pick one page to be the main page for that search, link to it from the other, and make the other page's title and H1 about its own angle. Do not delete, redirect, noindex or canonicalize either page based on this report alone. If there are none, write "None."

**Same page at two addresses:** List the pages with `also_at`, and what step 5 found. If one address doesn't already redirect, say a developer should permanently redirect it to the other. If there are none, write "None."

**Left out:** Pages from step 5 with the reason, or "None."

**About the numbers:**
- Positions are averages over 90 days. An AI Overview or a group of map results counts as one position.
- Google hides rare searches for privacy, so the totals for named searches are lower than the real ones.
- The last 3 days are left out because Search Console data is still incomplete.

**Next step:** Offer to run the first page's next step from the table.

## Rules

- Read only. Do not change Search Console or the website. Do not submit sitemaps, add sites, request indexing or use any other Composio app.
- Use only the numbers the script returns. Do not invent search volumes, rankings or traffic, and do not do the math yourself.
- Do not paste the raw Search Console data into the chat.
- Do not promise that a change will improve rankings or clicks.
- Request only the candidate pages and their `also_at` addresses in step 5. Do not follow their links or research other sites.
- Do not make requests look like they come from Googlebot or another search engine.
