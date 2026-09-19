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

P0 issue: [#1](https://github.com/Reckless2316/hermes-futures-lab/issues/1).
Draft PR: [#2](https://github.com/Reckless2316/hermes-futures-lab/pull/2).
Branch: `feat/p0-specification`; worktree:
`/home/reckless/projects/hermes-futures-lab/.worktrees/p0-specification`.
Claude gate: **FAIL pending remediation**, accepted by the human. The current
request authorizes remediation, commit/push to this existing branch and re-review
handoff. It explicitly prohibits P1 implementation and merging PR #2.

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
paths and commit. Push the existing topic branch with `git push origin
feat/p0-specification`. Keep PR #2 draft. Prepare its exact multiline body in the
ignored `PR_BODY.md` and use `gh pr edit 2 --body-file PR_BODY.md`. New authorized
tickets use draft PRs; do not create a duplicate PR for remediation.

## Frozen review handoff

Record full base/head SHAs, candidate/fixture hashes, exact validation commands,
results, limitations and the actual review disposition. For this remediation,
use `3ee851b81912697ea53bed4db4b4b965fb0229bf` as the diff base. The original
planning base remains `22abff4a8760b17ee838ec95f51e83f13f9f0631`.

Claude should inspect the remediation diff and affected downstream artifacts.
A full 4,379-line reread is unnecessary unless foundational P0 assumptions change.
Provide the public PR plus REVIEW_PACKET.md and REVIEW_DIFF.txt; when Desktop
cannot receive them directly, give the human a ready-to-paste handoff. Never
claim a handoff was delivered or review passed without evidence. Record actual
returned findings and fix them on the same branch before another re-review.

## Acceptance, storage and future gates

The human owns merge decisions. Do not merge PR #2 or start P1 during this
remediation. After a separately accepted merge, sync the WSL and Windows clones
through GitHub, preserving local changes. Deploy only a reviewed accepted build
at the appropriate phase; a pushed draft is not deployment approval.

Store only code, docs, synthetic fixtures and sanitized evidence in Git. Keep
raw data, secrets, `.env`, databases and local review packets ignored. Ignore
rules do not remove existing history; inspect staged files before every public
push. MIT covers project-owned code/docs, not third-party sources or market data.

CI and automated security checks are scheduled for P1, not configured in P0.
Require passing checks and reviews when introduced; never infer CI success from
local tests. Preserve other repositories, especially the upstream-pointed
`tonbistudio` template checkouts, and the separation from execution systems.
