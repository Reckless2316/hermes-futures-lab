# P1 acceptance and merge authorization

The human accepted the P1 implementation at exact HEAD
`fe7c1ba1b263ad6b0b897997116cd7bb982537ca` and explicitly authorized the final
status-documentation update, merge gate, conversion of PR #4 from draft, merge
into main and closure of Issue #3. This record does not authorize candidate.4,
GUI implementation, deployment or another phase.

## Review and remediation evidence

- P0 base: `4740732d1ff4dfff3d0e9ebb042c08a8f6545a59`.
- Claude's independent P1 review at `52606daadcfe662161623e02612973ce32494dc7`:
  **PASS WITH REQUIRED FOLLOW-UP**, as reported by the human; 0 Critical,
  0 High and 0 blocking fixes before merge.
- Required MED-P1-1 follow-up: implemented at the accepted HEAD above. Gross/net
  satisfaction disagreement now exposes `consistency_basis_divergence` without
  changing arithmetic, aggregate state, drawdown or any FTMO interpretation.
- Both reachable divergence directions have end-to-end regressions. The accepted
  implementation passed 61 unittest tests and 61 pytest tests / 137 subtests,
  with zero skips, artifact/static/security/build/isolated-wheel checks and CI.
- The human's subsequent instruction accepts this exact implementation and
  authorizes merge after the final gate. No separate focused Claude PASS or
  GitHub account review is asserted where none was supplied in this session.

The accompanying status commit changes documentation only. Its candidate, source,
tests, schemas, dependencies and workflow bytes must match the accepted HEAD.
The final PR evidence records that documentation HEAD and its gate results; the
GitHub merge record identifies the resulting merge commit without a self-referential
commit hash in this file.

## Scope and remaining interpretations

P1 is the deterministic ledger and Growth lab engine described in P1_DESIGN.md.
Human acceptance does not promote candidate.3's immutable pending metadata or
make its lab estimates official FTMO determinations. Gross/net fee semantics,
fractional micros, exposure consequences and coverage limitations remain explicit.
The CLI's embedded acceptance label belongs to the frozen implementation; this
document records the subsequent human milestone without changing executable code.

Candidate.4 follow-up remains separate, as listed in P1_REVIEW_FOLLOWUP.md. GUI
planning is separate from this merge and no GUI implementation is included.
Future work requires its own accepted ticket, branch and review/acceptance gate.

All candidate SHA-256 values remain historical evidence:

```text
candidate.1 c835db6b7f455c7df4a246827ab77653f94a0dc4af92c25ec20634fd826ea750
candidate.2 2da332b5627dee4585555e7af9cc375d8b1ab65107dba54b4c17d538b71179eb
candidate.3 a1dcf3f3ac04abb7c5334bd6e65e9374fc36d67c3422a4b590c3ed3ae8eeeda6
```
