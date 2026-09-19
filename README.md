# Futures Lab

A local futures practice and research lab. The standalone Python core will
reconstruct synthetic or user-supplied practice events without Hermes or an LLM.
The initial scope is **50K FTMO Futures Growth Evaluation**.

**P0 review gate: FAIL pending remediation re-review; acceptance pending.** This version provides a CLI
skeleton, data contract, candidate rules manifest, threat model, decision records
and synthetic reference cases. It does not calculate P&L or evaluation status.
The fee convention is human-accepted for the lab, pending FTMO verification.
Claude re-review and human scope acceptance are required before P1. See [P0 acceptance](docs/P0_ACCEPTANCE.md).

## Run from this checkout

Use Python 3.11.16 (pinned in `.python-version`) and uv 0.12.17 for the
validated development environment. Run from the repository root:

```bash
uv sync --locked
uv run --locked futures-lab status
uv run --locked futures-lab fingerprint rules/ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.3.yaml
uv run --locked python scripts/verify_p0_artifacts.py
uv run --locked python -m unittest discover -s tests -v
uv run --locked pytest -q
uv build
```

See [clean-environment validation](docs/P0_VALIDATION.md), including cache and
isolated-environment instructions. Both runners execute the same tests.

This repository is **public** and licensed under [MIT](LICENSE), selected by the
human on 2026-09-18. External source material and licensed market data retain
their own terms; the repository license grants no rights to those materials.

The installed CLI uses only the Python standard library. Test dependencies and
the build backend are pinned; `uv.lock` records transitive dependencies. Initial
environment setup downloads packages; subsequent tests and CLI use no network.
The `fingerprint` command hashes bytes without validating or evaluating them.
Errors return exit code 2; successful commands return one stable JSON object.

## Contracts and review

- [Data contract](docs/DATA_CONTRACT.md): events, exact money, ordering and reports.
- [Rules register](docs/RULES_REGISTER.md): source observations and open questions.
- [Threat model](docs/THREAT_MODEL.md): trust boundaries and later security gates.
- [Decision records](docs/ADR/2026-09-17-001-p0-scope.md): scope and interpretations.
- [Synthetic fixtures](tests/fixtures/README.md): reference expectations for P1.
- [Operator workflow](docs/CODEX_OPERATOR.md): implementation and review handoff.

Runtime data belongs under ignored `local_data/`. This lab has no execution or
FTMO account connection. Future rule reports are estimates from recorded events;
FTMO determines actual account standing.
