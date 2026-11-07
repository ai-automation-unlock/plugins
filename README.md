# AI Automation Unlock plugins

Plugins for Claude Code and Codex from AI Automation Unlock.

| Plugin | What it does |
|---|---|
| [Simple SEO](simple-seo/README.md) | Checks one web page's on-page SEO against a target keyword, then drafts a better title, meta description, H1 and intro for you to review |

These steps are written for a Mac. You set things up once, then install each tool with two commands. The first setup can take 15 to 30 minutes if your Mac needs Apple's developer tools.

**What you need:**

- A free GitHub account
- Claude Code with a paid Claude plan (Pro or higher), or the ChatGPT desktop app with a plan that includes Codex. You can install in one or both

## Step 1: Get access

This repository is private, so you need access before you can install anything.

1. If you don't have one yet, create a free GitHub account at https://github.com/signup.
2. Send your GitHub username to Tariehk.
3. Accept the invitation to the AI Automation Unlock organization. GitHub emails it to you, or you can open https://github.com/orgs/ai-automation-unlock/invitation while signed in. Invitations expire after 7 days, so if yours did, ask Tariehk to send a new one.

## Step 2: Let your computer sign in to GitHub

Claude Code and Codex download plugins with Git, and they can't ask you for a password while they do. So you save your GitHub sign-in once with GitHub's free `gh` tool.

1. Make sure your Mac has Git. Open the Terminal app and run:

   ```bash
   git --version
   ```

   If it prints a version number, go on to the next step. If a window asks to install the command line developer tools, click **Install** and wait until it finishes. That can take several minutes.

2. Install `gh`. Go to https://github.com/cli/cli/releases/latest. Under **Assets**, download the file whose name ends in `_macOS_universal.pkg`, open it and follow the installer. If you use Homebrew, you can run `brew install gh` instead. Then open a new Terminal window.

3. Sign in:

   ```bash
   gh auth login
   ```

   Use the arrow keys and Enter to answer its questions. Choose **GitHub.com**, **Login with a web browser** and **HTTPS**, and answer **Yes** to "Authenticate Git with your GitHub credentials?" The order of the questions depends on your version of `gh`. It then shows a one-time code. Copy it, press Enter to open your browser, paste the code and click **Authorize**. You can ignore any tip about expiring tokens.

4. Run this too. It makes sure Git uses that sign-in:

   ```bash
   gh auth setup-git
   ```

5. Check that it worked:

   ```bash
   git ls-remote https://github.com/ai-automation-unlock/plugins.git main
   ```

   You should see one line that ends in `refs/heads/main`. If you see "Repository not found," you haven't accepted the invitation yet, or `gh` is signed in to a different GitHub account. Run `gh auth status` to see which account it's using.

## Step 3: Install in Claude Code

You need Claude Code's command-line tool. To check, run `claude --version` in Terminal. If you get "command not found," install it from https://code.claude.com/docs/en/setup, then open a new Terminal window.

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

If you get "No such file or directory," update the ChatGPT app and try again. Older versions don't include Codex's command-line tool.

## Step 5: Try it

In Claude Code or Codex, ask in plain English:

```text
Check the SEO of https://example.com/your-page for the keyword "your keyword"
```

Use your own page and keyword. If it asks for permission to run `curl`, allow it. That's how it reads your page. After the audit, ask it to fix the problems it found. It gives you drafts to review. It never changes your website.

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

This removes the plugin but keeps the AI Automation Unlock store added, so you can install it again later. To remove the store too, run `claude plugin marketplace remove ai-automation-unlock` in Claude Code, or the same long Codex path followed by `plugin marketplace remove ai-automation-unlock`.

## If something goes wrong

| What you see | What to do |
|---|---|
| "Failed to add marketplace," "Repository not found," "could not read Username," "unable to get password" or "Permission denied" | Your computer can't sign in to GitHub, or you don't have access yet. Make sure you accepted the invitation in Step 1, then redo Step 2 |
| A window asks to install the command line developer tools | Click **Install**, wait until it finishes, then run the command again |
| `claude: command not found` | Install Claude Code from https://code.claude.com/docs/en/setup |
| "No such file or directory" for the long Codex path | Make sure the ChatGPT app is in your Applications folder and up to date, or install Codex's command-line tool and use `codex` |
| The plugin is installed but doesn't do anything | Start a new session. In the ChatGPT app, quit with Cmd + Q and reopen it |
| It says the marketplace is "already" added | That's fine. You added it before, so go on to the install command |
