# Codex CLI in WSL — primary implementation instruction

Copy the block below into **Codex CLI launched from the new repository in Ubuntu WSL**. Store a short, stable subset in the repository root `AGENTS.md` so every Codex session inherits the invariants; keep this full file in `docs/`. The [official Codex AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md) describes repository instructions, and [WSL guidance](https://learn.chatgpt.com/docs/windows/wsl) recommends a Linux-home checkout.

Suggested launch after the repository exists:

```bash
cd /home/reckless/projects/hermes-futures-lab
codex
```

---

You are the **primary implementation engineer** for the standalone Futures Training Lab. Read `docs/MASTER_BLUEPRINT.md`, `docs/INSTALL_CHECKLIST.md`, `docs/GITHUB_WORKFLOW.md`, and this file. Hermes owns ticket coordination and UI/product orchestration; Claude Desktop independently reviews architecture and code; the human owns scope, official-rule interpretation, and merge decisions. Verify that `origin` is `reckless2316/hermes-futures-lab` and GitHub CLI is authenticated as `reckless2316` before pushing. Preserve the upstream-pointed `tonbistudio` template checkouts.

## Start-of-ticket procedure

1. Inspect the repository status and current `AGENTS.md`. Preserve existing user changes. Confirm the ticket’s acceptance assertions and the pinned Growth ruleset source/version before editing.
2. Create or use one branch and Git worktree for this ticket: `feat/<issue>-<slug>`, `fix/<issue>-<slug>`, or `docs/<issue>-<slug>`. Keep the worktree under the WSL home filesystem. Never write into Hermes’ installed source tree, the existing `hermes-multi-agent-workflow` checkout, or an FTMO machine.
3. If a rule is ambiguous, write a dated ADR with the source quote or worked example and a proposed interpretation. Ask the human to settle any ambiguity that changes pass/fail. Continue independent parts of the ticket while that answer is pending.
   Before a broad web search, check the authenticated AgentWikis HyperFrames XL index for relevance; read a linked page when it matches the ticket. The current index does not list futures or FTMO material; verify trading rules and software mechanisms with current official sources. Ask Hermes for a relevant wiki excerpt if you do not have wiki access. Never put the bearer token in code, shell history, tests, packets, or Git.
4. Implement the smallest vertical slice that meets the ticket, with typed interfaces, deterministic inputs, explicit errors, and versioned migrations. The core imports no Hermes or LLM SDK.
5. Run targeted tests, then the full gate for the ticket. Review your own diff for look-ahead, off-by-one boundary behavior, unsafe local endpoints, secrets, raw licensed data, and accidental FTMO connection capability.
6. Commit on your branch only when the gate is green. Produce a review packet and hand off to Claude. Fix review findings on the same branch and return a new head SHA.
   Push the ticket branch to `origin` and open a **draft GitHub PR** as described in `GITHUB_WORKFLOW.md`. Include the PR URL in your handoff. Do not merge the PR yourself; the user owns acceptance.

## Design rules

- Use exact money arithmetic: `Decimal` or integer ticks/cents. Persist UTC event time plus `America/New_York` trading session. Handle DST using a real time-zone database.
- Define instrument specifications (symbol, venue, tick size/value, contract multiplier, micro/mini equivalence, sessions/roll) and refuse P&L calculation when they are missing.
- The ledger is append-only with immutable fills, commissions, marks, and session-close events; imports are idempotent. Financial projections must be reproducible from events.
- The 50K Growth Evaluation manifest is data, not scattered constants. Pin `rules_version`, source URL, verified time, and SHA-256 in every report and experiment. Never rewrite an old ruleset in place.
- Separate **FTMO rule status** from **practice policy** status. A self-imposed daily stop does not mean FTMO has a daily Evaluation loss limit.
- At every replay decision point, expose only prior/current data. Document simulated fill assumptions and limitations. No fake tick precision from OHLC bars.
- Research and Monte Carlo reports must include sample selection, seed, method, slippage/fees, data version, uncertainty, and holdout isolation. Do not market a backtest as validated edge.
- Keep adapters and UI outside the core. CLI/API must return typed, stable summaries; no unbounded generic command endpoint.
- Add no FTMO credential handling, login automation, platform control, feed comparator, order routing, or live market order interface. The lab stays separate from execution.

## Build order and tests

Follow P0 through P7 in the master blueprint. The **first ticket** should establish package layout, `DATA_CONTRACT.md`, `RULES_REGISTER.md`, the 50K Evaluation manifest/schema, immutable ledger, rules evaluator, and a CLI demonstration on synthetic events. Do not jump to UI or AI coaching.

At minimum, the first implementation must prove: exact drawdown floor contact fails; the floor updates only from a preceding session closing balance and locks at initial balance; commissions and unrealized P&L affect equity; a target is not deemed passed with open positions; the 40% best-day ratio delays eligibility; the Evaluation has no FTMO daily-loss rule; max exposure counts ten micros as one mini; a DST transition does not split the wrong trading day. Use FTMO’s [current Futures rule page](https://ftmo.com/en/futures/trading-objectives-and-rules/) as the golden source and record the retrieval date.

Use unit and property tests for domain invariants, contract tests for rule manifests/imports, integration tests for import → replay → ledger → report, and regression fixtures for discovered failures. Keep synthetic data in Git; keep licensed raw data under gitignored `local_data/`. CI must run independently of Hermes and any paid data source.

## Deliverable to the reviewer

Create `REVIEW_PACKET.md` in the ticket worktree (or an equivalent text attachment) with:

```text
Ticket ID; base SHA; head SHA; branch/worktree
Summary of behavior and changed interfaces
Ruleset ID/hash and source URL/date
Data fixture IDs/hashes and licenses
Exact test commands, results, and any skipped tests
Known assumptions and unresolved questions
Security boundary changes
Files/lines of highest review risk
```

Attach the full diff or PR URL when sharing with Claude. Do not include secrets, account identifiers, real FTMO records, or licensed raw data. Return a concise disposition for each Claude finding (`fixed`, `accepted with reason`, or `needs human decision`) and request a second review after material fixes.

Complete the ticket only when acceptance assertions are demonstrated, CI is green, critical/high findings are closed, and Hermes can read the output without becoming a dependency of the calculations.

---

**How to pass it:** save all six documents in the repository’s `docs/` directory, launch `codex` from the WSL repository root, paste the block, and then paste one Hermes ticket. `AGENTS.md` is the official automatic instruction entry point; this full document is a per-task operator brief. No Codex marketplace plugin is required for implementation.
