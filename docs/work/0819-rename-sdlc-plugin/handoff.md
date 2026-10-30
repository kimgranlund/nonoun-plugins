---
id: T-0819
title: "Rename sdlc-lite to sdlc, conductor to factory, direct to live; marketplace nonoun"
type: chore           # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0815]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
claimed_by: sdlc-lite-author 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The plugin, its agents and its marketplace carry the new names everywhere, as one clean break shipped as 1.0.0:
- plugin `sdlc-lite` becomes `sdlc` (folder `plugins/sdlc-lite/` becomes `plugins/sdlc/`, agent and skill prefix `sdlc-lite:` becomes `sdlc:`);
- marketplace `sdlc-lite` becomes `nonoun` in both `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` (install `sdlc@nonoun`, `context@nonoun`, `design@nonoun`, `dev-tools@nonoun`);
- session agent `conductor` becomes `factory` (`sdlc:factory`), `direct` (from T-0815) becomes `live` (`sdlc:live`), `hybrid` stays (`sdlc:hybrid`).

## Context
- The user decided on 2026-10-30: these names; marketplace `nonoun`; clean break (no aliases, no migration command; old names stop working); version 1.0.0; the `/build` skill keeps its name, which is why the direct mode is `live`, not `build`.
- Lane: solo L3, reason: a mechanical, cross-cutting rename with no design decisions left, so no planner; one verifier.
- About 192 files under `plugins/sdlc-lite/` name `sdlc-lite`. Installed-cache paths change shape from `~/.claude/plugins/cache/sdlc-lite/sdlc-lite/<version>` to `~/.claude/plugins/cache/nonoun/sdlc/<version>`: every script that builds or parses that path (for example `plugin_min.py`, the `messages-run.py` launcher in `messages.py`, `fleet_collect.py` env detection) must follow.
- Hooks key on agent types: `hooks/block-role-spawn.sh` (`sdlc-lite:conductor`), `hooks/_role.sh` (the `sdlc-lite:` prefix strip). Codex generated agents: `codex_roles.py` (`sdlc-conductor-l1.toml` becomes the factory's name), `claude_roles.py`.
- Out of scope and unchanged: the `.sdlc/` folder, `SDLC_*` environment variables, the GitHub repository name, ticket ids, this repo's own `sdlc-lite-author` agent, dated reports in `docs/reports/` (except path spans that `docs_check.py` S-6 checks in reports that opt in with `doc-type: report`: point those at `plugins/sdlc/`), closed `.NNNN-*` ticket folders, and CHANGELOG history entries.

## Do
1. `git mv plugins/sdlc-lite plugins/sdlc`, then rename every live reference: manifests (`plugin.json` names, both marketplace files), agent files (`agents/conductor.md` to `agents/factory.md`, `agents/direct.md` to `agents/live.md`), skills, hooks, scripts, adapters, checks, `AGENTS.md`/`CLAUDE.md` at the root and in the plugin, `docs/` specs, references, guides and planning (not reports), `.sdlc/config` and repo scripts that name the plugin path, and this repo's `.claude/settings.json` and `.claude/` agent files where they name the plugin.
2. Prose: "SDLC Lite" becomes "SDLC" where it names the plugin; "conductor" becomes "factory" where it names the session agent or mode (a generic word "conductor" in history stays).
3. Set the version to 1.0.0 in both plugin manifests; regenerate Claude and Codex agents.
4. Write the upgrade section of the next CHANGELOG entry as `## [Unreleased]`: uninstall `sdlc-lite@sdlc-lite`, add the `nonoun` marketplace, install `sdlc@nonoun`, change `"agent": "sdlc-lite:conductor"` to `"agent": "sdlc:factory"`, re-resolve helper script paths.

## Acceptance criteria
- `bash plugins/sdlc/scripts/check.sh` exits 0.
- `python3 scripts/check-packaging.py` exits 0.
- `git grep -n "sdlc-lite" -- plugins/ scripts/ .claude-plugin/ .agents/ AGENTS.md CLAUDE.md docs/specs docs/references docs/guides docs/planning` prints only lines that name this repository (its folder or GitHub name), the `sdlc-lite-author` agent, recorded fixtures, or dated history (CHANGELOG and updates-log entries); list each kept line in the report.
- `! git grep -q "sdlc:conductor\|sdlc:direct" -- plugins/`

## Replan
One replan (2026-10-30, conductor): the solo found that check.sh docs-repo fails on path spans in three opted-in dated reports and that criteria 3 and 4 were wrong as written. Fix: rewrite only those path spans to the new paths; criterion 3 also keeps recorded fixtures and dated history; criterion 4 is negated. The pre-existing migrate-worktrees failure (red at base 2896f0eb) is out of scope and filed separately.

## Constraints
- No behavior change beyond names and paths. No alias for an old name.
