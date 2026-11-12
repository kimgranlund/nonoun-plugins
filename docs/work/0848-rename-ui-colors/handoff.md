---
id: T-0848
title: "Rename the design skill hct-palettes to ui-colors"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The design skill `hct-palettes` is named `ui-colors`, the first of the ui-* set (`ui-geometry`, `ui-colors`, `ui-materials`, `ui-interaction`, `ui-kit`; user decision 2026-11-12, for the release after 1.0.6).

## Context
- Folder `plugins/design/skills/hct-palettes/`; 19 references under `plugins/` (SKILL.md `name:`, `agents/openai.yaml`, `evals/triggers.json`, `references/{build-manifest.json,engine.md,system.md}`, `scripts/generate.cjs`, `scripts/system/runtime.json`), plus `plugins/design/AGENTS.md`, `docs/reports/broken-links-allowlist.md` and the design manifests' descriptions.
- The MacBook source `/Volumes/kimba/.claude/skills/hct-palettes/` is read-only; never write there. The user is writing `ui-materials`, `ui-interaction` and `ui-kit` separately.
- Keep CHANGELOG history and dated reports as they are; add a Changed line under `[Unreleased]`.

## Acceptance criteria
- `test -d plugins/design/skills/ui-colors -a ! -e plugins/design/skills/hct-palettes` exits 0, and SKILL.md says `name: ui-colors`.
- `git grep -n "hct-palettes" -- plugins docs/reports/broken-links-allowlist.md ':!*CHANGELOG.md'` prints only lines the report names as kept on purpose (for example the HCT colour model itself).
- `cd plugins/design/skills/ui-colors && node scripts/check.mjs` exits 0, `python3 plugins/sdlc/scripts/check.py` and `python3 scripts/check-packaging.py` exit 0, and `git diff --check` is clean.

## Outcome
