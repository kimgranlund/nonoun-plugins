---
id: T-0602
title: "check.py spec gate order check matches the run.sh header comment"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0602-t0602
worktree: ../sdlc-lite.worktrees/T-0602-t0602
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

## Outcome

2026-10-15 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full; verifier notes: note: .sdlc/runtime/tasks/0602-check-specgate-order-comment has no builder-*.md report, so builder claims could not be read; the verdict rests on the runs above. | note: the handoff Repro calls run.sh line 416 the command; it is the refusal `echo`, and the command is run.sh:414. The fix anchors on 414 correctly. | note: cleanup of the scratch dirs /Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/tmp/0602-verifier-L2 and /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0602-verifier-L2 was denied by the permission layer; both git worktrees were removed with `git worktree remove --force`, so only empty parent or probe files remain.) · verifier: verifier-L2 (opus) · base: 639a85601b88
- Changed: see commits
- Commits: 5c482fb T-0602: check.py spec gate order check matches the run.sh header comment; 42cde72 T-0602: record lane T-0602-t0602
- Check: 1 `python3 plugins/sdlc-lite/scripts/check.py` exits 0 on the fixed tree and exits 1 on a copy of `...: pass
