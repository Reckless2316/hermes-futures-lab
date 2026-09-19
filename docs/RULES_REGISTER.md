# Rules register

Observed 2026-09-17 by Codex. **P0 accepted 2026-09-19:** Claude focused re-review
PASS and human scope acceptance at `2384d549424f3897438059bc84796b65401116b0`,
as reported by the human. See P0_ACCEPTANCE.md for the two non-blocking Medium
findings recorded as mandatory P1 requirements.
Scope: FTMO Futures **Growth / Evaluation / 50K**, USD. Pro, CFD and Sim-Funded
are separate products/stages and are not supported by this candidate.

## Source evidence

| Source | Retrieved | Relevant sections | Evidence retained |
| --- | --- | --- | --- |
| [Trading Objectives & Rules](https://ftmo.com/en/futures/trading-objectives-and-rules/) | 2026-09-17 | Evaluation; Profit Target; Max Drawdown EOD Trailing; Consistency; Max Contracts | Paraphrased observations and numeric vectors below; no full-page archive |
| [Comparison table](https://ftmo.com/en/futures/comparison-table/) | 2026-09-17 | Growth Evaluation 50K and Every account | Numeric cross-check and no minimum trading days |

Both pages also contain other sizes/stages; page-wide text matching must not
combine their settings. `verified_on` records source observation, not independent
review or a legal effective date. The source does not establish an effective
timestamp, so `effective_at_utc` is null. No account terms were available.

The observed 50K values are initial capital 50000, target 3000, trailing amount
2000, contract cap 5 mini equivalents, 10 micros per mini, consistency 40%, no
Evaluation daily loss limit, and no minimum trading days. Assessment is after
the trading day, with positions closed. Session time is 18:00 to next-day 16:10
America/New_York. Exact floor contact breaches; consistency excess delays
eligibility. See ADR 002 for the proposed boundary contract.

## Candidate and version policy

Active file: `rules/ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.3.yaml`.
ID: `ftmo-futures-growth-evaluation-50k`.
Version: `2026-09-18-candidate.3`. Supersedes: `2026-09-18-candidate.2`.
Immutable manifest `review_status`: pending (unchanged). P0 specification review
and scope acceptance are complete; this does not promote an evaluation manifest.
Created 2026-09-18 for ADR 004 remediation decisions;
source observation remains 2026-09-17, not a new source verification.

Historical candidate.1 (`rules/ftmo_futures_growth_evaluation_50k_2026-09-17.yaml`)
and candidate.2 (`rules/ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.2.yaml`)
remain byte-identical. They encode an incomplete drawdown basis; candidate.3
explicitly uses `max(initial_balance, highest_prior_session_closing_balance)`.
No prior close means initial balance. Apply the trailing amount and initial-balance
lock only at next session start, as ADR 002 already specifies.
The schema validates each version independently and rejects mixed-version fields.
All candidates are unpromoted and must not be used for eligibility calculations.
Exact hashes appear in `tests/fixtures/artifacts.sha256.json` and the review packet.

Freeze original UTF-8 bytes and their hash in every later experiment. A changed
rule or interpretation creates a new file and version; historical manifests
stay intact. Promoting a reviewed version requires source reconciliation,
reviewer identity/disposition and human decision evidence in this register.

## Examples and open issues

`growth_50k_reference.json` identifies official numeric examples separately from
synthetic boundary extensions. The floor sequence is 48000 → 49000 → 49000 →
50000 from prior closes 51000, 50500, 52500. Daily profits 2000 and 1000 miss the
consistency objective; a total of 5000 with best day 2000 meets it. Official
exposure examples include 4 standard + 10 micro and 2 mini + 30 micro.

- **Fee interpretation: unresolved official semantics.** ADR 003 is human-accepted
  for lab accounting only. FTMO's treatment of fees, including open-position entry
  fees and delayed postings, remains unverified. P1 must show gross and net-of-fees
  consistency shares separately and label the latter as the current lab convention
  pending verification. Neither may silently substitute for the other.
- **Fractional micros: unresolved official semantics.** Candidate.3 declares
  standard = 1.0, mini = 1.0, micro = 0.1. Summing fractional equivalents is a lab
  convention; examples involving whole groups of ten do not verify partial-group
  rounding/counting. The one-micro, mixed-class and 51-micro vectors carry that
  unresolved status. Do not call those outcomes FTMO-verified.
- **Scope acceptance:** human accepted P0 / 50K Evaluation scope on 2026-09-19.
- **Independent review:** Claude focused remediation re-review PASS at the HEAD
  recorded above, reported by the human on 2026-09-19. No GitHub account approval
  is claimed. The previous FAIL gate is superseded; P1 requirements are recorded
  in P0_ACCEPTANCE.md.
- **Calendar and endpoints:** ADR 002's exact-close quarantine and assessment
  ordering remain proposed lab boundaries. Supply a pinned session/holiday
  schedule and reconcile real source endpoints before real-data use.
- **Coverage and terms:** no market data or account-specific terms verified;
  source effective date unknown. Sparse marks cannot establish continuous equity
  compliance. Manifest promotion remains pending source/terms reconciliation; P0 acceptance
  does not alter immutable candidate metadata.

House risk limits will live in a separate practice-policy file, labelled house
rules. No house policy or evaluator is implemented in P0.
