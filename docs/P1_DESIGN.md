# P1 deterministic ledger and candidate Growth engine

Ticket: [Issue #3](https://github.com/Reckless2316/hermes-futures-lab/issues/3).
Base: `4740732d1ff4dfff3d0e9ebb042c08a8f6545a59` (merged P0).
Status: implementation pending independent Claude review and human acceptance.
Human-accepted [ADR 005](ADR/2026-09-19-005-p1-evaluation-status-decisions.md)
permits labelled candidate.3 lab estimates and withholds eligibility after observed
excess exposure without inventing permanent failure. P0 ADRs 001–004 otherwise
continue to govern. No manifest bytes or fixture expectations change.

## Package boundaries and arithmetic

- `domain/`: strict values, immutable canonical events, append-only journal and
  FIFO lots; standard library only, imports no other lab layer.
- `rules/`: approved manifest loader and pure drawdown/target/consistency/counting
  calculations. PyYAML is the sole runtime third-party dependency. Exact candidate.3
  SHA-256 is checked before safe YAML parsing; other bytes are refused.
- `data/`: bounded JSON parsing, explicit provenance and pinned session-calendar
  input. Duplicate JSON keys, nonfinite values and malformed types fail validation.
- `engine.py`: deterministic orchestration of those components; transactional
  application to disposable in-memory projections, never mutation of journal events.
- `reporting.py` / CLI: structured JSON and source-content identity. No financial
  logic is delegated to AI, UI, network, storage or an integration.

Amounts arrive as decimal strings; quantities are strict positive integers.
Finite decimal values, tick alignment and exact cents are checked. Accounting
uses a private Decimal context with precision 128 and an Inexact trap, independent
of the caller's context. Invalid precision is rejected, never silently rounded.
FIFO supports partial closes, multiple lots and reversals. Balance is initial
cash plus realized gross P&L minus posted commissions. Equity adds current
unrealized P&L. Each distinct Commission event posts once, including entry fees
for still-open positions and multiple fee components for a fill.

## Input and deterministic ordering

`futures-lab evaluate INPUT.json [--run-id ID] [--include-checkpoints]` accepts the
normalized P0 trace envelope (`schema_version`, `fixture_id`, `provenance`,
`calendar`, `events`). See `tests/fixtures/round_trip.json` and DATA_CONTRACT.md.
The optional synthetic `expected_checkpoints` field is ignored as input, never
trusted for outcomes. P1 does not import arbitrary vendor CSV, infer contracts,
simulate fills, or fetch missing data. Limits: 32 MiB JSON, 10,000 events per batch,
bounded identifiers/decimal strings and quantity at most 1,000,000,000 per event.
These are parser/resource limits, not FTMO rules.

Ordering requires strictly increasing sequence and nondecreasing UTC timestamp;
one account per journal. Exact duplicate `(account, source, source_event_id)`
imports are no-ops, including duplicates repeated after later events. Conflicting
duplicates, duplicate event IDs and out-of-order records enter quarantine.
Financial application is atomic per event; rejected events never partly change
cash or positions. Accepted canonical bytes and event-array SHA-256 are retained.
Quarantine records carry input/event hashes and reasons. Caller-owned dictionaries
and returned snapshots cannot mutate the journal. To reproduce the full audit,
retain the original bounded input alongside the report; P1 has no database.

Instrument specifications must match declared provenance and candidate counting
classes. Orders require explicit acceptance before fills; rejected orders and
overfills quarantine. Market/limit/stop intents describe recorded orders; no queue,
slippage, stop-trigger or execution model is invented. Corrections explicitly
quarantine as `correction_not_implemented`; reconciliation is a later accepted
workflow, never an in-place financial edit.

## Sessions and mark coverage

The input supplies a complete ordered schedule for its run. Session IDs are New
York closing dates; starts are 18:00 on the preceding date, closes no later than
16:10, with explicit early closes permitted. The runtime records the calendar hash
and installed tzdb version. It invents no holiday/weekend calendar. SessionClose
must match the supplied close; non-close events exactly at close or outside a
covered interval quarantine. A next-session transition requires the preceding
close and cannot skip an intervening supplied session.

`Engine.advance_to(utc)` advances a deterministic calendar clock without inventing
imported events. It activates the next floor at session start. The input batch
otherwise advances on its events. No wall clock, random number, network, or future
market event influences results. Exposed events/checkpoints are immutable copies.

A fill supplies that instrument's observed valuation at its exact timestamp.
PositionMark requires a preceding same-time, same-instrument trade MarketEvent
with the same price. Quotes/bars are retained but do not invent a mark path. Marks
are usable only at that exact timestamp; P1 has no accepted stale-price tolerance.
Every open instrument needs a current mark. Missing valuation on a financial
event is recorded permanently as incomplete valuation history, even if later flat.
This conservative policy also means a position open at SessionClose lacks an
accepted close-time trade mark under the current boundary contract, so its equity
is unavailable. It cannot meet the flat-position target condition in any case.
Reports explicitly limit coverage to recorded instants; sparse records cannot
certify continuous intraday compliance.

## Rules and aggregate status

Normal domain code calculates the next-session floor:

`min(initial_balance, max(initial_balance, highest_prior_session_closing_balance) - drawdown_amount)`.

With no close, the basis is initial balance. A close records cash but cannot move
the active session's floor; the next start applies it. The floor never decreases
and locks at initial balance. Candidate.3's expression-string is never evaluated,
parsed or interpreted as executable semantics. Observed equity at or below the
active floor permanently sets `drawdown_breached`, with event evidence. Later
recovery, quarantine or missing data cannot erase a known breach.

Counting sums absolute per-instrument net positions without offsetting different
contracts: standard 1.0, mini 1.0, micro 0.1 from `contract_counting`. The legacy
numeric cap is normalized once into `Ruleset.exposure_limit`; there is no competing
legacy counting algorithm. Fractional micro summation is visibly a lab convention
pending FTMO confirmation. Historical excess is retained and withholds eligibility
with `exposure_consequence_unresolved` / `MANUAL_REVIEW`, even after flattening.

Both consistency reports include best day, total, exact rational share and a
threshold result. Each computes its own day series; net is not substituted into
gross. Nonpositive denominators produce an explicit undefined reason. Fees use
their posting session, including open-position entry fees, under ADR 003's lab
convention. Aggregate lab eligibility uses the net view and labels that choice.
Official fee/day-assignment semantics remain unresolved.

When the two views disagree on `satisfied`, `data_quality_reasons` includes
`consistency_basis_divergence`. This explains dependence on the consistency basis;
it does not classify the input as corrupted or claim an FTMO breach/disqualification.
It is appended after aggregate-state selection, so it does not change the authorized
net-based lab state or the missing-data/breach precedence below. Consumers must
inspect the reason alongside both views, including when state is `eligible_estimate`.

State precedence is:

1. Known drawdown contact → `breached` (recorded lab drawdown, not an assertion that
   FTMO adjudicated the real account).
2. Missing data, quarantined input, valuation gaps or historical excess exposure
   → `data_unavailable` with specific reasons.
3. Flat after session close, balance at least initial + target, and net consistency
   satisfied → `eligible_estimate`, explicitly candidate.3 lab mode.
4. Otherwise → `not_yet_eligible`; consistency alone never breaches the account.

Evaluation has no daily loss limit or minimum trading-day requirement. Reports
preserve pending candidate status, `official_account_certification: false`, both
lab-convention labels, input/event/calendar hashes, source metadata and code-content
hash. The declared source-file hash is provenance supplied by the user, not proof
that P1 retrieved or authenticated an original vendor file. Invalid envelopes
return a smaller `data_unavailable` report containing input and rules identities;
no financial values are manufactured. CLI parsing/file failures exit 2.

## Scope, security and remaining interpretations

Futures-only policy classifications are recorded in RULES_REGISTER.md. P1 has no
news windows, CFD holding rules, universal risk-per-trade disqualifiers, qualitative
thresholds, training guardrails or full compliance engine. Missing official policy
semantics stay unknown/manual review/not implemented. No FTMO credentials,
connectivity, platform control, live orders, feed comparison, LLM dependency,
dashboard, strategy generation or Monte Carlo are introduced. Hermes is untouched.

Official fee/day assignment, fractional micros, excess-exposure consequences,
real-source boundary reconciliation, continuous mark coverage, account terms and
qualitative forbidden-practice adjudication remain unresolved. ADR 005 authorizes
the explicit lab outputs above while preserving those limitations. No additional
human interpretation was silently adopted.

There are no schema migrations or database changes: journal and projections are
in memory, and the original normalized input is the replay source. Performance is
bounded for small P1 batches; this is not a large-market-data engine. Tests are
offline and synthetic. Dependency advisory lookup is an explicit validation step,
outside runtime/tests. The credential scan checks tracked files offline, excluding
entropy heuristics because public SHA hashes dominate the evidence; it is a
pattern scan, not proof that every possible secret has been excluded.
