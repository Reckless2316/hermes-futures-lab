# P0 remediation handoff and resume state

Updated 2026-09-18. Claude PR #2 review gate: **FAIL pending remediation**,
accepted by the human. Remediation is prepared for re-review; no new Claude
verdict exists. P0 phase acceptance remains pending. Do not implement P1 or merge.

## Location and review target

- Worktree: `/home/reckless/projects/hermes-futures-lab/.worktrees/p0-specification`.
- Branch: `feat/p0-specification`; original planning base: `22abff4`.
- Remediation base: `3ee851b81912697ea53bed4db4b4b965fb0229bf`.
- Repository: https://github.com/Reckless2316/hermes-futures-lab (PUBLIC).
- Issue: https://github.com/Reckless2316/hermes-futures-lab/issues/1.
- Draft PR: https://github.com/Reckless2316/hermes-futures-lab/pull/2.
- REVIEW_PACKET.md records the frozen final head, hashes and publication status.

The human authorized this remediation, commit/push to the existing branch and
re-review handoff. Historical publication approval is only a record of that past
action and never permission for future unrelated actions. Fetch/push URLs and
the authenticated GitHub account were verified on 2026-09-18 before remediation.

## Decisions and changes

- Candidate.1 and candidate.2 remain byte-identical. Candidate.3 encodes the full
  drawdown basis, empty-history behavior, explicit counting classes, both required
  consistency reports and unresolved official-semantics labels. Source observation
  remains 2026-09-17. No candidate is promoted or accepted for evaluation.
- Standard = 1.0, mini = 1.0, micro = 0.1. Fractional micro summation remains a
  lab convention pending FTMO confirmation, visibly unresolved in artifacts.
- P1 must report gross AND net-of-fees consistency shares separately. Net remains
  the accepted ADR 003 lab convention pending official verification; no silent
  substitution. Do not ask the human to re-decide the accepted lab fee convention.
- V3 fixtures contain 51 proposed reference cases and the 13-event synthetic trace.
  Nine artifact hashes bind all manifests, schemas, fixtures and recipe.
- Python 3.11.16 and uv 0.12.17 are pinned for validation; pytest is a locked dev
  dependency, with deterministic test discovery and development-helper imports.
  README/P0_VALIDATION document `uv sync --locked` and both runners.
- Public-repository documentation is reconciled. The human selected MIT licensing;
  LICENSE is included in source and wheel metadata. External materials retain
  their own terms. See ADR 004 for the complete decision record.

## Remaining review and acceptance

Give Claude Desktop REVIEW_PACKET.md and REVIEW_DIFF.txt (remediation base to new
head), the public PR and affected downstream artifacts per CLAUDE_OPERATOR.md.
The human requests a focused re-review; a full original 4,379-line reread is
unnecessary unless foundational P0 assumptions change. No direct Claude Desktop
connector is available in this session; the prepared packet requires human relay.
Do not claim it was delivered or independently accepted without evidence.

Record returned findings on this same branch, then seek human P0 scope/gate
acceptance. Outstanding official interpretations: consistency fee basis/day
assignment and fractional micro counting. Session endpoints/assessment ordering,
real calendars/coverage and account-specific terms also need reconciliation.
No PASS, merge or P1 authorization is implied by successful local checks.

The original checkpoint and bundle remain unchanged. No ledger, evaluator,
importer, database, network API, plugin, coach or execution connection exists.
P0 checks validate contracts and authored reference data, not financial outcomes.
CI remains unconfigured until P1. Use a writable cache such as
`UV_CACHE_DIR=/tmp/futures-lab-uv-cache` in this environment.
