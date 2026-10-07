---
id: T-0222
title: "fanout solo lane closes: write the ## Skipped entries the T-0219 skips guard needs"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A fanout solo lane closes its tickets: after the T-0219 skips guard, `fanout.py` closes a solo ticket with `tickets.py close --reason`, and the guard must accept it.

## Repro
1. On main at 01559a6 (T-0221 merged, T-0219 guard live), in a throwaway repo run `fanout.py run x=T-0001,T-0002` with size S tickets and no `--driver`.
2. Each lane delivers its first ticket; the close is refused.

## Expected
Every solo ticket merges and closes.

## Actual
`merged, close refused`: `steps.py lane` wrote only `lane: solo` to skips.md, and the guard demanded `## Skipped` entries for the planner and filer that nothing wrote. Reproduced twice by the 0.20.6 release fact-check. The T-0221 selftest always passed `--driver`, and the live run predates T-0219, so nothing caught it.

## Context
Found by the 0.20.6 release fact-check (coordinator message). Cause: T-0221 added the solo path without the Skipped entries T-0219 requires.

## Constraints
The T-0219 guard stays unchanged. A selftest must run the real lane decision and the real close with a negative control.

Done: `fanout.py` has `write_solo_skips` (called when a solo lane starts, before the close); selftest case 16 runs two solo tickets through the real `steps.py lane`, the default driver (a `claude` shim stands in for the model) and the real `tickets.py close`, and its negative control, with the write off, is refused. Live rerun: four lanes (three S, one M) all merged and closed, hidden check 24/24 (`docs/reports/fanout-solo-live-run.md`, addendum). Files: `plugins/sdlc-lite/scripts/fanout.py`, `plugins/sdlc-lite/skills/fanout/SKILL.md`, `docs/references/sdlc-internals.md`, `docs/reports/fanout-solo-live-run*`. Verifier: independent L3 (Fable) passed 7 of 7. Merged at 51df377.

## Closed

2026-10-04: Fixed: fanout.py writes the planner and filer ## Skipped entries when a solo lane starts, so the T-0219 skips guard accepts the close by reason; guard unchanged. Selftest case 16 runs the real lane decision and real close with a negative control; live rerun of 4 lanes closed all four (hidden check 24/24); skill lane count and overlap-limit docs fixed. Independent L3 verifier passed 7 of 7.
