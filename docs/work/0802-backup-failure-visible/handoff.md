---
id: T-0802
title: "a failed background backup push is silent after T-0800"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
claimed_by: sdlc-lite-author 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A failed background backup push is reported: the next `lanes.py finish` (and `lanes.py finish` itself when the push already ended) reads the previous push's `exit <code>` from `<git common dir>/sdlc-backup.log` and prints a `backup: previous push failed (exit N), see <log>` line with a nonzero exit code.

## Repro
1. Make the backup remote reject the push (for example a pre-push hook that exits 1).
2. `lanes.py finish <lane> --backup origin/wip/main`, then a second `finish`.

## Expected
The second finish reports the failed push and exits nonzero after landing.

## Actual
T-0800 verifier, 2026-10-28 (`decide:` at `plugins/sdlc-lite/scripts/lanes.py:1283`): before T-0800 a failed push stopped finish with exit 1 and `backup: stopped`; now the only trace is `exit <code>` at the end of `sdlc-backup.log`, and nothing reads that log. The backup is the only off-machine copy of main between releases.

## Context
`plugins/sdlc-lite/scripts/lanes.py` finish (`--backup`, around line 1283). Decision: the user chose a fix ticket on 2026-10-28.

## Acceptance criteria
1. A lanes selftest case: after a background push that exits 1, the next finish prints `backup: previous push failed` and exits nonzero; with the fix reverted it does not (state the FAIL line).
2. lanes selftest through gate_lock exits 0, `check.py` exits 0.

## Constraints
The failing test lands before or with the fix. The push stays in the background.
