---
id: T-0771
title: "board.py renders a done ticket as closed and lets a later verifier pass win"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #79 reports no longer happens (title: board.py renders a done ticket as closed and lets a later verifier pass win).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/board.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #79 (quoted):

> **Observed:** a ticket closed after all 6 steps passed verification rendered as `85% (5/6) · 🔴1` on main and integration.
>
> **Root cause:** (a) `step_row` checks the builder's `inherited red` Status (`scripts/board.py:149`) before the verifier verdict (`:151`), so a later passing verifier on that step is ignored; `steps.py next` has the same ordering (`steps.py:3233`). (b) a `done` ticket renders closed only for a solo lane (`board.py:260`) or with no steps (`:270`).
>
> **Proposed fix:** render `status: done` as closed regardless of lane, and let a verifier pass that comes after an inherited-red build win.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `board.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
