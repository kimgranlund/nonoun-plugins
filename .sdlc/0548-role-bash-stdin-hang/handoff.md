---
id: T-0548
title: "A role's Bash call that reads stdin (bare cat > file) hangs the run with no timeout"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A role's Bash call that waits on stdin cannot stall a run for long: the call fails fast, or the run reports the stall, instead of hanging silently.

## Repro
1. In a headless role run (`claude -p`, fanout lane), have the role run `cat > /tmp/x; python3 - <<'EOF' ... EOF`.
2. `cat` reads the inherited stdin, which never closes, so the run waits with no output.

## Expected
The command gets a closed stdin (`< /dev/null`) or a timeout, or a watchdog reports the run stalled.

## Actual
T-0543 step 2 builder (wave 70, 2026-10-14) sat 39 minutes on `cat > /tmp/x` (pid 99957) until the maintainer killed it; the transcript showed no writes from 04:43 to 05:23.

## Context
Builder L4 sub-agent of the conductor in `.worktrees/fanout70/d`. Guess: headless `claude -p` lanes run with an open stdin pipe; a fix might start lane drivers with `stdin=DEVNULL` in `fanout.py`/`solo_run.py`, or add a stall line to the lane monitor.

## Constraints
The failing test lands before or with the fix, never after.
