# Resume P0 from the saved checkpoint

Saved at the user's request on 2026-09-17. This is a **work-in-progress
checkpoint**, not P0 acceptance or a completed implementation ticket.

## Location and bookmark

- Repository: `/home/reckless/projects/hermes-futures-lab`.
- Worktree: `/home/reckless/projects/hermes-futures-lab/.worktrees/p0-specification`.
- Branch: `feat/p0-specification`.
- Bookmark tag: `checkpoint/p0-2026-09-17` (created after this note).
- Base commit: `22abff4` (planning documents).
- GitHub: private `Reckless2316/hermes-futures-lab`; authenticated account and
  origin were verified during this session. Verify again before any push.

Resume from the worktree, which already has the branch checked out:

```bash
cd /home/reckless/projects/hermes-futures-lab/.worktrees/p0-specification
git status --short
git log -1 --oneline checkpoint/p0-2026-09-17
cat docs/RESUME_P0.md
```

Suggested next-session request:

> Read docs/RESUME_P0.md and continue P0 on feat/p0-specification. Preserve the
> saved candidate.1 rules bytes, apply the recorded human ADR 003 decision in a
> new candidate version, complete the P0 checks and prepare the Claude review
> packet and draft PR. Verify origin is Reckless2316/hermes-futures-lab before
> pushing. Do not bypass P0 acceptance to start P1.

## Decisions and evidence already established

The user requested the implementation-engineer role and starting with P0. Read
MASTER_BLUEPRINT, GITHUB_WORKFLOW, CODEX_OPERATOR and INSTALL_CHECKLIST. Their
first-ticket suggestion includes P1, but the blueprint explicitly gates later
phases on P0 acceptance. This checkpoint implements only P0 specification work.

The official FTMO Futures rules and comparison pages were directly retrieved on
2026-09-17. Core numeric settings match the supplied blueprint. No broad search
or authenticated wiki research was needed. No external skills or subagents were
used. No other repositories, Hermes installation or execution machine changed.

**User accepted ADR 003:** daily consistency profit is realized gross P&L minus
all fees posted in that session, including entry fees for still-open positions.
Record this as a lab convention, not an official account-terms verification.
Do not ask the same interpretation question again.

## Files prepared

- AGENTS.md, README, Python 3.11 package/CLI skeleton and pinned pyproject/uv.lock.
- DATA_CONTRACT, RULES_REGISTER, THREAT_MODEL, P0_ACCEPTANCE and three dated ADRs.
- Candidate.1 YAML and strict candidate schema.
- 42 reference cases, a 13-event synthetic round-trip trace, fixture schemas and
  SHA-256 inventory. These are proposed P1 expectations, not evaluator results.
- Ignore rules for worktrees, build outputs and PR_BODY.md (original typo retained).

`uv sync --python 3.11 --cache-dir /tmp/futures-lab-uv-cache` succeeded after
network approval. Build backend: Hatchling 1.27.0. Development dependencies:
PyYAML 6.0.3 and jsonschema 4.25.1, with transitive packages locked. Runtime has
no dependencies. The cache override avoids writing to the protected home cache.
The local `.venv` is disposable and ignored; it is not part of the bookmark.

## Remaining work, in order

1. Create a new candidate.2 manifest applying ADR 003; preserve candidate.1 bytes.
   Update schema, register, trace rules reference, fee-vector decision metadata,
   README command and artifact inventory consistently. Current candidate.1 and
   fixtures intentionally retain their pre-decision state at this checkpoint.
2. Add meaningful contract/CLI tests. There are fixture schemas but **no test
   modules yet**. Do not report `unittest discover` with zero tests as a pass.
   Check strict decimal types, extra fields, source/hash linkage, event identity,
   reference integrity and CLI errors. Financial engine tests belong to P1.
3. Complete P0 installation/build/CLI/contract checks and self-review. Review the
   large generated JSON schemas and draft data contract for consistency. Pin
   hashes only after intended artifacts are settled.
4. Prepare gitignored REVIEW_PACKET.md, REVIEW_DIFF.txt and PR_BODY.md with
   base/head SHA, rules/fixture hashes, exact checks and limitations. Create a
   draft PR on the verified origin; no GitHub issue/PR has been created yet.
5. Obtain Claude's independent review and human scope acceptance. Both remain
   pending. No findings have been received. Human ADR 003 approval is recorded.
   Merge and phase acceptance belong to the human; do not claim CI is green
   (CI is not configured; workflow schedules it for P1).

No ledger, financial evaluator, importer, database, API, Hermes plugin or AI
coach exists. No real/paid data, account records or credentials are in fixtures.
There is no migration. The CLI only reports implementation status or hashes a
user-selected file. Current milestone limitations are explicit in README.

## Snapshot verification record

See `CHECKPOINT_VERIFICATION.md` beside this note for commands and actual
results captured immediately before the bookmark commit. The checkpoint can be
reviewed independently of conversation history. Its tag does not imply release,
Claude approval, financial correctness, or completion of the P0 gate.
