---
id: T-0888
title: "ui-geometry: an unknown --preset fails with a raw ENOENT"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
An unknown `--preset` name gets a clear error naming the built-in presets, not a raw ENOENT.

## Intent
- Do: in `loadPreset` (`plugins/design/skills/ui-geometry/scripts/derive.mjs`), when the name is not a built-in preset and no file exists at that path, exit 2 with `unknown preset "<name>": use one of <built-ins> or a path to a preset JSON`, adding a "did you mean" hint as `validatePreset` already does for keys.
- Non-goals: other error messages.
- Done when: the criteria below hold.

## Context
- Reproduced 2026-11-25: `node scripts/derive.mjs --preset nosuch` prints `ENOENT: no such file or directory, open 'nosuch'`. This predates PR #104.
- Tests: `node --test scripts/*.test.mjs` in the skill folder. Its `plugins/design/AGENTS.md` row records differences from the MacBook source; add this one.

## Acceptance criteria
- `node scripts/derive.mjs --preset nosuch` exits 2 and its stderr names `affine` and `ladder`; `--preset afine` suggests `affine`.
- A test covers it, and `node --test scripts/*.test.mjs` passes.
- A valid preset path still loads.

## Constraints
- None.
