# P0 implementation validation — 2026-09-18

Local implementation checks passed. P0 acceptance remains pending Claude review
and human approval of the 50K Evaluation scope. ADR 003's lab fee convention was
accepted by the human on 2026-09-17 and is recorded in candidate.2.

Environment: Python 3.11.16, uv 0.12.7. Commands ran from the P0 worktree unless
otherwise stated. The cache override is an environment-specific writable path.

| Command | Result |
| --- | --- |
| `uv sync --locked --offline --python 3.11 --cache-dir /tmp/futures-lab-uv-cache` | Passed; locked environment synchronized without network |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-uv-cache python -m unittest discover -s tests -v` | 15 tests passed, zero skipped |
| `uv build --offline --cache-dir /tmp/futures-lab-uv-cache` | Source distribution and wheel built |
| `uv venv /tmp/futures-lab-p0-wheel-20260918 --python 3.11 --cache-dir /tmp/futures-lab-uv-cache` | Created separate test environment |
| `uv pip install --python /tmp/futures-lab-p0-wheel-20260918/bin/python --offline --no-deps --cache-dir /tmp/futures-lab-uv-cache dist/hermes_futures_lab-0.0.1-py3-none-any.whl` | Wheel installed with no runtime dependencies |
| `/tmp/futures-lab-p0-wheel-20260918/bin/futures-lab status` from `/tmp` | Stable JSON: specification_only, evaluation_available=false, acceptance pending |
| Isolated `python -I` import and `importlib.metadata.requires` check from `/tmp` | Loaded site-packages copy; package has no runtime dependencies |
| `git diff --check` and staged equivalent | Passed before commit |

The tests cover both candidate schema versions, exact historical manifest bytes,
8 artifact hashes, trace/reference linkage, accepted fee metadata, malformed
amounts/quantities, duplicate keys, unsafe YAML tags, invalid timestamps, event
ordering, unknown references, off-tick prices, overfilled intents, DST reference
windows, stable CLI output, file hashing and CLI error exits. The artifact
verification script also runs as part of the suite.

A test initially exposed that JSON Schema's date-time format checker was absent
without its optional dependency. The artifact checker now registers an explicit
UTC parser; invalid dates and separators fail the schema gate. Decimal patterns
also reject trailing newlines. These are fixture validation controls, not a
production importer or financial evaluator.

Candidate.2 exact-byte SHA-256:
`2da332b5627dee4585555e7af9cc375d8b1ab65107dba54b4c17d538b71179eb`.
Candidate.1 remains
`c835db6b7f455c7df4a246827ab77653f94a0dc4af92c25ec20634fd826ea750`.
All other hashes are in `tests/fixtures/artifacts.sha256.json`.

No database/migration exists. No financial engine, P1 property/integration tests,
CI, automated dependency audit, dedicated secret scanner or external Claude
review has run. Git-tracked paths and the implementation diff were manually
inspected for secrets, raw data and execution connectivity. CI/security gates
remain P1 work under GITHUB_WORKFLOW; they are not reported as passing here.

Rules are pinned to the source observation on 2026-09-17. Candidate.2's creation
on 2026-09-18 incorporates the human convention; it is not a fresh official-source
verification or account-specific-terms review. All 43 reference cases remain
proposed P1 expectations, with fee interpretation acceptance recorded separately.
