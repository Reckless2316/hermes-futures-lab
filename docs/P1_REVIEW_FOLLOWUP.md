# P1 focused follow-up: MED-P1-1

Reviewed HEAD: `52606daadcfe662161623e02612973ce32494dc7` (PR #4).
Claude disposition, reported by the human: **PASS WITH REQUIRED FOLLOW-UP**;
0 Critical, 0 High, 0 blocking fixes before merge. The human requested MED-P1-1
before P1 acceptance/merge. The human subsequently accepted remediation HEAD
`fe7c1ba1b263ad6b0b897997116cd7bb982537ca` and authorized the final merge gate
and merge. See P1_ACCEPTANCE.md; no separate focused Claude disposition is invented.

## Change

Whenever gross and net-of-fees consistency disagree on `satisfied`, append
`consistency_basis_divergence` to `data_quality_reasons`. Append it after state
selection: it is an explanation of interpretation dependence, not corrupted
data, an eligibility blocker, a new breach or an official FTMO determination.
Both consistency reports, their arithmetic and lab-convention labels remain intact.
Existing net-based aggregate state, drawdown precedence and unavailable-data
behavior remain unchanged. No candidate/schema, GUI or replay changes are included.

## Reachable regression cases

Both tests construct recorded fills and commissions using the existing `multi_day`
helper, then evaluate them through the engine. They do not inject calculated reports.

| Case | Gross daily profits | Posted daily fees | Balance | Gross share | Net share | Existing aggregate state |
| --- | --- | --- | --- | --- | --- | --- |
| Gross satisfies, net does not | 1300, 1000, 1000 | 0, 70, 70 | 53160.00 | 13/33; true | 65/158; false | `not_yet_eligible` |
| Gross does not satisfy, net does | 1400, 1000, 1000 | 200, 0, 0 | 53200.00 | 7/17; false | 3/8; true | `eligible_estimate` |

Both meet the target. The inverse is reachable because fees concentrated on the
largest-profit day can reduce that day's share of total profit. Nonnegative fees
do not imply that the best-day ratio always increases.

Tests assert both views, exact ratios, target met, preserved state, the explicit
reason, no drawdown breach/evidence, no quarantine/valuation gaps and no official
account certification. The existing equal-view eligible case asserts no reason.
Both new tests failed on the reviewed implementation solely because the reason
was absent, before applying the fix.

Run the complete gate in P1_VALIDATION.md. The PR and frozen focused review packet
record the new HEAD, final runner counts, immutable candidate hashes, build/smoke,
security and CI results. Review the remediation diff from the reviewed HEAD plus
the affected report documentation/tests; no full P1 reread is implied.

## Deferred follow-up

Candidate.4 work remains separate: structural/versionable manifest schema,
structured drawdown semantics, removal of expression-string semantics, explicit
cadence/coverage, normalized decimal validation, identity hashing versus structural
validation, loader assertions of implemented semantics, exposure display precision
for future weights, and unavailable-result implementation identity. None is
implemented or treated as resolved by MED-P1-1. Existing official fee/day-assignment,
fractional-micro and exposure-consequence uncertainties remain visibly unresolved.
