# ADR 005: P1 evaluation-status decisions

Date: 2026-09-19. Status: **human accepted both recommendations on 2026-09-19**.
Baseline: `4740732d1ff4dfff3d0e9ebb042c08a8f6545a59`.
Ticket: Issue #3. The complete P0 baseline passed; see P1_BASELINE.md.
The human instructed "follow your recommends" for both questions. The adopted
decisions below govern P1; no candidate bytes or metadata are changed.

## 1. Candidate.3 calculations versus eligibility gate

Evidence: P0_ACCEPTANCE.md says, "Refuse a pending manifest for eligibility
calculation. Use a new reviewed manifest after human decisions." RULES_REGISTER
also says all candidates are unpromoted and must not be used for eligibility
calculations. Candidate.3 still has `review_status: pending`. Issue #3 asks P1 to
implement target/evaluation behavior from the accepted candidate.3 specification,
while the current instruction forbids modifying or relabelling its bytes.

Affected outputs: permission to evaluate, `eligible_estimate`, target/consistency
assessment results, and ruleset status/provenance in reports. Accounting formulas
and the already accepted lab fee/fractional-micro conventions are not in question.

Available interpretations:
- Preserve the promotion gate: permit candidate.3 financial diagnostics and
  individual rule calculations for synthetic regression, but withhold aggregate
  eligibility while its manifest is unpromoted. A separately reviewed manifest
  would be needed before aggregate eligibility output.
- Authorize a specifically labelled candidate.3 lab evaluation mode that may emit
  `eligible_estimate` using the accepted conventions, preserving the immutable
  pending status/hash and explicitly distinguishing this from FTMO verification.
  This needs an explicit exception to the earlier P0 promotion gate.

Recommendation: labelled candidate.3 lab evaluation mode, with immutable provenance
and unresolved official-semantics labels. It fulfills the ticket without silently
promoting a historical candidate, and the human explicitly accepted this exception on 2026-09-19.

Differing test: a fully specified flat account at session close with balance
53000, best closed-profit day 1200 and total profit 3000, no prior breach and
adequate data. The first interpretation withholds aggregate eligibility due to
manifest status; the second permits a labelled lab `eligible_estimate`.

## 2. Observed exposure above the accepted five-equivalent cap

Evidence: candidate.3 and accepted P0 fixtures establish counting weights, the
five-equivalent cap and `within_cap: false` for six minis and 51 micros. They do
not specify an aggregate-state consequence or whether excess exposure is sticky.
ADR 002 explicitly makes drawdown contact permanent, but does not extend that
permanence to exposure. The Issue #3 hygiene note prohibits fabricated FTMO
failure/review thresholds. The cap itself is accepted; its lifecycle consequence
for already recorded fills remains unspecified in this contract.

Affected outputs: aggregate `breached` versus unavailable/review-needed status,
breach persistence after reduction/flattening, and subsequent eligibility.

Available interpretations:
- An observed over-cap holding permanently breaches the lab evaluation run.
- An observed over-cap holding fails current exposure compliance, but that failure
  clears after reducing holdings; historical evidence remains.
- Record the exact holding and `within_cap: false`, retain the ledger and evidence,
  and withhold aggregate eligibility with an explicit unresolved-policy reason
  until an authoritative consequence is accepted. Do not invent permanent failure.

Recommendation: the third interpretation until a lifecycle consequence is
accepted. Do not reject or erase real recorded fills to pretend excess exposure
never occurred. No platform order routing or compliance engine is proposed.

Differing tests: six standard contracts at one event, then reduced to five and
later flat; equity never touches drawdown and all financial objectives are later
met. Permanent breach, recovery after reduction, and unresolved aggregate status
produce different results. Repeat with 51 micros and preserve the explicit
fractional-counting lab-convention label under every interpretation.

## Accepted disposition and implementation scope

1. Candidate.3 may produce explicitly labelled lab eligibility estimates, including
   `eligible_estimate`, while preserving its immutable pending metadata and hash.
   This is an explicit, candidate.3-only exception to the earlier P0 promotion gate.
   It is not official FTMO verification or general permission to load other candidates.
2. Record observed over-cap holdings, preserve financial events, and withhold
   aggregate eligibility with an explicit unresolved-policy reason until authoritative
   consequences are accepted. Reduction/flattening does not resolve that historical
   policy question. This is not a permanent drawdown breach or an FTMO disqualification.

Implement these decisions in Issue #3. Keep gross/net consistency and fractional
micro labels visible. Do not modify or relabel candidate.1/.2/.3. The human did not
change any money, drawdown, counting, or session formula. Independent P1 review and
human acceptance remain required before merge.
