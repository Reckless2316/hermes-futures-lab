# Futures Training Lab — install and handoff checklist

**Historical setup observations: 17 September 2026.** Current update, 2026-09-18:
the repository exists and is public, with MIT licensing; WSL GitHub CLI is
authenticated. Skip the historical creation commands below. Follow current
GITHUB_WORKFLOW.md, RESUME_P0.md and P0_VALIDATION.md for this existing checkout.
Past setup/publication decisions do not authorize future unrelated actions.

 This checklist distinguishes what is already present, what must be created for the project, and what is optional. The blueprint does not require a marketplace bundle, a GitHub connector, or any paid trading-data add-on to begin P0/P1.

**User-provided research wiki:** The authenticated [AgentWikis HyperFrames XL index](https://agentwikis.com/raw/hyperframes/wiki-xl/index.md) was reachable on 17 September 2026. Check its index before broad web searches and fetch a relevant page when the work concerns HyperFrames, video rendering, motion components, or explainers. The index currently lists no FTMO/futures or operator-product documentation; continue to current official sources for those topics. Hermes CLI already has the wiki access according to the user. Share only relevant excerpts or page references with Codex/Claude; do not replicate the credential across operators. Store any replacement bearer token in a local secret store or transient environment variable, outside the repository and handoff packets.

**Current GitHub ownership and setup:** `Reckless2316/hermes-futures-lab` is the
existing public project repository. WSL GitHub CLI/account verification is in
place. Preserve the separate upstream-pointed template checkouts. Follow
GITHUB_WORKFLOW.md for the existing PR branch; do not recreate the repository or
change visibility based on the superseded private-repository proposal.

## 1. Current operator installations

| Operator | Inspected state | Required download now | Official setup / extension source |
|---|---|---|---|
| Hermes Desktop / Agent | Windows Hermes executable found under `%LOCALAPPDATA%\hermes\bin\hermes.exe`; Agent `0.21.0` in that install. WSL has a separate Hermes Agent `0.21.3`. | **None for P0/P1.** Before P5, verify/update the Windows Desktop app only if the chosen SDK feature is absent. | [Hermes quickstart](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/getting-started/quickstart.md), [native plugin guide](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/plugins/index.md), [Desktop SDK](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/desktop-plugin-sdk.md) |
| OpenAI Codex CLI | Ubuntu WSL CLI `0.154.0` at `/home/reckless/.local/bin/codex`. | **None.** Sign in only if the current session is not authenticated. | [Codex CLI](https://learn.chatgpt.com/docs/codex/cli), [WSL setup](https://learn.chatgpt.com/docs/windows/wsl), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |
| Claude Desktop | Windows Claude package `1.52386.6.0` found. | **None.** Use chat or a Project with pasted text or supported text attachments. | [Install Claude Desktop](https://support.claude.com/en/articles/10065433-install-claude-desktop), [Projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects), [uploads](https://support.claude.com/en/articles/8241126-upload-files-to-claude) |

Version numbers are observations from this machine, not minimum supported versions. Current online Hermes documentation can be ahead of the installed Windows build, so P5 includes a real compatibility check. The Windows and WSL Hermes installations have separate homes and configuration; select **Windows Desktop** as the cockpit runtime and do not assume a plugin installed in WSL appears there.

## 2. Required project assets, by operator

### Hermes

- **Required now:** this document set and a new dedicated lab repository. No third-party skill/plugin download.
- **Required at P5:** the project’s own **hybrid Hermes plugin**, built in this repository. Root `plugin.yaml` and `__init__.py` register narrow agent tools; `desktop/plugin.js` supplies the native Desktop page; `dashboard/manifest.json` declares `dashboard/plugin_api.py`, which proxies to the lab’s local read interface. This plugin **does not exist yet** and must be built/tested before installation. Hermes documents the [agent plugin](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/plugins/index.md), the separate [Desktop SDK and unified package layout](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/desktop-plugin-sdk.md), and [install/enable controls](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/plugins.md).
- **Optional at P6:** the repo’s own `futures-coach` `SKILL.md` for repeatable post-trade review. It is a custom project file, not a named marketplace skill. Hermes’ [skills guide](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/work-with-skills.md) documents `SKILL.md` and skill installation. Do not install unrelated finance or autonomous trading skills.

### Codex CLI in WSL

- **Required now:** the existing Codex CLI, Git, Python 3.11, and the new repo’s root `AGENTS.md`. On this WSL install, `git`, `python3.11`, and `uv` were found. `AGENTS.md` is a repository instruction file, not a downloadable plugin. [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- **Recommended for the GitHub workflow:** install GitHub CLI (`gh`) in WSL using its [official Linux instructions](https://github.com/cli/cli/blob/trunk/docs/install_linux.md), then run `gh auth login` and verify it reports `reckless2316`. The GitHub web UI plus Git commands is an alternative if you do not install `gh`. Do not reuse the AgentWikis bearer credential for GitHub.
- **Required as implementation proceeds:** project dependencies named and locked in `pyproject.toml`/lockfile, plus a virtual environment. Codex should choose specific libraries only when a phase needs them and record why. No Codex marketplace plugin, MCP server, or trading add-on is required. [Codex CLI setup](https://learn.chatgpt.com/docs/codex/cli).
- **Optional later:** a repo-specific Codex skill for a repeated review/fixture workflow, only after the workflow stabilizes. Official [skill format](https://learn.chatgpt.com/docs/build-skills) is a folder with `SKILL.md`; it is not needed for initial development.

### Claude Desktop on Windows

- **Required now:** existing Claude Desktop, the blueprint/review packet, and access to the diff as pasted text or a supported text attachment. Claude [Projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects) can hold persistent instructions and reference documents; [uploads](https://support.claude.com/en/articles/8241126-upload-files-to-claude) work per chat. If `.md` is not accepted, paste its contents or use a `.txt` copy. Neither requires an extension.
- **Optional only if direct local-folder review is desired:** Claude Cowork with the lab repository folder explicitly shared, subject to plan availability. It adds file access and should remain read-only by instruction for this review role. [Cowork guide](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork).
- **No required Claude plugin or desktop extension.** If an MCP integration is later justified, Anthropic’s current route is Claude Desktop **Settings → Extensions** for a desktop extension or the **Customize** directory for skills/plugins/connectors. Install only a reviewed extension with minimal file scope. [Desktop extension guide](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop), [Claude directory guide](https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory).

## 3. Existing repository preparation

The WSL repository, Git identity, origin and root AGENTS.md are already set up.
Use the current P0 worktree and inspect `git status --short` before changes.
Read RESUME_P0.md and P0_VALIDATION.md for the phase and locked environment.
Do not run `git init`, recreate the remote repository or copy over its files.
The original creation recipe is retained in Git history at 3ee851b.

Keep `local_data/`, `.env`, auth files, databases and local review packets outside
Git. The public MIT repository must contain only material suitable for public
redistribution; third-party source/data terms still apply. Windows Hermes uses
a separate reviewed checkout at the later deployment phase.

## 4. Pass the instructions to each operator

1. **Hermes:** open Windows Hermes Desktop on the new repo or set its working directory to the reviewed Windows checkout. Paste `HERMES_OPERATOR.md`’s instruction block. Hermes drafts P0/P1 tickets. For now, you can manually relay its ticket to Codex; no cross-app automation is required.
2. **Codex:** in WSL, `cd /home/reckless/projects/hermes-futures-lab && codex`; paste the block in `CODEX_OPERATOR.md` and one ticket. Codex returns a branch/commit plus `REVIEW_PACKET.md` and test results.
3. **Claude:** in Windows Claude Desktop, create a Project if convenient; add the contents of `MASTER_BLUEPRINT.md`, `CLAUDE_OPERATOR.md`, and the current rules register as project knowledge. For each review, paste its instruction block with the stable diff/review packet. Return findings to Hermes and Codex. Do not rely on a private GitHub URL unless Claude can actually access it.
4. **Loop:** Codex fixes findings on its ticket branch; Claude re-reviews the new head; the user approves rule changes/merges after the acceptance gate is green.

## 5. Before installing the lab’s Hermes plugin

- Confirm the Windows Hermes app version and test a minimal documented Desktop plugin against it. The current Windows Agent reports `0.21.0` and the WSL Agent `0.21.3`; online documentation may describe newer behavior. Use the official Hermes update mechanism if the feature is absent, then rerun the smoke test. Do not blindly edit Hermes core.
- Build and test the standalone lab package on Windows from a reviewed Git commit. Give it a dedicated virtual environment and data directory on the **lab** machine.
- Start the lab API on `127.0.0.1` with only explicit read endpoints, bounded inputs, no wildcard CORS, no shell or SQL escape hatch, and no FTMO host credentials. Verify the Windows Desktop plugin shows the same synthetic evaluation as the CLI.
- For a published repo, Hermes supports `hermes plugins install owner/repo`, then explicit enablement; plugins are opt-in. Pin a full immutable commit for reproducibility where supported. For a local development package, use the documented plugin directory in the selected **Windows** Hermes profile and verify `hermes plugins list`; do not confuse it with the WSL `~/.hermes` profile. [Hermes plugin management](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/plugins.md).
- Review the plugin’s source and permission surface before enabling it. No third-party trading plugin is needed.

## 6. First-run verification commands

In Windows PowerShell:

```powershell
& "$env:LOCALAPPDATA\hermes\bin\hermes.exe" --version
Get-AppxPackage -Name Claude | Select-Object Name,Version
wsl --list --quiet
```

In Ubuntu WSL:

```bash
codex --version
git --version
python3.11 --version
cd /home/reckless/projects/hermes-futures-lab
git status --short
```

At P1, the final verification command must run the synthetic 50K Growth evaluation and print the manifest hash, event hash, balance/equity, floor, gross consistency share, net-of-fees consistency share (labelled lab
convention pending verification), unresolved fractional-micro semantics, and eligibility. Codex will supply that CLI command and its test suite as part of the implementation; this blueprint does not invent an unimplemented command name.
