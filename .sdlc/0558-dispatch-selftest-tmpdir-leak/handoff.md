---
id: T-0558
title: "dispatch.py selftest accept-all controls fail when an unmarked folder sits under TMPDIR/sdlc-lite"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
branch: lane/T-0558-w76-0558
worktree: .claude/worktrees/T-0558-w76-0558
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py selftest` passes regardless of what other runs left under `$TMPDIR/sdlc-lite/`.

## Repro
1. Leave an unmarked folder under `$TMPDIR/sdlc-lite/` (any scratch without `.owner.json`).
2. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`.

## Expected
PASS: the selftest's fixtures use their own scratch root.

## Actual
The 3 accept-all negative controls fail because `record` prints `unmarked:` for the foreign folder (T-0545 builder, 2026-10-14; same on unchanged HEAD). `check.sh` went red once for this reason.

## Context
T-0550 made the sweep cover every repo's scratch under `$TMPDIR/sdlc-lite/`. Guess: the selftest should point the scratch root at a private temp dir.

## Constraints
The failing test lands before or with the fix. Target 0.23.1.
