---
id: T-0793
title: "rename the progressive-context plugin to context"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0789]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
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
