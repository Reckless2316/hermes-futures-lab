# P0 remediation validation — 2026-09-18

Local remediation checks passed. Final P0 acceptance was recorded on 2026-09-19:
Claude focused remediation re-review PASS and human scope accepted for
`2384d549424f3897438059bc84796b65401116b0`. See P0_ACCEPTANCE.md. No P1
financial implementation or CI exists. Both runners exercise the same 20 tests,
not 40 independent tests. All passed; zero skipped.

## Reproduce from a clean checkout

Use uv **0.12.17**, enforced by `tool.uv.required-version`. `.python-version`
pins CPython **3.11.16** for development validation. Package metadata permits
Python >=3.11, but other interpreters/platforms were not validated in this run.
Run from the checked-out repository root, with no pre-existing `.venv`:

```bash
uv --version
uv sync --locked
uv run --locked python --version
uv run --locked python -m unittest discover -s tests -v
uv run --locked pytest -q
uv run --locked python scripts/verify_p0_artifacts.py
uv build
```

Initial sync requires package-index access (and interpreter download if absent).
Use `export UV_CACHE_DIR=/tmp/futures-lab-uv-cache` if the normal home cache is
outside writable roots. Do not use system Python/pytest against an unsynchronized
checkout or silently skip unavailable dependencies. `tests/__init__.py` supports
unittest discovery; `scripts/__init__.py` and pytest's explicit root `pythonpath`
make the development helper import stable. The installed CLI stays independent
of test helpers and has no runtime dependencies.

