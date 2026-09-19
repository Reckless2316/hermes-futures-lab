# P0 remediation handoff and resume state

Updated 2026-09-19. **P0 accepted:** Claude focused remediation re-review returned
**PASS** and the human accepted P0 scope on 2026-09-19, for implementation HEAD
`2384d549424f3897438059bc84796b65401116b0`. The human supplied this review
disposition. This documentation/status update does not authorize P1 or merge.

## Location and review target

- Worktree: `/home/reckless/projects/hermes-futures-lab/.worktrees/p0-specification`.
- Branch: `feat/p0-specification`; original planning base: `22abff4`.
- Remediation base: `3ee851b81912697ea53bed4db4b4b965fb0229bf`.
- Repository: https://github.com/Reckless2316/hermes-futures-lab (PUBLIC).
- Issue: https://github.com/Reckless2316/hermes-futures-lab/issues/1.
- PR: https://github.com/Reckless2316/hermes-futures-lab/pull/2.
- REVIEW_PACKET.md preserves the historical remediation handoff;
  P0_ACCEPTANCE.md records the final PASS, human acceptance and P1 requirements.

The human authorized recording final P0 acceptance, complete validation, and
commit/push of this documentation-only update to the existing branch. Historical
publication approval is only a record of that past action and never permission for future unrelated actions. Fetch/push URLs and
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

## Accepted gate and P1 handoff requirements

P0_ACCEPTANCE.md is the acceptance record for the reviewed implementation HEAD.
Claude's two non-blocking Medium findings are mandatory P1 requirements:

- Do not treat the drawdown basis expression-string as executable semantics;
  candidate.3's explicit formula is authoritative.
- Candidate.3 `contract_counting` is authoritative; legacy
  `max_contracts_mini_equivalent` must not become a competing implementation rule.

The accepted P0 gate does not resolve official consistency fee basis/day
assignment or fractional micro counting. Session endpoints/assessment ordering,
real calendars/coverage and account-specific terms also need reconciliation.
All three candidate files remain immutable and unpromoted. No P1 implementation
or merge is authorized by this status update.

The original checkpoint and bundle remain unchanged. No ledger, evaluator,
importer, database, network API, plugin, coach or execution connection exists.
P0 checks validate contracts and authored reference data, not financial outcomes.
CI remains unconfigured until P1. Use a writable cache such as
`UV_CACHE_DIR=/tmp/futures-lab-uv-cache` in this environment.
