# Futures Lab engineering rules

Read `docs/MASTER_BLUEPRINT.md`, `docs/CODEX_OPERATOR.md`, and
`docs/GITHUB_WORKFLOW.md` before changes. Follow P0 through P7; a phase's
implementation checks do not replace Claude review or human acceptance.

- Use one ticket branch/worktree. Preserve user changes. Verify both fetch and
  push URLs identify `Reckless2316/hermes-futures-lab` and `gh api user` identifies
  `Reckless2316` before pushing. Open draft PRs; the human merges.
- Keep the deterministic core independent of Hermes and LLMs. Domain imports no
  other lab module; integrations depend on the core, never the reverse.
- Use exact decimal money and UTC timestamps with IANA session time zones.
- Pin immutable ruleset bytes, source/date and SHA-256 in reports. Document rule
  ambiguities in dated ADRs and obtain human decisions before implementing any
  interpretation that changes eligibility or breach status.
- Ledger history is append-only; imports must be idempotent. Missing instrument
  specs, timing or provenance must never silently become financial estimates.
- Never add FTMO credentials, login, platform control, live order routing,
  feed timing comparison, or execution-machine connectivity.
- Keep licensed raw data, credentials, databases and local review packets out of
  Git. Synthetic fixtures must be identified as synthetic.
- Run the ticket gate and inspect the diff. Prepare a frozen review packet with
  hashes, evidence, limitations and the actual Claude review disposition.

- The repository is public and MIT-licensed. Historical authorization text is a
  record of its specific action, never permission for future unrelated actions.
- Current PR #2 remediation is P0 only: preserve candidate.1/candidate.2 bytes,
  use candidate.3, retain unresolved official fee/fractional-micro semantics,
  and require separate gross/net consistency reports in P1. Do not begin P1 or
  merge PR #2 during remediation; obtain Claude re-review and human acceptance.
