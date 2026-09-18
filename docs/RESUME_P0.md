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
  A question about publishing publicly is pending. Do not push until the human
  answers, or they restore private visibility and the private workflow applies.

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

1. Resolve the repository visibility question before publishing. The remote and
   authenticated account must be verified again immediately before pushing.
2. Prepare/update local REVIEW_PACKET.md, REVIEW_DIFF.txt and PR_BODY.md with
   frozen base/head SHAs, hashes, exact checks and limitations. Push the topic
   branch and open a draft PR once the visibility decision permits it. Link the
   P0 issue if created; no existing issue/PR was found when resuming.
3. Give Claude Desktop the packet/diff using docs/CLAUDE_OPERATOR.md. Claude has
   not reviewed this implementation; there are no findings or approvals to claim.
4. Record the returned findings and resolve them on this branch. Obtain human
   acceptance of 50K Growth Evaluation scope and the P0 gate. Do not merge or
   begin P1 before acceptance. CI is not configured (scheduled for P1).

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
