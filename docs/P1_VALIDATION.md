# P1 locked validation

P0 clean-start evidence is in P1_BASELINE.md. P1 starts from merged P0 commit
`4740732d1ff4dfff3d0e9ebb042c08a8f6545a59`. Both runners discover the same suite;
test counts are not additive. Accepted P0 artifact bytes remain unchanged.

Use uv 0.12.17 and Python 3.11.16 (`.python-version`). From a fresh checkout with
no `.venv`, run all of the following. If the default uv cache is not writable,
set `UV_CACHE_DIR=/tmp/futures-lab-uv-cache` first. Environment/package setup and
advisory lookup need network or a populated cache; tests and runtime need none.

```bash
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked pytest -q
uv run --locked python scripts/verify_p0_artifacts.py
uv run --locked mypy --ignore-missing-imports --check-untyped-defs src/futures_lab
uv run --locked ruff check src/futures_lab tests scripts/check_secrets.py scripts/smoke_wheel.py --select F
uv run --locked ruff format --check src/futures_lab tests/test_domain.py tests/test_engine.py tests/test_financial_rules.py tests/test_assessment.py tests/test_p1_cli.py scripts/check_secrets.py scripts/smoke_wheel.py
uv run --locked python scripts/check_secrets.py
uv export --locked --no-emit-project --format requirements-txt --output-file /tmp/audit-requirements.txt
uv run --locked pip-audit --strict --disable-pip --require-hashes -r /tmp/audit-requirements.txt --progress-spinner off
uv build --no-sources
uv run --locked python scripts/smoke_wheel.py
```

The GitHub workflow runs the same gate using commit-pinned Actions and read-only
repository permissions. Never infer remote CI success solely from local results.
The wheel smoke installs into a fresh temporary environment outside the checkout,
uses isolated Python mode, loads packaged candidate.3, checks MIT/runtime metadata,
and verifies deterministic CLI evaluation. Keep only one built wheel in `dist`.

The initial advisory scan flagged pytest 8.4.2 (PYSEC-2026-1845); P1 pins the reported
fixed release 9.0.3. The dependency audit uses hash-pinned lockfile export including
development dependencies; it neither audits the editable project as a published
distribution nor claims to establish the security of system Python/tzdb or GitHub
Actions. Credential scanning is offline, tracked-file pattern detection with
entropy heuristics excluded; inspect the complete staged diff as well.

Final frozen results, full HEAD SHA, changed-file inventory and review range are
recorded in the local ignored REVIEW_PACKET.md and the P1 draft PR. Independent
Claude review and human P1 acceptance remain pending.
