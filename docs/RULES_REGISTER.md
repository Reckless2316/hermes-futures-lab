# Rules register

Observed 2026-09-17 by Codex; independent reviewer: **pending Claude Desktop**.
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

Active file: `rules/ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.2.yaml`.
ID: `ftmo-futures-growth-evaluation-50k`.
Version: `2026-09-18-candidate.2`. Supersedes: `2026-09-17-candidate.1`.
Review status: pending. Created 2026-09-18 to record the 2026-09-17 human decision;
source observation is still 2026-09-17, not a new source verification.

Historical file: `rules/ftmo_futures_growth_evaluation_50k_2026-09-17.yaml`,
version `2026-09-17-candidate.1`, is preserved without changes. Its fee basis is
unresolved and it must not be used for eligibility. The schema validates both
versions and rejects combinations of fields from different versions.
Exact-byte SHA-256 is recorded in `tests/fixtures/artifacts.sha256.json` and the
review packet. Run `futures-lab fingerprint <path>` to reproduce it.

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

- **Lab interpretation accepted:** ADR 003, realized gross P&L minus fees posted
  in the session, including entry fees; human approved 2026-09-17. Candidate.1
  predates approval. Candidate.2 and synchronized fixtures/schema record the
  accepted convention; independent review is still pending.
- **Scope acceptance:** 50K Evaluation; human pending.
- **Independent source/contract review:** Claude pending; no findings received.
- **Calendar:** supply a pinned session/holiday schedule before real-data use;
  P0 traces use an explicitly synthetic schedule.
- **Coverage:** no market data or account-specific terms verified. Later reports
  cannot establish continuous equity compliance from sparse fills alone.

House risk limits will live in a separate practice-policy file, labelled house
rules. No house policy or evaluator is implemented in P0.
