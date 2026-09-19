# Data contract v1 (P0 proposal)

This is the P1 implementation contract. P0 provides fixtures and schema checks;
it does not import events into an operational ledger or evaluate them.

## Encodings and identity

Use UTF-8 JSON/JSONL for normalized events. Monetary amounts are signed decimal
strings with two fractional digits; prices, tick values, multipliers and ratios
are decimal strings with explicitly declared precision. No float, NaN, infinity,
implicit currency conversion or silent rounding. USD is the only candidate
currency. Quantities are positive integers; side is `buy` or `sell`. Reject
off-tick prices and amounts requiring unsupported fractional-cent rounding.

Every event carries `schema_version`, `event_id`, `event_type`, `account_id` (lab
ID only), `source`, `source_event_id`, `timestamp_utc` (RFC3339 UTC ending Z),
`session_id` (closing local date), `sequence`, `provenance_id`, and `payload`.
Sequence is a strictly increasing integer per account stream. Effective event
timestamps must be nondecreasing in an imported stream; ties use sequence.
Reject duplicate JSON keys and unknown versions/types/fields. Imported text is
data and must never be executed, templated or interpreted as operator instructions.

Idempotency key: `(account_id, source, source_event_id)`. An exact repeat of a
normalized event is a no-op. A reused key with changed content is a conflict
requiring quarantine. `event_id` is also unique. Preserve source order; adapters
must explicitly reconcile unordered input, never silently sort conflicting ties.

Provenance records contain ID, vendor/source, dataset ID and exact input SHA-256,
license/usage restrictions, synthetic flag, original timezone, adapter/version,
instrument specification IDs, gaps, and correction policy. Market files also
record venue, interval and contract-roll metadata. Raw data lives outside Git.

## Event payloads

| Type | Required payload and meaning |
| --- | --- |
| InstrumentSpec | instrument_id, symbol, venue, currency, tick_size, tick_value, multiplier, ftmo_counting_class, mini_equivalent, expiry, calendar_id, roll_policy; immutable specification selected by ID |
| RulesetSelected | ruleset_id, rules_version, ruleset_sha256; bind a run before financial events; one rules version per run |
| MarketEvent | instrument_id, kind (`trade`, `quote`, `bar`), kind-specific price fields, volume and interval for bars; never invent a tick path from OHLC |
| OrderIntent | order_id, instrument_id, side, quantity, order_type (`market`, `limit`, `stop`), limit_price/stop_price as applicable; lab simulation only |
| OrderAccepted | order_id and intent_event_id; simulation acceptance |
| OrderRejected | order_id, intent_event_id and reason_code; no fill or money change |
| Fill | fill_id, order_id, instrument_id, side, quantity, price; fees are separate Commission events |
| Commission | fill_id, amount (nonnegative USD decimal), currency; charge once at event time |
| PositionMark | instrument_id, price, market_event_id; revalue remaining quantity; no realized cash change |
| SessionClose | calendar_id; balances/positions are reconstructed, never trusted from supplied totals |
| JournalNote | referenced_event_ids and bounded plain text; no financial effect |
| Correction | target_event_id, reason, replacement_payload or null for void; append with recorded_at_utc; requires revision/reconciliation described below |

Instrument definitions precede referencing events. The multiplier times tick
size must equal tick value. Contract identifiers include expiry and do not
silently roll. A synthetic specification must never be treated as a real exchange
specification. Missing specifications or marks block calculations.
`ftmo_counting_class` is explicitly `standard`, `mini`, or `micro`; the candidate.3
weights are respectively 1.0, 1.0, and 0.1. `mini_equivalent` must match the
selected class weight, never an inference from the symbol or multiplier.
Exposure sums absolute net positions per contract times class weight. Fractional
micro summation is a lab convention pending FTMO confirmation (ADR 004); reports
must retain this unresolved status rather than claim official verification.

## Ledger and revisions

