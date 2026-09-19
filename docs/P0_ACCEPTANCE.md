# P0 ticket and acceptance record

Task ID: P0-specification. Base: planning commit `22abff4`.
Branch: `feat/p0-specification`. Rules source observed: 2026-09-17.

## Final acceptance — 2026-09-19

Accepted implementation HEAD: `2384d549424f3897438059bc84796b65401116b0`.
The human reported Claude's focused remediation re-review **PASS** and accepted
P0's 50K Growth Evaluation scope on 2026-09-19. This records the external review
result supplied by the human; it does not claim a GitHub account approval.
The prior FAIL gate is superseded. The two Medium findings below are non-blocking
for P0 and mandatory requirements for P1. No P1 work or PR #2 merge is authorized
by this documentation/status update.

Candidate.1, candidate.2 and candidate.3 remain byte-for-byte unchanged. Their
embedded pending metadata is immutable; P0 acceptance does not promote a manifest
for evaluation or verify the unresolved official fee/fractional-micro semantics.

## Deliverable assertions

| Assertion | Evidence | Disposition |
| --- | --- | --- |
| Package installs; CLI works independently of Hermes/LLMs | pyproject.toml, locked environment, status/fingerprint commands | Passed local checks; see P0_VALIDATION.md |
| Data contract specifies identity, exact arithmetic, sessions and corrections | DATA_CONTRACT.md; synthetic normalized trace | Accepted for P0 at the recorded HEAD |
| Rule provenance and version are explicit | RULES_REGISTER.md, candidate YAML, strict schema, artifact hashes | Accepted for P0; immutable candidate metadata unchanged |
| Threat boundaries and future gates are explicit | THREAT_MODEL.md and AGENTS.md | Accepted for P0 at the recorded HEAD |
| Rule interpretations are documented before calculation code | ADRs 001–004 | Human remediation decisions recorded in candidate.3; official interpretations unresolved |
| P1 has official examples and boundary expectations | growth_50k_reference.json, round_trip.json | Contract validation only; evaluator absent |
| Claude finds no unresolved ambiguity changing pass/fail | Frozen diff and REVIEW_PACKET.md | **PASS — focused remediation re-review, 2026-09-19; two non-blocking Medium findings below** |
| Human accepts 50K Evaluation scope | Human decision recorded in ticket/review disposition | **Accepted — 2026-09-19** |

P0's implementation gate is locked installation, package build, CLI smoke checks,
contract/fixture tests and diff inspection. The review and human scope gates are
now satisfied at the recorded HEAD.
Official fee and fractional-micro interpretations remain explicitly unverified
lab conventions (ADRs 003–004), not blockers to the accepted P0 specification.
A successful schema test is not a financial correctness test. No skipped P1 test is counted as passed.

Migration note: no persistent database or previous package exists; no migration.
CI is introduced at P1 as specified by GITHUB_WORKFLOW. P0 has local checks only;
CI status must be reported as not configured, never green by inference.

## Non-blocking Medium findings — mandatory P1 requirements

1. **Drawdown basis is data, not executable semantics.** P1 must not evaluate or
   execute the `drawdown.basis` expression-string. Candidate.3's explicit formula
   is authoritative: `basis = max(initial_balance, highest_prior_session_closing_balance)`,
   using initial balance with no prior close; at next session start apply
   `floor = min(initial_balance, basis - drawdown_amount)`. Implement these
   semantics explicitly rather than treating manifest text as executable code.
2. **One authoritative contract-counting definition.** Candidate.3's
   `contract_counting` is authoritative. P1 must not let the legacy
   `max_contracts_mini_equivalent` field become a competing implementation rule.
   Counting classes and aggregation must follow `contract_counting`, preserving
   the unresolved fractional-micro lab-convention label.

Disposition: both findings accepted as explicit P1 requirements; neither is
implemented in this P0 documentation-only change.

## P1 handoff after acceptance

Implement immutable domain events and exact FIFO accounting; session calendar
with pinned timezone/calendar metadata; strict rules loader and pure evaluator;
explicit counting-class exposure and separate house practice guard; CLI
demonstration with separate gross and net-of-fees consistency shares and unresolved
lab-convention labels. This is future work, prohibited during this status update.
Convert these reference expectations into executable financial tests. Add
property, integration and boundary tests, plus required CI/security checks.

Report hashes and limitations for every evaluation. Refuse a pending manifest
for eligibility calculation. Use a new reviewed manifest after human decisions.
No UI, network API, historical import, replay engine or AI coach in this ticket.
