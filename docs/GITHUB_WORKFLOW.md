# GitHub workflow for the Futures Training Lab

Repository: [Reckless2316/hermes-futures-lab](https://github.com/Reckless2316/hermes-futures-lab).
Visibility: **PUBLIC**, verified through GitHub on 2026-09-18. License: [MIT](../LICENSE),
selected by the human during PR #2 remediation. The repository and WSL checkout
already exist; the original private-repository setup proposal is historical and
must not be run again. The Windows clone/deployment is a separate later concern.

GitHub is the shared source for code, docs, issues, PRs and test evidence, never
account credentials, live databases or licensed raw data. Public source can be
read by anyone. A past publication decision records only its specific action;
it is not authorization for future unrelated pushes, messages, visibility changes,
deployments or merges. Follow the current task's authorized scope.

## Operators and current ticket

| Operator | Location and responsibility |
| --- | --- |
| Codex | WSL repository; implement/test on a ticket branch and worktree; prepare draft PR and frozen review evidence |
| Claude Desktop | Read-only independent review of the supplied diff, affected contracts and evidence |
| Hermes Desktop | Separate Windows clone of an accepted build; product/ticket coordination |
| Human | Material rule interpretation, scope acceptance and final merge decision |

Current ticket: [#3](https://github.com/Reckless2316/hermes-futures-lab/issues/3),
P1 deterministic ledger and Growth rule engine. Branch:
`feat/p1-deterministic-engine`; worktree:
`/home/reckless/projects/hermes-futures-lab/.worktrees/p1-deterministic-engine`.
P0 issue #1 / PR #2 are complete and merged at
`4740732d1ff4dfff3d0e9ebb042c08a8f6545a59`, the verified P1 starting point.
Claude P0 remediation re-review PASS and human acceptance on 2026-09-19 remain
historical P0 evidence; they do not accept P1. ADR 005 records the human's two
P1 evaluation-status decisions. The current task authorizes P1 implementation,
commits, push and a draft PR, with independent review and human acceptance pending.

## Work and publish within the ticket scope

Inspect status and preserve existing changes. Read AGENTS.md and the current
handoff. Reuse this ticket's worktree. For a new authorized ticket, create its
own branch/worktree from the accepted base under the WSL home filesystem.
Before pushing, verify fetch and push URLs and the authenticated account:

```bash
git status --short
git remote -v
gh api user --jq .login
```

Both URLs must identify `Reckless2316/hermes-futures-lab`; the login must be
`Reckless2316` (case-insensitive). Stop on a mismatch. Never embed credentials
in URLs, shell commands, packets or Git. Do not alter existing template remotes.

Run the phase's documented validation, inspect the diff, stage specific reviewed
paths and commit. Push this topic with `git push origin feat/p1-deterministic-engine`.
Prepare the exact multiline body in ignored `PR_BODY.md`, then create a **draft**
PR against main using `gh pr create --draft --base main --head
feat/p1-deterministic-engine --body-file PR_BODY.md` plus a descriptive title.
Do not merge. Freeze P1 review evidence over the full range from
`4740732d1ff4dfff3d0e9ebb042c08a8f6545a59` to the implementation HEAD. New P1
code and affected downstream contracts need independent review; the old focused
P0 remediation scope does not limit review of this new implementation.

## Historical remediation review handoff (completed)

Record full base/head SHAs, candidate/fixture hashes, exact validation commands,
results, limitations and the actual review disposition. For this remediation,
use `3ee851b81912697ea53bed4db4b4b965fb0229bf` as the diff base. The original
planning base remains `22abff4a8760b17ee838ec95f51e83f13f9f0631`.

Claude reviewed the remediation diff and affected downstream artifacts and
returned PASS, reported by the human on 2026-09-19. The handoff scope was:
A full 4,379-line reread is unnecessary unless foundational P0 assumptions change.
Provide the public PR plus REVIEW_PACKET.md and REVIEW_DIFF.txt; when Desktop
cannot receive them directly, give the human a ready-to-paste handoff. Never
claim a handoff was delivered or review passed without evidence. Record actual
returned findings and fix them on the same branch before another re-review.

## Acceptance, storage and future gates

The human owns merge decisions. Do not merge the P1 PR. After a separately
accepted merge, sync the WSL and Windows clones
through GitHub, preserving local changes. Deploy only a reviewed accepted build
at the appropriate phase; a pushed draft is not deployment approval.

Store only code, docs, synthetic fixtures and sanitized evidence in Git. Keep
raw data, secrets, `.env`, databases and local review packets ignored. Ignore
rules do not remove existing history; inspect staged files before every public
push. MIT covers project-owned code/docs, not third-party sources or market data.

P1 introduces `.github/workflows/validation.yml` and documented security checks.
Require passing checks and reviews when introduced; never infer CI success from
local tests. Preserve other repositories, especially the upstream-pointed
`tonbistudio` template checkouts, and the separation from execution systems.