Development requirements/transitive versions and artifact hashes are locked in
uv.lock. Hatchling and all its build dependencies on Python 3.11 are pinned in
`tool.uv.build-constraint-dependencies`; isolated build requirements are resolved
separately from application dependencies. See the official
[uv build-constraint setting](https://docs.astral.sh/uv/reference/settings/#build-constraint-dependencies).
These pins make the tested package selection reproducible; they do not claim
bit-for-bit identical build output across operating systems or timezone databases.

## Observed clean-environment run

A clean checkout of the staged remediation files was produced using
`git checkout-index --all --prefix=/tmp/futures-lab-p0-clean-_phmu4kn/`.
It contained neither a copied virtual environment nor editable-install metadata.
The cache `/tmp/futures-lab-p0-clean-cache-_phmu4kn` was new. CPython 3.11.16 was
already available; this run did not test downloading Python. Validation and
resume prose were finalized after the run; tested code, manifests, fixtures,
packaging and lockfile bytes match the committed remediation.

Commands below ran in `/tmp/futures-lab-p0-clean-_phmu4kn` unless stated otherwise.

| Command | Result |
| --- | --- |
| `uv sync --locked --cache-dir /tmp/futures-lab-p0-clean-cache-_phmu4kn` | Passed; created .venv, built editable package, prepared/installed 13 packages from a fresh cache |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-p0-clean-cache-_phmu4kn python -m unittest discover -s tests -v` | **20 tests, OK**, zero skipped (1.957s) |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-p0-clean-cache-_phmu4kn pytest -q` | **20 passed**, zero skipped (1.97s) |
| Artifact checker, executed by both suites | All three manifest schemas, 9 hashes, both historical manifests, trace and reference links passed |
| `uv build --offline --cache-dir /tmp/futures-lab-p0-clean-cache-_phmu4kn` | Source distribution and wheel built successfully |
| `uv venv /tmp/futures-lab-p0-wheel-_phmu4kn --python 3.11.16 --cache-dir /tmp/futures-lab-p0-clean-cache-_phmu4kn` | Created separate wheel-smoke environment |
| `uv pip install --python /tmp/futures-lab-p0-wheel-_phmu4kn/bin/python --offline --no-deps --cache-dir /tmp/futures-lab-p0-clean-cache-_phmu4kn dist/hermes_futures_lab-0.0.1-py3-none-any.whl` | Installed wheel with no dependencies |
| `/tmp/futures-lab-p0-wheel-_phmu4kn/bin/futures-lab status` from `/tmp` | Stable specification-only JSON, evaluation unavailable, acceptance pending |
| Isolated `python -I` import/metadata check from `/tmp` | Loaded site-packages, no runtime requirements, MIT metadata and LICENSE included |
| `git diff --cached --check`; historical-manifest diff against `3ee851b` | Passed; both historical manifest diffs empty |

New regressions reject the incomplete drawdown basis, wrong/missing counting
classes, false verification claims, omitted gross/net reports or labels, and
class/weight mismatches. Reference cases cover an empty history, losing first
close, all closes below initial, separate standard/mini/micro counts, fees changing
the share/best day, and a zero net denominator with a positive gross denominator.
These are P0 contracts and authored expectations, not financial engine outcomes.
A first run caught a null-share schema error; it was fixed before the clean run.

Candidate SHA-256 values:

```text
candidate.1  c835db6b7f455c7df4a246827ab77653f94a0dc4af92c25ec20634fd826ea750
candidate.2  2da332b5627dee4585555e7af9cc375d8b1ab65107dba54b4c17d538b71179eb
candidate.3  a1dcf3f3ac04abb7c5334bd6e65e9374fc36d67c3422a4b590c3ed3ae8eeeda6
```

Candidate.1 and candidate.2 match the pre-remediation bytes at `3ee851b`.
The nine-file inventory is `tests/fixtures/artifacts.sha256.json`. V3 includes
51 reference cases and 13 synthetic events. Source observation remains 2026-09-17;
remediation is not a fresh FTMO source or account-terms verification.

No database or migration, financial evaluator, property/integration engine tests,
CI, dependency audit or automated secret scan was introduced or claimed to pass.
The public diff was inspected for source scope, credentials, raw data and execution
connectivity. The completed independent re-review and unresolved official interpretations are
listed in RULES_REGISTER and ADR 004. Original validation remains in Git at 3ee851b.

## Acceptance-status validation — 2026-09-19

The documentation-only acceptance update reran the complete P0 gate from the
P0 worktree using Python 3.11.16 and uv 0.12.17. Existing development environment
and cache were reused; the fresh-checkout evidence above remains historical.
All commands below passed. No tests were skipped.

| Command | Result |
| --- | --- |
| `uv sync --locked --cache-dir /tmp/futures-lab-uv-cache` | Passed; lock unchanged |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-uv-cache python -m unittest discover -s tests -v` | 20 tests OK (1.946s) |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-uv-cache pytest -q` | 20 passed (2.00s) |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-uv-cache python scripts/verify_p0_artifacts.py` | Three manifest schemas, nine hashes and fixture links passed |
| `uv build --offline --cache-dir /tmp/futures-lab-uv-cache` | Source distribution and wheel built |
| `uv venv /tmp/p0-acceptance-20260919-40mcut6e/venv --python 3.11.16 --cache-dir /tmp/futures-lab-uv-cache` | Fresh isolated wheel environment created |
| `uv pip install --python /tmp/p0-acceptance-20260919-40mcut6e/venv/bin/python --offline --no-deps --cache-dir /tmp/futures-lab-uv-cache dist/hermes_futures_lab-0.0.1-py3-none-any.whl` | Wheel installed with no dependencies |
| Installed `futures-lab status` and isolated `python -I` import/metadata checks from the temporary directory | Specification-only CLI works; site-packages import, no runtime dependencies, MIT metadata/license verified |
| `git diff --check` and exact-byte comparisons against accepted HEAD `2384d549424f3897438059bc84796b65401116b0` | Passed; all three candidate files match, with SHA-256 values listed above |

The unchanged CLI still emits its original literal
`pending_external_review_and_human_scope_approval`. Runtime code/tests are outside
this documentation-only update; P0_ACCEPTANCE.md records the actual accepted gate.
Immutable candidate metadata also remains unchanged. No P1 implementation or
manifest promotion is implied by these validation results.
