# ADR 002: Rule boundaries and assessment timing

Date: 2026-09-17. Status: accepted P0 specification, 2026-09-19; Claude focused
remediation re-review PASS. See P0_ACCEPTANCE.md for the accepted HEAD and P1
requirements; official-source uncertainties below remain unresolved.
Source: [FTMO Futures rules](https://ftmo.com/en/futures/trading-objectives-and-rules/),
Growth / Evaluation / 50K, retrieved 2026-09-17. See RULES_REGISTER for provenance.

The official worked floor example progresses 48000, 49000, 49000, 50000 as
preceding closing balances progress 51000, 50500, 52500. P1 will use
`min(initial_balance, max(initial_balance, prior_closes...) - drawdown_amount)`
only at session start. Intraday highs and the current close do not change the
current session's floor. A contact or crossing is a permanent breach within the
run. Resetting creates a new run, never erases a breach.

The official target example requires balance 53000. Interpret target equality
as satisfied, assessed only after all events at session close, with no positions
open. An intraday target crossing is progress only. A 40% consistency share is
allowed; compare `best_day <= total_closed_profit * Decimal('0.40')` without
rounding a displayed ratio. For nonpositive total profit, ratio is null with
reason `nonpositive_total_profit`; eligibility is false. Loss days remain in the
denominator. An excess share delays eligibility; it does not breach the account.

Time is UTC plus `America/New_York`. A session ID is its closing local date.
Scheduled trading events occupy [18:00 previous date, 16:10 closing date); process
the explicit SessionClose at 16:10 after any same-instant bookkeeping. Quarantine
a trade exactly at the close pending source reconciliation; do not silently move
it to the next day. The daily gap has no session. This endpoint convention is a
lab data-quality choice, not a claim about venue last-trade semantics.

P1 must use an explicit calendar with eligible session dates and early closes,
versioned and hashed. P0 DST cases use synthetic weekday sessions on either side
of US DST transitions, not invented Sunday trading. Missing calendar or boundary
reconciliation blocks evaluation as `data_unavailable`. No automatic holiday or
early-close assumptions. UTC inputs avoid ambiguous local-clock parsing.

Exposure is the sum of absolute net positions per contract times its declared
candidate.3 FTMO counting-class weight (standard 1.0, mini 1.0, micro 0.1),
across instruments. Fractional summation remains a lab convention pending FTMO
confirmation; see ADR 004. Opposite positions in different contracts
do not offset. Working orders are not holdings, but the practice guard reserves
their possible additional exposure. Incomplete marks or event coverage cannot
prove that equity never touched the floor; reports must disclose coverage.
