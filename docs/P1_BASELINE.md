# P1 starting baseline — 2026-09-19

Ticket: [Issue #3](https://github.com/Reckless2316/hermes-futures-lab/issues/3),
read in full including its Futures-only rule hygiene section; no comments present.
Repository and authenticated identity: Reckless2316/hermes-futures-lab and
Reckless2316. Both origin URLs are
`https://github.com/Reckless2316/hermes-futures-lab.git`.

Local main was clean, fetched, and fast-forwarded without rewriting history.
P1 branch: `feat/p1-deterministic-engine`.
Worktree: `/home/reckless/projects/hermes-futures-lab/.worktrees/p1-deterministic-engine`.
Starting HEAD: `4740732d1ff4dfff3d0e9ebb042c08a8f6545a59`.
The required P0 merge is the starting commit itself; ancestry check passed.
The new worktree was clean before validation. P0 worktree was not reused.

Read AGENTS.md, README, MASTER_BLUEPRINT, CODEX_OPERATOR, GITHUB_WORKFLOW,
P0_ACCEPTANCE, P0_VALIDATION, DATA_CONTRACT, RULES_REGISTER, THREAT_MODEL,
ADRs 001–004, candidate.3/schema, synthetic recipe, 51 reference vectors and
13-event trace. Historical P0-only task restrictions do not override the human's
new P1 authorization. No P1 implementation code was written before this gate.

## Complete existing P0 gate

Environment: uv 0.12.17, CPython 3.11.16. Fresh P1 `.venv`; existing writable
cache reused. Commands run from the P1 worktree unless stated otherwise.

| Command | Result |
| --- | --- |
| `uv sync --locked --cache-dir /tmp/futures-lab-uv-cache` | Passed; fresh environment, 13 packages installed |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-uv-cache python -m unittest discover -s tests -v` | 20 tests OK, zero skipped (1.934s) |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-uv-cache pytest -q` | 20 passed, zero skipped (1.93s) |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-uv-cache python scripts/verify_p0_artifacts.py` | All three manifests/schema checks, nine hashes and trace/reference links passed |
| `uv build --offline --cache-dir /tmp/futures-lab-uv-cache` | Source distribution and wheel built |
| `uv venv /tmp/p1-baseline-20260919-vt933_qj/venv --python 3.11.16 --cache-dir /tmp/futures-lab-uv-cache` | Fresh isolated smoke environment created |
| `uv pip install --python /tmp/p1-baseline-20260919-vt933_qj/venv/bin/python --offline --no-deps --cache-dir /tmp/futures-lab-uv-cache dist/hermes_futures_lab-0.0.1-py3-none-any.whl` | Wheel installed without dependencies (absolute wheel path used from temporary directory) |
| Installed `futures-lab status`, run outside checkout | Passed; original specification-only P0 status |
| Installed `python -I` import/metadata checks | Site-packages import, zero runtime dependencies and MIT metadata/LICENSE verified |

Both runners execute the same 20 tests. This proves the P0 baseline, not an
implemented P1 engine. CI is not configured at this baseline.

All candidates matched starting-commit bytes exactly:

```text
candidate.1 c835db6b7f455c7df4a246827ab77653f94a0dc4af92c25ec20634fd826ea750
candidate.2 2da332b5627dee4585555e7af9cc375d8b1ab65107dba54b4c17d538b71179eb
candidate.3 a1dcf3f3ac04abb7c5334bd6e65e9374fc36d67c3422a4b590c3ed3ae8eeeda6
```

Baseline passed. Evaluation-status interpretations were documented in ADR 005 before dependent
implementation; the human accepted both recommendations on 2026-09-19.
