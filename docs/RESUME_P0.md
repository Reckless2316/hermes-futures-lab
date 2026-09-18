# P0 handoff and resume state

Updated 2026-09-18 after resuming checkpoint `checkpoint/p0-2026-09-17`.
**P0 local implementation checks passed; phase acceptance remains pending.**
The original checkpoint and portable bundle remain unchanged.

## Location

- Repository: `/home/reckless/projects/hermes-futures-lab`.
- Worktree: `/home/reckless/projects/hermes-futures-lab/.worktrees/p0-specification`.
- Branch: `feat/p0-specification`; base planning commit: `22abff4`.
- Origin: `https://github.com/Reckless2316/hermes-futures-lab.git`.
- GitHub account verified as `Reckless2316` on 2026-09-18.
- GitHub now reports **public**, changed from private at the original checkpoint.
  The human explicitly approved pushing the branch and opening its draft PR
  publicly on 2026-09-18. Do not ask for that authorization again.
- P0 tracking issue: https://github.com/Reckless2316/hermes-futures-lab/issues/1.
  The local REVIEW_PACKET.md records the draft PR URL and frozen head SHA.

```bash
cd /home/reckless/projects/hermes-futures-lab/.worktrees/p0-specification
git status --short
cat docs/RESUME_P0.md
```

## Completed work

Read MASTER_BLUEPRINT, GITHUB_WORKFLOW, CODEX_OPERATOR and INSTALL_CHECKLIST.
Follow P0's separate acceptance gate before implementing P1. No external skills
or subagents were used. Other repositories and execution systems are untouched.

- Package/CLI skeleton, locked development dependencies, data contract, threat
  model, rules register, ADRs and P0 acceptance record are prepared for review.
- Historical candidate.1 is byte-identical to the checkpoint. Candidate.2 records
  the **already accepted** ADR 003 lab convention: realized gross P&L minus all
  fees posted in the session, including entry fees for positions still open.
  Do not ask the human to decide that convention again.
- Schema, 43 reference cases, 13-event synthetic trace and 8 artifact hashes are
  synchronized. Both candidates await independent review; neither is a promoted
  ruleset. Official source observation remains 2026-09-17.
- Fifteen contract/CLI tests passed, with zero skipped. They check fixture
  contracts and references; they do not prove financial engine outcomes.
- Offline locked installation, source/wheel build and isolated installed-wheel
  smoke checks passed. See P0_VALIDATION.md for commands and limitations.

Use `--cache-dir /tmp/futures-lab-uv-cache` for uv commands in this environment;
its normal home cache is outside writable roots. The CLI has zero runtime
dependencies. The `.venv`, build outputs and caches are ignored and disposable.

## Remaining handoff

1. Give Claude Desktop the frozen REVIEW_PACKET.md and REVIEW_DIFF.txt using
   docs/CLAUDE_OPERATOR.md. The public draft PR is also available via
   `gh pr view feat/p0-specification --repo Reckless2316/hermes-futures-lab`.
   Claude has not reviewed this implementation; no findings or approvals exist.
2. Record returned findings and resolve them on this branch. Update the packet
   and draft PR to the new head after any fixes, then request independent review.
3. Obtain human acceptance of 50K Growth Evaluation scope and the P0 gate. Do not
   merge or begin P1 before acceptance. CI is not configured (scheduled for P1).

The current review packet, when present, is a local gitignored handoff artifact;
it records the exact frozen head and publication status. No secrets, real account
records or licensed market data belong in it.

No ledger, financial evaluator, importer, database, network API, plugin or coach
exists. There is no migration. The CLI reports implementation status and hashes
explicitly selected local files. The trace checker validates only the authored
P0 subset; production event processing remains P1 work.

## Suggested next-session instruction

> Read docs/RESUME_P0.md and the local REVIEW_PACKET.md in the P0 worktree.
> Continue the publication/review handoff on feat/p0-specification, respecting
> the recorded visibility decision and already accepted ADR 003 convention.
> Verify origin and account before pushing. Do not bypass P0 acceptance.
