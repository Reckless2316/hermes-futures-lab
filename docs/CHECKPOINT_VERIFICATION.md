# P0 checkpoint verification — 2026-09-17

This record describes local artifact checks, not the full P0 gate or P1 financial
tests. Run from the P0 worktree. Python 3.11.16; uv 0.12.7.

| Command | Actual result |
| --- | --- |
| `uv sync --python 3.11 --cache-dir /tmp/futures-lab-uv-cache` | Passed; 8 packages resolved/installed; uv.lock created |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-uv-cache futures-lab status` | Passed; specification_only, evaluation_available=false, acceptance pending |
| `uv run --locked --offline --cache-dir /tmp/futures-lab-uv-cache futures-lab fingerprint rules/ftmo_futures_growth_evaluation_50k_2026-09-17.yaml` | Passed; SHA-256 below |
| `uv build --offline --cache-dir /tmp/futures-lab-uv-cache` | Passed; source distribution and wheel built |
| `.venv/bin/python scripts/verify_p0_artifacts.py` | Three schema validations, seven artifact hashes and trace linkage checks passed |
| `git diff --cached --check` | Passed before checkpoint commit |

Candidate.1 SHA-256:
`c835db6b7f455c7df4a246827ab77653f94a0dc4af92c25ec20634fd826ea750`.

No test modules exist yet. No financial evaluator, property/integration suite,
installed-wheel isolation test, CI/security scan, or Claude review ran. Build
success does not prove financial correctness. Artifacts retain pre-ADR-003
decision metadata as documented in RESUME_P0; synchronization is next.

No push or draft PR is part of this checkpoint. It is saved locally as a commit
and annotated tag. A portable Git bundle is exported to ignored
`local_data/checkpoints/p0-2026-09-17.bundle`; it includes committed history and
the branch/tag, not virtual environments, caches or secrets. To restore elsewhere:

```bash
git clone /path/to/p0-2026-09-17.bundle -b feat/p0-specification restored-lab
```

A bundle clone initially uses the bundle as origin. Before later publishing,
restore and verify the intended GitHub remote and authenticated account using
GITHUB_WORKFLOW. The existing main checkout remains on the planning baseline.
