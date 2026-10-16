---
id: T-0602
title: "check.py spec gate order check matches the run.sh header comment"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`check.py` proves `specgate.py check` runs before `exec run_lifecycle.py` in `scripts/run.sh` by the command line, not by the first line that merely mentions it.

## Repro
1. `grep -n 'specgate.py check' plugins/sdlc-lite/scripts/run.sh` lists the header comment at line 96 before the command at line 416.
2. `plugins/sdlc-lite/scripts/check.py` (`spec_gate_order_bad`, about line 689) takes the first matching line, so it passes on the comment.

## Expected
The order check anchors on the command line (the `if ! ... specgate.py check` call), and a negative control that moves only the command below the `exec` line goes red.

## Actual
Moving the command below the `exec` line while the comment stays above leaves the check green.

## Context
Found by the T-0210 verifier (2026-10-04); still true on main at T-0573. Source note: `.sdlc/notes.md` T-0210 fix-now.

## Constraints
Touch `plugins/sdlc-lite/scripts/check.py` only. The failing negative control lands with the fix.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 on the fixed tree and exits 1 on a copy of `run.sh` with the command moved below the `exec` line.
