# P0 ticket and acceptance record

Task ID: P0-specification. Base: planning commit `22abff4`.
Branch: `feat/p0-specification`. Rules source observed: 2026-09-17.

## Deliverable assertions

| Assertion | Evidence | Disposition |
| --- | --- | --- |
| Package installs; CLI works independently of Hermes/LLMs | pyproject.toml, locked environment, status/fingerprint commands | Passed local checks; see P0_VALIDATION.md |
| Data contract specifies identity, exact arithmetic, sessions and corrections | DATA_CONTRACT.md; synthetic normalized trace | Prepared for review |
| Rule provenance and version are explicit | RULES_REGISTER.md, candidate YAML, strict schema, artifact hashes | Prepared; independent review pending |
| Threat boundaries and future gates are explicit | THREAT_MODEL.md and AGENTS.md | Prepared for review |
| Rule interpretations are documented before calculation code | ADRs 001–004 | Human remediation decisions recorded in candidate.3; official interpretations unresolved |
| P1 has official examples and boundary expectations | growth_50k_reference.json, round_trip.json | Contract validation only; evaluator absent |
| Claude finds no unresolved ambiguity changing pass/fail | Frozen diff and REVIEW_PACKET.md | **FAIL pending remediation; Claude re-review required** |
| Human accepts 50K Evaluation scope | Human decision recorded in ticket/review disposition | **Pending** |

P0's implementation gate is locked installation, package build, CLI smoke checks,
contract/fixture tests and diff inspection. P0 acceptance additionally requires
the last two rows and explicit disposition of the unresolved official fee and
fractional-micro interpretations (ADRs 003–004). A successful schema test is not a
financial correctness test. No skipped P1 test is counted as passed.

Migration note: no persistent database or previous package exists; no migration.
CI is introduced at P1 as specified by GITHUB_WORKFLOW. P0 has local checks only;
CI status must be reported as not configured, never green by inference.

## P1 handoff after acceptance

Implement immutable domain events and exact FIFO accounting; session calendar
with pinned timezone/calendar metadata; strict rules loader and pure evaluator;
explicit counting-class exposure and separate house practice guard; CLI
demonstration with separate gross and net-of-fees consistency shares and unresolved
lab-convention labels. This is future work, prohibited during this remediation.
Convert these reference expectations into executable financial tests. Add
property, integration and boundary tests, plus required CI/security checks.

Report hashes and limitations for every evaluation. Refuse a pending manifest
for eligibility calculation. Use a new reviewed manifest after human decisions.
No UI, network API, historical import, replay engine or AI coach in this ticket.
