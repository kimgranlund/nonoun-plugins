---
id: T-0890
title: "ui-colors: a pinned step 9 drifts in the contrast modes"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-26
claimed_by: nonoun-author 2026-11-26
branch: lane/T-0890-t0890
worktree: ../sdlc-lite.worktrees/T-0890-t0890
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A pinned step 9 (role anchor or `familyAnchors`) stays recognisably the pinned colour in the contrast modes, and the run reports any move it makes there.

## Intent
- Do: in a contrast mode, when a pinned step 9 fails that mode's raised solid floor, move it the least visible distance (try the other label first, then the smallest lightness change at the anchor's hue), and record the per-mode move in `anchorReport`; add a check and a negative control; document it in `references/system.md` (Anchors).
- Non-goals: light, dark and dim (the pin already holds there at ΔE 0); unpinned families; the contrast-mode thresholds themselves.
- (gap: whether a pin may break the contrast floor instead of moving; default: it never does, the floor wins.)
- Done when: the criteria below hold.

## Repro
1. From a clean checkout of `main`, in `plugins/design/skills/ui-colors`, write `drift.json`: `{"settings":{"hueSet":"radix"},"compare":"radix","familyAnchors":{"orange":{"value":"#f76b15","dark":"#f76b15"}}}`.
2. `node scripts/system.mjs --request drift.json --out <new dir>` (exit 0).
3. Read `modes.<id>.radix.families.orange.steps[8]` and the orange step 9 hex in `system.json` for each mode.

## Expected
Orange step 9 stays `#f76b15`, or near it, in every mode where it clears the floor; where it cannot, it moves the least visible distance and `anchorReport` says so per mode.

## Actual
Measured 2026-11-26 on `main` at `bfacc404`:

| Mode | Step 9 | ΔE to pin (OKLab ×100) | ΔL |
|---|---|---|---|
| light | `#f76b15` | 0 | 0 |
| dark | `#f76b15` | 0 | 0 |
| dim | `#f76b15` | 0 | 0 |
| light-contrast | `#ef6300` | 2.35 | -2.35 |
| dark-contrast | `#832a00` | 28.11 | -27.55 |

The T-0885 verifier saw the same with teal: ΔE 1.49 in light-contrast and 26.85 in dark-contrast. The brand orange turns brown in dark-contrast, and `anchorReport` does not record that move.

## Context
- Found by the T-0885 solo and verifier (`compare: "radix"` made the drift visible). `references/system.md` › Reports › Radix comparison currently notes that contrast modes re-solve.
- Guess [U]: the contrast modes add 15 Lc to the solid floor, and the solve keeps the light label and darkens step 9 to clear it, instead of trying the dark label at the pinned value.
- Skill: `plugins/design/skills/ui-colors/` (`scripts/system.mjs`, `scripts/check.mjs`, `references/system.md`). Add the change to the ui-colors row in `plugins/design/AGENTS.md` (differences from the MacBook source). Do not edit any CHANGELOG.

## Acceptance criteria
- With the repro request, orange step 9 in `dark-contrast` is within ΔE 10 of `#f76b15`, or `anchorReport` records for that mode the move and the floor that forced it; a new `check.mjs` check shows which.
- A negative control that restores the current placement fails that check.
- `node scripts/check.mjs` reports every check passing and every control biting; a `{}` request's output is byte-identical to `main`.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
The failing check lands before or with the fix, never after.

## Outcome

2026-11-26 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 7f132cb88c75
- Changed: see commits
- Commits: 41fd445 T-0890: ui-colors: a pinned step 9 drifts in the contrast modes; b2c122f T-0890: record lane T-0890-t0890
- Check: 1 Orange step 9 in dark-contrast within ΔE 10 of the pin, or anchorReport records the move and the ...: pass
- Check: 2 A negative control that restores the current placement fails that check: pass
- Check: 3 `node scripts/check.mjs` all checks pass, all controls bite; `{}` output byte-identical to main: pass
- Check: 4 `python3 scripts/check-packaging.py` exits 0 and `git diff --check` clean: pass
- Follow-up: note: plugins/design/skills/ui-colors/references/system.md:494 says "Then... -> notes.md
- Follow-up: note: the dark-contrast fix lands orange lighter #ffa16e, ΔE 12.86, not... -> notes.md
