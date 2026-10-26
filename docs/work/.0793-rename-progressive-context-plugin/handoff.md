---
id: T-0793
title: "rename the progressive-context plugin to context"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0789]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
claimed_by: sdlc-lite-author 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The Progressive Context plugin installs as `context`, so the plugin name says what it owns once it also carries the context-routing and system-mapping skills (T-0790).

## Intent
- Do: rename `plugins/progressive-context/` to `plugins/context/`; set `name` to `context` in its `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` and in both marketplaces (`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`); update every live reference (`git grep -n 'progressive-context' -- ':!docs/work/.*' ':!docs/reports'`: `scripts/check-packaging.py`, `plugins/sdlc-lite/scripts/check.py`, `README.md`, `docs/README.md`, `AGENTS.md`, `docs/specs/generative-constructs/`, `docs/specs/repo-onboarding/design.md`, `docs/planning/docs-schema/design.md`); bump the plugin version and add upgrade notes.
- Non-goals: renaming the `progressive-context` skill inside the plugin (it becomes `context:progressive-context`); renaming the `docs/specs/generative-constructs/progressive-context-*.md` files, which name the method, not the plugin; editing closed tickets or dated reports.
- Done when: `python3 scripts/check-packaging.py` passes, `python3 plugins/sdlc-lite/scripts/check.py` exits 0, the grep above lists only method-name uses (each one kept on purpose), and `git diff --check` exits 0.

## Context
User decision 2026-10-25: "rename `progressive-context` plugin to `context`". A plugin rename changes its install id: users with `progressive-context@sdlc-lite` enabled must install `context@sdlc-lite` and remove the old entry, so the upgrade note says so. Read `plugins/progressive-context/AGENTS.md` first. T-0790 moves more skills into this plugin after the rename.

## Constraints
The plugin's skill behavior does not change. Marketplace parity between the Claude and Codex catalogs holds.

## Outcome
`plugins/progressive-context/` is now `plugins/context/` (`git mv`), both manifests say `name: context`, version 0.2.0, and the Codex display name is `Context`. Both marketplaces, `scripts/check-packaging.py` (catalog set, link-check path, and an `ENTRY_SKILL` map because the entry skill keeps its name), `plugins/sdlc-lite/scripts/check.py` (sibling skills root), `AGENTS.md`, `README.md`, `HARNESS-NOTES.md`, and the spec and planning links now point at `context`. Upgrade notes are in the new `plugins/context/CHANGELOG.md`; the root `CHANGELOG.md` links to it. Eight links in the dated `docs/reports/workflow-stage-pilot/` records still point at the old path and are listed in `docs/reports/broken-links-allowlist.md` instead of edited.

Remaining `progressive-context` grep hits, each kept on purpose:
- Skill name and its uses: `plugins/context/skills/progressive-context/` (SKILL.md `name:`, `performance-contract.json` `skillId`), `$progressive-context` in `.codex-plugin/plugin.json`, `README.md`, `HARNESS-NOTES.md`, `/context:progressive-context`, `plugins/context/AGENTS.md` skill path, the `ENTRY_SKILL` map in `scripts/check-packaging.py`. Non-goal: the skill is not renamed.
- Method-name spec files `docs/specs/generative-constructs/progressive-context-*.md` and every link or mention of them (`docs/README.md`, `docs/specs/generative-constructs/AGENTS.md` and `README.md`, the gap analysis, `docs/planning/docs-schema/design.md:162`, `docs/planning/repo-onboarding/reorganization.md`). Non-goal.
- Dated report `reports/progressive-context-gap-analysis-review.md` and its mentions (`docs/README.md:44`, `docs/layout.md:100`).
- History: gap analysis line 9 (the plugin as analyzed at 0.1.2), spec decision line 270 and status line 290 (now say renamed), the proposed package tree at spec line 188 (future layout of the skill).
- Ticket ids and folder names in `.sdlc/AGENTS.md` and `docs/work/ROADMAP.md`; `docs/other/claude-response.md` (out of scope, names the skill folder); the upgrade note in `plugins/context/CHANGELOG.md` (names the old install id).

Checks: `python3 scripts/check-packaging.py` exit 0, `python3 plugins/sdlc-lite/scripts/check.py` exit 0, `git diff --check` exit 0.

## Acceptance criteria
- `python3 scripts/check-packaging.py` exits 0.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- `git diff --check` exits 0.
- `test ! -e plugins/progressive-context && test -f plugins/context/skills/progressive-context/SKILL.md` exits 0.
- `grep -q '"name": "context"' plugins/context/.claude-plugin/plugin.json && grep -q '"version": "0.2.0"' plugins/context/.codex-plugin/plugin.json` exits 0.
- `! git grep -n -e 'progressive-context@' -e '/progressive-context:' -e 'plugins/progressive-context' -- ':!docs/work' ':!docs/reports' ':!plugins/context/CHANGELOG.md'` exits 0.

## Outcome

2026-10-25 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: none · base: none
- Changed: see commits
- Commits: none
- Check: 1 `python3 scripts/check-packaging.py` exits 0: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass
- Check: 3 `git diff --check` exits 0: pass
- Check: 4 old folder gone, new SKILL.md present: pass
- Check: 5 manifest name and version: pass
- Check: 6 no old install id, invocation or path outside work, reports and the CHANGELOG: pass
- Check: 7 Intent (Do): pass
- Check: 8 Intent (Done when, remaining grep hits are method-name uses): pass
- Check: 9 Solo's added criteria faithful to Intent: pass
- Follow-up: note: .github/workflows/release-check.yml names no plugin path, so CI... -> notes.md
