---
id: T-0802
title: "a failed background backup push is silent after T-0800"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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

## Outcome
`lanes.py finish` now reads the last line of `<git common dir>/sdlc-backup.log` before its own steps (and before its own push rewrites the log). When it is `exit N` with N nonzero, finish prints `backup: previous push failed (exit N), see <log>` after its steps and returns 1 at least. Still-running pushes (no `exit` line) and `exit 0` print nothing. The push stays in the background. A failed log stays reported until a later push rewrites it.

Files: `plugins/sdlc-lite/scripts/lanes.py` (`backup_log`, `failed_backup`, `finish` wrapper over `finish_steps`, docstring step 8, selftest case `finish backup failed`).

Checks:
- Red first, fix absent: `FAIL: finish backup failed: finish bgfail: want a nonzero exit and `backup: previous push failed (exit 1), see .../.git/sdlc-backup.log`, got 0: backup: none (no --backup)`.
- Fix in: `python3 plugins/sdlc-lite/scripts/lanes.py selftest` through gate_lock exit 0 (90 ok, includes `ok: finish backup failed`).
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `git diff --check` exit 0.

## Outcome

2026-10-28 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: cf9b0cac8dda
- Changed: see commits
- Commits: 4bd23d9 T-0802: a failed background backup push is reported by the next finish
- Check: 1 A lanes selftest case: after a background push that exits 1, the next finish prints `backup: prev...: pass
- Check: 2 lanes selftest through gate_lock exits 0, `check.py` exits 0: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/lanes.py:1338 the Goal's parenthetical... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/lanes.py:1338 a failed log keeps every... -> notes.md
