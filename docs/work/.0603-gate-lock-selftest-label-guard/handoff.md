---
id: T-0603
title: "gate_lock selftest status checks never run: label compared to real, controls pass real0"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-17
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The `case_cap` and `case_livegroup` status assertions in the `gate_lock.py` selftest run, and a mutant that breaks `gate_lock.py status` goes red.

## Repro
1. `grep -n "label == 'real'" plugins/sdlc-lite/scripts/gate_lock.py` finds the guards at lines 1146 and 1249.
2. The controls loop (about line 1480) calls `case(script, base, f'real{i}')`, so the label is `real0`, `real1`, ... and the guarded `status` checks never run.

## Expected
The guard matches the labels the loop passes (for example `label.startswith('real')`), and the status assertions execute.

## Actual
Both blocks are skipped on every run.

## Context
Found while verifying T-0497 (2026-10-12); predates it and is still true on main at T-0573. Source note: `.sdlc/notes.md` T-0497 decide.

## Constraints
Touch `plugins/sdlc-lite/scripts/gate_lock.py` selftest only. Run `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` through `gate_lock.py run`; show one observed-red mutant for the status output.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 and the `status` assertions in `case_cap` and `case_livegroup` execute.

## Outcome

2026-10-17 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full; verifier notes: note: no builder-*.md report is in the artifacts dir, and `redck.py deviations` printed no lines. The criterion is not marked (red), and the base-vs-built mutant runs above supply the red evidence.) · verifier: verifier-L2 (opus) · base: 4973e6a6bed7
- Changed: see commits
- Commits: 25eb0e0 T-0603: gate_lock selftest status checks never run: label compared to real, controls pass real0
- Check: 1 `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 and the `status` assertions in ...: pass
