# Synthetic reference fixtures

All event prices, instruments, fills, fees, account IDs and journals here are
invented for this project. They contain no exchange feed or account records.
Synthetic fixtures may be used and redistributed for testing without market-data
license restrictions; they do not license the rest of this repository.

`growth_50k_reference.json` contains hand-selected P1 acceptance vectors.
`official_numeric_example` marks numeric examples transcribed from the rules
source in RULES_REGISTER; `synthetic_boundary` marks lab extensions. These are
expected results, not output from an implemented evaluator. ADR 003 fee vectors
carry `human_accepted_lab_convention`; all others remain proposed for review.
P0 validates contracts and provenance, not financial engine outcomes.

The active v2 fixtures select candidate.2, incorporating the 2026-09-17 human
decision. Original v1 fixture bytes are preserved by the checkpoint Git tag.
The historical candidate.1 manifest remains unchanged in the current tree.

`round_trip.json` is a normalized event trace with this authoring recipe:

- Synthetic mini LAB-MINI-202609 at fictional venue LAB: tick size 0.25, tick
  value 12.50, multiplier 50.00, mini equivalence 1.0; no real instrument claim.
- One contract bought at 100.00, fee 2.50, marked at 101.00, sold at 102.00,
  exit fee 2.50; all on session 2026-09-17, closing 20:10 UTC (16:10 EDT).
- Starting cash 50000.00. After entry fee: cash/equity 49997.50. At the mark:
  unrealized 50.00, equity 50047.50. After exit and fees: gross realized 100.00,
  total fees 5.00, cash/equity 50095.00, zero positions, current floor 48000.00.
- The next synthetic session opens at 22:00 UTC with floor 48095.00. Current
  session close does not activate that future floor. Target remains unmet.

The trace's provenance input hash identifies this exact authoring recipe file;
the rules selection identifies exact manifest bytes. `artifacts.sha256.json`
pins every reference/trace/schema/recipe and manifest for review, using paths
relative to the repository root. It excludes itself to avoid a self-reference.
Hashes provide integrity relative to reviewed Git history, not authenticity.

Session vectors use weekdays before and after the 2026 spring/fall DST changes.
Gap/close-boundary vectors are data-quality expectations. A real calendar,
holiday rules, importer and P1 evaluator remain to be implemented.