P1 uses FIFO lots within each instrument, handles partial exits and reversals,
and computes gross realized P&L as price movement in integer ticks times exact
tick value and closed quantity. Cash = initial balance + gross realized P&L −
posted fees. Equity = cash + unrealized P&L. Fees are never deducted twice.
Commission assignment for consistency follows the human-accepted ADR 003 lab
convention: subtract all fees posted in the session, including entry fees for
positions still open. Independent review and account-terms verification remain
separate. The P0 schemas cover only the authored trace subset, not every event
type or an operational importer; P1 must implement the wider contract above.

After each financial event, evaluate equity and exposure. Every required mark
must be present at the valuation instant; mark freshness/coverage is explicit.
Session close follows that session's fills, fees and marks. Assessment occurs
then; the next floor becomes active only at the next SessionStart clock boundary.
SessionStart is a derived calendar boundary, not a fabricated imported fill.

Corrections append to history and retain the target's original effective time
and session. Their sequence and recorded_at_utc describe arrival order; they
are exempt from ordinary nondecreasing effective-time ingestion only through a
dedicated reconciliation path. Rebuild a new projection revision as of a stated
knowledge cutoff; preserve the original projection and original bytes. Corrected
data is unavailable to replay decisions before the correction's recorded time.
P1 may reject correction input until this path exists; silently mutating events
or accepting corrections without replay support is forbidden.

## Session and quality contract

Use UTC with calendar zone `America/New_York`, never machine local time. Session
IDs identify the closing local date. ADR 002 defines endpoints, gaps and DST.
Calendar bytes, timezone database version and holiday/early-close overrides
are pinned per run. No session for weekends/gaps unless the pinned schedule says
otherwise. Unknown/missing timestamps, specs, calendar, conflicting duplicates,
unresolved corrections or inadequate marks produce quarantine with reason,
source row/key and raw-data reference; no partial success disguised as eligibility.

## Later report interface

Schema version 1 reports include lab account/run ID, as-of event/UTC time,
session ID, projection revision, ruleset ID/version/hash, event-data hash,
code commit/version, calendar hash/tzdb version, fill-model version and seed
(null when inapplicable), provenance/license references and coverage limitations.

Amounts: balance, equity, open P&L, fees, target progress, floor and buffer are
decimal strings. P1 MUST report separate `gross_consistency_share` and
`net_of_fees_consistency_share` objects. Each contains its own `best_day`, `total`,
exact `share` (reduced rational string such as `2/5`), and `reason` (null when
defined). Gross days are realized gross P&L; net days subtract every fee posted
in that session, including entry fees on open positions. Choose the best positive
day independently for each basis (zero if none); retain loss days in each total.
For each basis independently, nonpositive totals give `share: null` and
`reason: nonpositive_total_profit`. Never borrow the other basis's numerator,
denominator or result. Optional rounded display values must not drive eligibility.
`net_of_fees_label: lab_convention_pending_verification` is mandatory alongside
both outputs. Gross is a separate measure, not an assertion that FTMO requires
gross accounting. The current lab convention uses net; neither share silently
substitutes for the other. Pending official semantics must remain visible.

Also include mini-equivalent exposure, explicit counting classes and position
count, with `fractional_micro_summation: lab_convention_pending_ftmo_confirmation`.
Each rule includes evidence event/session IDs and a reason code.

Evaluation state is one of `data_unavailable`, `breached`, `not_yet_eligible`,
`eligible_estimate`. Data insufficiency prevents a clean eligibility result;
previously observed breach evidence must still be retained. Assessment time and
open positions are explicit. `practice_policy_status` and hash are separate and
cannot masquerade as FTMO rules. No actual-account pass/fail certification.

Persistence, migrations and API are absent in P0. P1 storage design must version
migrations and retain immutable event/rules bytes. Derived caches key on source,
code, calendar, rules and fill-model hashes; they are disposable.
