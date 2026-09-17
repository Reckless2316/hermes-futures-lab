# GitHub workflow for the Futures Training Lab

**Account:** [github.com/reckless2316](https://github.com/reckless2316). **Proposed new repository:** `reckless2316/hermes-futures-lab`, private by default. This is a proposed name; confirm it is available in your signed-in GitHub account before creating it.

## 1. What I found, and what GitHub will do

The public `reckless2316` profile currently shows 12 public repositories, all forks. Two relevant examples are the [`hermes-multi-agent-workflow` fork](https://github.com/reckless2316/hermes-multi-agent-workflow) and [`model-trader` fork](https://github.com/reckless2316/model-trader). The latter describes a Hyperliquid paper-trading framework, so it should not become the Futures Lab core by accident. Private repositories are not visible in this public inspection. The local WSL checkouts of `hermes-multi-agent-workflow` still have `https://github.com/tonbistudio/hermes-multi-agent-workflow.git` as `origin`, even though your fork exists. No local Futures Lab repository was found in the checked project directories.

For this project, GitHub is the **shared source of truth for code, documentation, issues, branches, pull requests, and test results**. It is not the live database, market-data store, FTMO account, or secrets vault. The intended flow is:

```text
Your GitHub account: reckless2316/hermes-futures-lab
    │
    ├── WSL clone: Codex writes/tests on ticket branches and worktrees
    ├── Windows clone: Hermes Desktop runs a reviewed lab build
    └── Pull request: Claude reviews the frozen diff; you accept the merge
```

`origin` is simply the local name for the GitHub URL a checkout pushes to. It does **not** automatically become your account because you own a fork. Verify it in every checkout with `git remote -v`.

## 2. One-time WSL setup

Run these in **Ubuntu WSL**. `gh` (GitHub CLI) was absent when checked, while Git was present. Install `gh` using GitHub’s current [official Linux instructions](https://github.com/cli/cli/blob/trunk/docs/install_linux.md). On Ubuntu, that page gives the maintained apt repository setup. Then:

```bash
gh --version
gh auth login --hostname github.com --web --git-protocol https
gh auth status
gh api user --jq .login
gh auth setup-git
```

The login should print `reckless2316` (GitHub capitalization may differ). Stop before creating or pushing a repo if another account appears. The browser login is GitHub CLI’s [documented default flow](https://cli.github.com/manual/gh_auth_login); `gh auth setup-git` configures Git to use that login as its credential helper. Never paste the AgentWikis bearer token or an FTMO credential into GitHub authentication. [GitHub CLI authentication reference](https://cli.github.com/manual/gh_auth_setup-git).

You will set your commit identity inside the new repository after creating its local directory. Choose the email shown in your GitHub **Settings → Emails** page, or your GitHub-provided `noreply` address. Do not invent an email; GitHub [documents commit email configuration](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address).

## 3. Create your own Futures Lab repository

**Recommended path:** start with the local blueprint files, make a clean first commit, then create a **private** GitHub repository under your account. Run in WSL:

```bash
mkdir -p /home/reckless/projects/hermes-futures-lab/docs
cd /home/reckless/projects/hermes-futures-lab
git init -b main
cp /mnt/c/Users/lucky/Documents/Codex/2026-09-17/referenced-chatgpt-conversation-this-is-an/outputs/*.md docs/
```

If that local path already exists, inspect its `git status` and remotes first. Do not initialize over unrelated work. Set the identity while inside this new repository:

```bash
git config user.name "Reckless2316"
git config user.email "YOUR_VERIFIED_OR_NOREPLY_GITHUB_EMAIL"
git config user.name
git config user.email
```

Replace the email placeholder with your actual GitHub address before running that line. This setting applies only to this repository. Create `.gitignore` **before** adding files by running this in the repository root:

```bash
cat > .gitignore <<'EOF'
.venv/
__pycache__/
.pytest_cache/
.env
.env.*
local_data/
*.db
*.sqlite
*.sqlite-*
REVIEW_PACKET.md
REVIEW_DIFF.txt
PR_BODY.md
EOF
```

Then make the first commit and create the GitHub repository:

```bash
git add docs .gitignore
git diff --cached --check
git diff --cached --stat
git commit -m "docs: add Futures Lab blueprint"
gh repo create reckless2316/hermes-futures-lab --private --source=. --remote=origin --push
git remote -v
gh repo view reckless2316/hermes-futures-lab --web
```

GitHub CLI documents `--source`, `--remote`, and `--push` for creating a repository from an existing local one. [Official `gh repo create` reference](https://cli.github.com/manual/gh_repo_create). Confirm that the browser page shows **Private** and that `origin` is `https://github.com/reckless2316/hermes-futures-lab.git` or the equivalent authenticated SSH URL.

**Web alternative:** sign in as `reckless2316`, go to GitHub’s **New repository** page, choose owner `reckless2316`, name `hermes-futures-lab`, select **Private**, and leave README, `.gitignore`, and license unchecked because the local repo already has its first commit. Then from WSL:

```bash
cd /home/reckless/projects/hermes-futures-lab
git remote add origin https://github.com/reckless2316/hermes-futures-lab.git
git push -u origin main
git remote -v
```

Use **one** creation path. If `origin` already exists, inspect `git remote -v` before changing it. GitHub documents both [web repository creation](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository) and [adding locally hosted code](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).

## 4. Point each operator to that repository

| Operator | Where it works | GitHub role |
|---|---|---|
| **Codex CLI** | `/home/reckless/projects/hermes-futures-lab` in WSL; separate worktree per ticket | Commits and pushes a topic branch to `origin`; opens a draft pull request; attaches test/review packet. |
| **Hermes Desktop** | A **separate Windows clone** of the same repo on the lab machine | Reads merged `main` for the cockpit and tracks issue/PR status. It does not write financial calculations or silently deploy a draft branch. |
| **Claude Desktop** | Review chat/Project, no shared writable checkout required | Reviews the PR URL and diff if accessible; otherwise receives `REVIEW_DIFF.txt` and packet as text. Returns findings to the ticket/PR handoff. |
| **You** | GitHub web UI | Owns repository visibility, issues, permissions, and the final merge decision. |

For the Windows clone, use Windows Git and authenticate to the **same** `reckless2316` account using its browser-backed credential flow. Keep it separate from the WSL working tree:

```powershell
cd C:\Users\lucky\Documents\Codex
git clone https://github.com/reckless2316/hermes-futures-lab.git hermes-futures-lab
cd .\hermes-futures-lab
git remote -v
git status --short
```

Do this after the GitHub repo exists. This Windows clone is a staging checkout for the reviewed Hermes build. At P5, install the lab backend in a dedicated Windows virtual environment from a reviewed commit and keep runtime data outside Git. The WSL and Windows checkouts exchange code **through GitHub**, not by editing each other’s files. If a private clone cannot authenticate, follow GitHub’s [cloning guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) and confirm the account in the credential prompt; do not embed a token in the URL.

## 5. The everyday change cycle

GitHub’s [pull request workflow](https://docs.github.com/en/pull-requests/get-started/pull-request-quickstart) is the record of each change. One Hermes ticket becomes one Codex branch/worktree and one PR.

**Start a ticket in WSL:**

```bash
cd /home/reckless/projects/hermes-futures-lab
git switch main
git pull --ff-only origin main
mkdir -p ../hermes-futures-lab-worktrees
git worktree add ../hermes-futures-lab-worktrees/p1-growth-rules -b feat/p1-growth-rules main
cd ../hermes-futures-lab-worktrees/p1-growth-rules
git status --short
```

Codex edits this worktree, runs the ticket tests, and checks the diff. Then:

```bash
git add <reviewed-files>
git diff --cached --check
git diff --cached
git commit -m "feat: implement 50K Growth rules"
git push -u origin feat/p1-growth-rules
gh pr create --draft --base main --head feat/p1-growth-rules --title "P1: 50K Growth rules" --body-file PR_BODY.md
```

Replace `<reviewed-files>` with the specific files Codex changed; do not type the angle brackets. Inspect `git diff --cached` before committing so that local data and credentials stay out of the PR.

`PR_BODY.md` is a local, gitignored file Codex prepares with the ticket objective, test commands/results, ruleset hash, known limits, and Claude review status. The [GitHub CLI PR reference](https://cli.github.com/manual/gh_pr_create) supports draft PRs and `--body-file`. If `gh` is unavailable, open the pushed branch on GitHub and use **Compare & pull request**.

**Review and revise:** Codex gives Claude the PR URL, base/head SHA, `REVIEW_PACKET.md`, and this text diff if Claude cannot access the private repository:

```bash
git fetch origin main
git diff origin/main...HEAD > REVIEW_DIFF.txt
```

Claude reports findings. Codex fixes them **on the same topic branch**, reruns tests, commits, and `git push`es. The PR updates automatically. Claude reviews the new head. Record the disposition in the PR body or ticket. Avoid committing raw data, secrets, or oversized review packets.

**Accept and sync:** after CI and Claude’s gate pass, you merge the PR in GitHub’s web UI. A squash merge keeps `main` readable. Then update the two clones separately:

```bash
# WSL coding clone
cd /home/reckless/projects/hermes-futures-lab
git switch main
git pull --ff-only origin main
```

```powershell
# Windows Hermes clone
cd C:\Users\lucky\Documents\Codex\hermes-futures-lab
git switch main
git pull --ff-only origin main
```

Use the Windows `main` checkout for a released cockpit; test its installed package before switching the running Hermes plugin. Do not deploy an unreviewed branch merely because it was pushed.

## 6. GitHub settings and boundaries

- Use **Issues** for the phase tickets; link each PR to its issue. The master blueprint remains the product specification, while Issues track current work.
- Add CI through GitHub Actions once P1 has tests. After checks exist, use **Settings → Rules → Rulesets** or branch protection for `main` to require a PR and passing checks if the account/repo plan presents those options. GitHub documents [rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository) and [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches). Claude’s chat review is an external review step; do not pretend it is a GitHub account approval.
- Store only code, docs, synthetic fixtures, small sanitized review artifacts, and CI settings. Keep FTMO credentials, account records, AgentWikis tokens, paid/raw market data, `.env`, databases, and virtual environments out of Git. `.gitignore` prevents new untracked files from being added but does not erase anything already committed. [GitHub `.gitignore` guide](https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files).
- A **private** repo is the sensible starting choice while the lab is being designed. You can decide on public release after license, data, secret, and compliance review.

## 7. Existing forks: do not change their remotes blindly

Your public `reckless2316/hermes-multi-agent-workflow` is a fork of `tonbistudio/hermes-multi-agent-workflow`. The inspected WSL checkouts point directly to `tonbistudio` as `origin` and contain uncommitted files. They are **not** the new Futures Lab repo. Preserve those changes.

If you later want one of those existing checkouts to push to your own fork, first run `git status --short`, `git branch -vv`, and `git remote -v`. After confirming the matching fork URL, a conventional remote layout is:

```bash
git remote rename origin upstream
git remote add origin https://github.com/reckless2316/hermes-multi-agent-workflow.git
git remote -v
git fetch origin
git branch -vv
```

That changes **where future pushes go**; it does not commit or discard local work. Inspect branch divergence before pushing. Repeat only for a repository whose matching fork actually belongs to `reckless2316`. Do not mass-rewrite all remotes or mix the Hyperliquid `model-trader` fork into the Futures Lab.

## 8. Quick command map

| Goal | Command in the correct checkout |
|---|---|
| See local changes | `git status --short` |
| See connected GitHub URL | `git remote -v` |
| Get accepted work | `git switch main && git pull --ff-only origin main` |
| See your branch | `git branch --show-current` |
| Send commits to GitHub | `git push -u origin <branch>` the first time; then `git push` |
| Open PR in browser | `gh pr create --web` or use the GitHub **Compare & pull request** button |
| See PR status | `gh pr status` or the repository’s Pull requests tab |
| Check authenticated account | `gh api user --jq .login` |

**First action:** authenticate `gh` in WSL and confirm it reports `reckless2316`. Then create the new private Futures Lab repository from the reviewed blueprint files. Keep the two existing template checkouts untouched until their uncommitted work is assessed.
