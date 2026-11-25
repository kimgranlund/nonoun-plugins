---
id: T-0887
title: "ui-geometry: --density does nothing under the affine preset"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-25
claimed_by: nonoun-author 2026-11-25
branch: lane/T-0887-t0887
worktree: ../sdlc-lite.worktrees/T-0887-t0887
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`derive.mjs` tells the user when `--density` has no effect, instead of printing it in the header as if it applied.

## Intent
- Do: under a preset whose inset is one line (`affine`, the default), a `--density` other than `default` prints a one-line note on stderr that density is a scope with another n there, and the header omits or marks it.
- Non-goals: making density a dial under `affine` (the model says it is not: `scripts/derive.mjs` line 88).
- Done when: the criteria below hold.

## Context
- Reproduced 2026-11-25: `node scripts/derive.mjs --n 16 --density loose` and `--density compact` differ only in the header line (`density loose` vs `density compact`); `--json` output is identical.
- Skill: `plugins/design/skills/ui-geometry/` (`scripts/derive.mjs`, `scripts/*.test.mjs`, run with `node --test scripts/*.test.mjs`).

## Acceptance criteria
- `node scripts/derive.mjs --n 16 --density loose 2>&1 >/dev/null` prints the note; `--preset ladder --density loose` prints none.
- A test in a new file `scripts/density.test.mjs` covers both, and `node --test scripts/*.test.mjs` passes.
- stdout for `--preset ladder` is byte-identical to `main`.

## Constraints
- T-0888 runs in a parallel lane on the same `derive.mjs`: change only the function you need, put your test only in `scripts/density.test.mjs`, and do not edit `plugins/design/AGENTS.md` or any CHANGELOG (the conductor records both at landing).
- Output of unit presets unchanged.
