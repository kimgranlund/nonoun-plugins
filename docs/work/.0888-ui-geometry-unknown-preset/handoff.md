---
id: T-0888
title: "ui-geometry: an unknown --preset fails with a raw ENOENT"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
claimed_by: nonoun-author 2026-11-25
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
- Tests: `node --test scripts/*.test.mjs` in the skill folder.

## Acceptance criteria
- `node scripts/derive.mjs --preset nosuch` exits 2 and its stderr names `affine` and `ladder`; `--preset afine` suggests `affine`.
- A test in a new file `scripts/preset.test.mjs` covers it, and `node --test scripts/*.test.mjs` passes.
- A valid preset path still loads.

## Constraints
- T-0887 runs in a parallel lane on the same `derive.mjs`: change only the function you need, put your test only in `scripts/preset.test.mjs`, and do not edit `plugins/design/AGENTS.md` or any CHANGELOG (the conductor records both at landing).
- None.

## Outcome

2026-11-25 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L1 (opus) · base: 708a30071c7c
- Changed: see commits
- Commits: 9ed6d80 T-0888: ui-geometry unknown --preset exits 2 with built-ins and a hint; b66a0a5 T-0888: record lane T-0888-t0888
- Check: 1 `--preset nosuch` exits 2 naming `affine` and `ladder`; `--preset afine` suggests `affine`: pass
- Check: 2 test in new `scripts/preset.test.mjs`, `node --test scripts/*.test.mjs` passes: pass
- Check: 3 a valid preset path still loads: pass
- Follow-up: note: redck.py deviations printed no process deviation lines; no red... -> notes.md
