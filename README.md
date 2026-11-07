# AI Automation Unlock plugins

Plugins for Claude Code and Codex from AI Automation Unlock.

| Plugin | What it does |
|---|---|
| [Simple SEO](simple-seo/README.md) | Checks one web page's on-page SEO against a target keyword, then drafts a better title, meta description, H1 and intro for you to review |

These steps are written for a Mac. You set things up once (about 10 minutes), then install each tool with two commands.

## Step 1: Get access

This repository is private, so you need access before you can install anything.

1. If you don't have one yet, create a free GitHub account at https://github.com/signup.
2. Send your GitHub username to Tariehk.
3. Accept the invitation to the AI Automation Unlock organization. GitHub emails it to you, or you can open https://github.com/orgs/ai-automation-unlock/invitation while signed in.

## Step 2: Let your computer sign in to GitHub

Claude Code and Codex download plugins with Git, and they can't ask you for a password while they do. So you save your GitHub sign-in once with GitHub's free `gh` tool.

1. Install `gh` from https://cli.github.com. If you use Homebrew, you can run `brew install gh` instead.
2. Open the Terminal app and run:

   ```bash
   gh auth login
   ```

   Choose **GitHub.com**, then **HTTPS**. When it asks whether to authenticate Git with your GitHub credentials, choose **Yes**. Then sign in through your browser.

3. Run this too. It makes sure Git uses that sign-in:

   ```bash
   gh auth setup-git
   ```

4. Check that it worked:

   ```bash
   git ls-remote https://github.com/ai-automation-unlock/plugins.git main
   ```

   You should see one line that ends in `refs/heads/main`. If you see "Repository not found," you haven't accepted the invitation yet, or `gh` is signed in to a different GitHub account. Run `gh auth status` to see which account it's using.

## Step 3: Install in Claude Code

You need Claude Code's command-line tool. To check, run `claude --version` in Terminal. If you get "command not found," install it from https://code.claude.com/docs/en/setup first.

Run these two commands:

```bash
claude plugin marketplace add ai-automation-unlock/plugins
```

```bash
claude plugin install simple-seo@ai-automation-unlock
```

Then start a new Claude Code session. A session that was already open won't see the plugin. In the Claude desktop app, start a new session in the Code tab.

## Step 4: Install in Codex

Codex's command-line tool comes with the ChatGPT desktop app, so you don't need to install anything else. The commands below use its full location, which assumes the ChatGPT app is in your Applications folder. If you installed Codex's command-line tool on its own, type `codex` instead of the long path.

Run these two commands:

```bash
/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex plugin marketplace add ai-automation-unlock/plugins
```

```bash
/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex plugin add simple-seo@ai-automation-unlock
```

Then fully quit the ChatGPT app with Cmd + Q and open it again. You'll find Simple SEO in the plugins list under Customize.

## Step 5: Try it

In Claude Code or Codex, ask in plain English:

```text
Check the SEO of https://example.com/your-page for the keyword "your keyword"
```

Use your own page and keyword. After the audit, ask it to fix the problems it found. It gives you drafts to review. It never changes your website.

In Claude Code, you can also run a skill by name with `/simple-seo:page-audit` or `/simple-seo:page-fix`.

## Get updates

When Tariehk releases a new version, run these.

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

## If something goes wrong

| What you see | What to do |
|---|---|
| "Repository not found," "Authentication failed" or a request for a username | Redo Step 2. Make sure you accepted the invitation in Step 1 |
| `claude: command not found` | Install Claude Code from https://code.claude.com/docs/en/setup |
| "No such file or directory" for the long Codex path | Make sure the ChatGPT app is in your Applications folder, or install Codex's command-line tool and use `codex` |
| The plugin is installed but doesn't do anything | Start a new session. In the ChatGPT app, quit with Cmd + Q and reopen it |
| "Already exists" when you add the marketplace | You added it before, so skip to the install command |
