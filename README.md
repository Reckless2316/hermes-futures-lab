# Futures Lab

A local futures practice and research lab. The standalone Python core can
reconstruct synthetic or user-supplied practice events without Hermes or an LLM.
The initial scope is **50K FTMO Futures Growth Evaluation**.

**P1 human-accepted at `fe7c1ba1b263ad6b0b897997116cd7bb982537ca`.** See
[P1 acceptance](docs/P1_ACCEPTANCE.md) for review evidence and merge authorization. The core
reconstructs recorded fills, fees, FIFO positions, balance/equity and session rule
state with exact Decimal arithmetic. [P0 acceptance](docs/P0_ACCEPTANCE.md) is
complete; P1 starts at its merge `4740732d1ff4dfff3d0e9ebb042c08a8f6545a59`.

[ADR 005](docs/ADR/2026-09-19-005-p1-evaluation-status-decisions.md) authorizes
explicitly labelled candidate.3 lab eligibility estimates while preserving its
pending manifest status. Net-of-fees consistency and fractional micro summation
remain lab conventions pending FTMO confirmation. Observed excess exposure
withholds eligibility pending an accepted consequence; it does not invent an FTMO
disqualification. All three historical candidates remain immutable.

## Run from this checkout

Use Python 3.11.16 (pinned in `.python-version`) and uv 0.12.17 for the
validated development environment. Run from the repository root:

```bash
uv sync --locked
uv run --locked futures-lab status
uv run --locked futures-lab evaluate tests/fixtures/round_trip.json
uv run --locked futures-lab fingerprint rules/ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.3.yaml
uv run --locked python scripts/verify_p0_artifacts.py
uv run --locked python -m unittest discover -s tests -v
uv run --locked pytest -q
uv build --no-sources
uv run --locked python scripts/smoke_wheel.py
```

See [P1 validation](docs/P1_VALIDATION.md) for the complete clean-environment gate,
and [P1 design](docs/P1_DESIGN.md) for inputs, outputs and limitations. Both runners
execute the same tests; the accepted P0 artifact suite remains part of that gate.

This repository is **public** and licensed under [MIT](LICENSE), selected by the
human on 2026-09-18. External source material and licensed market data retain
their own terms; the repository license grants no rights to those materials.

The installed CLI uses Python and pinned PyYAML to load hash-approved candidate
bytes. The domain uses only the standard library. Test dependencies and the build
backend are pinned; `uv.lock` records transitive dependencies. Initial
environment setup downloads packages; subsequent tests and CLI use no network.
The `fingerprint` command hashes bytes without validating or evaluating them.
Invalid files/commands return exit code 2. A parsed evaluation with insufficient
data returns explicit `data_unavailable` JSON; it never estimates missing money.

## Contracts and review

- [Data contract](docs/DATA_CONTRACT.md): events, exact money, ordering and reports.
- [Rules register](docs/RULES_REGISTER.md): source observations and open questions.
- [Threat model](docs/THREAT_MODEL.md): trust boundaries and later security gates.
- [Decision records](docs/ADR/2026-09-17-001-p0-scope.md): scope and interpretations.
- [Synthetic fixtures](tests/fixtures/README.md): reference expectations for P1.
- [Operator workflow](docs/CODEX_OPERATOR.md): implementation and review handoff.

Runtime data belongs under ignored `local_data/`. This lab has no execution or
FTMO account connection. Rule reports are estimates from recorded events;
FTMO determines actual account standing.
