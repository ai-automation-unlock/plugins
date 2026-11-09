# AI Automation Unlock plugins

Plugins for Claude Code and Codex from [AI Automation Unlock](https://www.aiautomationunlock.com).

| Plugin | What it does |
|---|---|
| [Simple SEO](simple-seo/README.md) | Finds the pages on your site that are closest to more Google clicks, checks a page's on-page SEO against a keyword, checks whether a page is ready for AI search like ChatGPT and Claude, then drafts fixes for you to review |

These steps are written for a Mac. You don't need a GitHub account.

**What you need:** Claude Code with a paid Claude plan (Pro or higher), or the ChatGPT desktop app with a plan that includes Codex. You can install in one or both. Simple SEO's Quick Wins skill also needs a free Composio account and Google Search Console (Step 4).

## Step 1: Make sure your Mac has Git

Claude Code and Codex download plugins with Git. Open the Terminal app and run:

```bash
git --version
```

If it prints a version number, go on to the next step. If a window asks to install the command line developer tools, click **Install** and wait until it finishes. That can take several minutes.

## Step 2: Install in Claude Code

You need Claude Code's command-line tool. To check, run `claude --version` in Terminal. If you get "command not found," install it from https://code.claude.com/docs/en/setup, then open a new Terminal window.

Run these two commands:

```bash
claude plugin marketplace add ai-automation-unlock/plugins
```

```bash
claude plugin install simple-seo@ai-automation-unlock
```

Then start a new Claude Code session. A session that was already open won't see the plugin. In the Claude desktop app, start a new session in the Code tab.

## Step 3: Install in Codex

Codex's command-line tool comes with the ChatGPT desktop app, so you don't need to install anything else. The commands below use its full location, which assumes the ChatGPT app is in your Applications folder. If you installed Codex's command-line tool on its own, type `codex` instead of the long path.

Run these two commands:

```bash
/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex plugin marketplace add ai-automation-unlock/plugins
```

```bash
/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex plugin add simple-seo@ai-automation-unlock
```

Then fully quit the ChatGPT app with Cmd + Q and open it again. You'll find Simple SEO in the plugins list under Customize.

If you get "No such file or directory," update the ChatGPT app and try again. Older versions don't include Codex's command-line tool.

## Step 4: Connect Composio for Quick Wins (optional)

Simple SEO's Quick Wins skill reads your Google Search Console data to find the pages closest to getting more clicks. It reaches Search Console through Composio, a free service. Page Audit and Page Fix work without it, so you can skip this step and come back later.

You need a free Composio account at https://composio.dev, and a website that's set up in Google Search Console.

**In the Claude desktop app** (this also covers Claude Code when you're signed in with the same Claude account):

1. Open Settings, then Connectors, then **Add custom connector**.
2. Name it `Composio`, enter the URL `https://connect.composio.dev/mcp`, and add it.
3. Sign in to Composio when it asks.

**In Codex, in the ChatGPT app:**

1. In https://dashboard.composio.dev, copy your Composio API key.
2. In the ChatGPT app's Codex settings, click the gear at the bottom left, then **MCP Servers**, then **Add server**, then **Streamable HTTP**.
3. Name it `composio` and enter the URL `https://connect.composio.dev/mcp`.
4. Add a header named `x-consumer-api-key`, and paste your Composio API key as its value. Save.

**The first time you run Quick Wins,** it gives you a link to connect Google Search Console to Composio. Sign in with the Google account that owns your Search Console, then tell it you're done. You only do this once.

Your Search Console data passes through Composio to reach Claude or Codex. Quick Wins only reads it. It never changes your website or Search Console.

## Step 5: Try it

In Claude Code or Codex, ask in plain English:

```text
Check the SEO of https://example.com/your-page for the keyword "your keyword"
```

Use your own page and keyword. If it asks for permission to run `curl`, allow it. That's how it reads your page. After the audit, ask it to fix the problems it found. It gives you drafts to review. It never changes your website.

If you connected Composio, ask:

```text
Find my SEO quick wins
```

It lists the pages closest to getting more clicks, with the search term to work on for each, and offers to check the first one. Codex asks you to approve each Composio step. That's normal.

To check whether a page is ready for AI search, ask:

```text
Is https://example.com/your-page ready for AI search like ChatGPT and Claude?
```

It shows which AI tools can reach the page, checks whether the page is easy for them to read and quote, and drafts the fixes. It doesn't need Composio. If it asks for permission to run `python3`, allow it. That's how it checks your page.

In Claude Code, you can also run a skill by name with `/simple-seo:quick-wins`, `/simple-seo:page-audit`, `/simple-seo:page-fix` or `/simple-seo:ai-search-check`.

## Get updates

When a new version is released, run these.

In Claude Code:

```bash
claude plugin marketplace update ai-automation-unlock
```

```bash
claude plugin update simple-seo@ai-automation-unlock
```

In Codex:

```bash
/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex plugin marketplace upgrade ai-automation-unlock
```

Then start a new session. For the ChatGPT app, quit it and open it again.

## Uninstall

In Claude Code:

```bash
claude plugin uninstall simple-seo@ai-automation-unlock
```

In Codex:

```bash
/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex plugin remove simple-seo@ai-automation-unlock
```

This removes the plugin but keeps the AI Automation Unlock store added, so you can install it again later. To remove the store too, run `claude plugin marketplace remove ai-automation-unlock` in Claude Code, or the same long Codex path followed by `plugin marketplace remove ai-automation-unlock`.

## If something goes wrong

| What you see | What to do |
|---|---|
| A window asks to install the command line developer tools | Click **Install**, wait until it finishes, then run the command again |
| `claude: command not found` | Install Claude Code from https://code.claude.com/docs/en/setup, then open a new Terminal window |
| "No such file or directory" for the long Codex path | Make sure the ChatGPT app is in your Applications folder and up to date, or install Codex's command-line tool and use `codex` |
| "Failed to add marketplace," "could not read Username" or "unable to get password" | Check your internet connection and that you typed `ai-automation-unlock/plugins` exactly, then try again. You don't need a GitHub account or password |
| The plugin is installed but doesn't do anything | Start a new session. In the ChatGPT app, quit with Cmd + Q and reopen it |
| It says the marketplace is "already" added | That's fine. You added it before, so go on to the install command |
| Quick Wins says Composio isn't connected | Follow Step 4, then start a new session. In the ChatGPT app, quit with Cmd + Q and reopen it |
| Quick Wins shows a Google sign-in link | Open it and sign in with the Google account that owns your Search Console, then tell it you're done |
| Quick Wins says there are no sites or no data | Check that your site is verified in Google Search Console and has had search traffic in the last 3 months |
| AI Search Check says it couldn't reach the internet | Allow it when it asks for permission. In Codex, approve the request to use the network |
| AI Search Check says the site refused the check | Some sites block automated checks. Ask it to check the page's HTML, and paste the HTML when it asks |

Questions? Ask in the AI Automation Unlock community, or email hello@aiautomationunlock.com.
