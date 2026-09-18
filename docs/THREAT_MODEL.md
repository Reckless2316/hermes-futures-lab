# Threat model v1

Scope: P0 local specification CLI, with explicit controls required before later
phases. Assets are deterministic results, event/rule provenance, private source,
licensed input data and the isolation of the user's execution environment.

The current trust boundary is user-selected local artifact → read-only CLI →
stdout. Test fixtures and build inputs come from this reviewed checkout. There
is no API, database, plugin, credential store or financial engine in P0.

| Threat / entry | Required control | Evidence / gate |
| --- | --- | --- |
| Wrong product or changed rule bytes | Pin stage, version, original bytes and SHA-256; never overwrite historical manifests | P0 strict manifest schema, fixture hashes and rules register; P1 every report |
| Floating-point drift, duplicated fees or fills | Decimal/ticks, explicit fee events, unique import keys and append-only revisions | P0 contract and hand-calculated trace; P1 invariants/idempotency tests |
| Missing marks, timestamps or wrong DST mapping | Quarantine gaps and unknown specs; version calendar/tzdb; disclose observation coverage | P0 session vectors; P1 session and insufficient-data tests |
| Future information in replay | Separate effective/arrival times, bind code/data versions, reveal only current/prior events | P0 correction contract; P3 look-ahead tests |
| Malicious journal or imported data | Treat as inert bounded data; no eval, shell, pickle, template execution, or unsafe YAML loaders | P0 safe YAML in tests; P2 importer limits; P6 injection fixtures |
| Data/secret disclosure via Git or packets | Ignore raw data, auth files, DBs, environments and private packets; inspect staged files | P0 ignore checks and diff review; CI secret scan required with P1 |
| Supply-chain changes | Pin package/build dependencies and lock hashes; review dependency changes | P0 uv.lock/build gate; P1 dependency audit and pinned Actions |
| Access to FTMO execution | No account credentials, order routing, platform automation, network share or remote control | Current CLI has no networking; deployment isolation must be verified separately |
| Later API/plugin misuse | Loopback only, authenticated/scoped read DTOs, bounded requests, no generic shell/SQL, restrictive CORS | P5 security tests; absent in P0 |
| Coach corrupts accounting or leaks data | Read-only summaries and bounded citations; no ledger/rules/order authority | P6 adversarial tests; absent in P0 |

The fingerprint command reads the path the user explicitly supplies and emits
only its digest. It does not certify file safety, financial correctness or source
authenticity. Reviewers must inspect the corresponding bytes and sources.

Residual risks: local machine compromise and malicious package installation are
outside the CLI's isolation guarantees. Sparse practice data cannot prove
continuous equity compliance. Host network isolation, Windows runtime, backup
and restore, and data-license review have not been tested in P0. A private
repository and `.gitignore` do not remove already committed sensitive material.

Operational response: quarantine disputed input, retain original hashes and
evidence, invalidate dependent projections, and review a new version. Never
silently repair a past result or present a stale result as current.
