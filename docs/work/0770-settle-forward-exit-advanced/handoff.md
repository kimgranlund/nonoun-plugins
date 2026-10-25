---
id: T-0770
title: "settle --forward exits 0 after advancing main with lanes still open"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #78 reports no longer happens (title: settle --forward exits 0 after advancing main with lanes still open).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/fanout.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #78 (quoted):

> **Observed:** `fanout.py settle <integration> --forward --force` advanced main (fast-forward plus ledger cover) and then exited 1 with `lane still open: <integration> (lanes still open into <integration>: ...)`. Callers cannot tell a successful settle from a failed one by exit code.
>
> **Root cause:** after the fast-forward, `close_lane` refuses because lanes are still open into the branch and `scripts/fanout.py:3103-3106` returns 1, the same code used for "nothing merged" elsewhere (docstring at 3038 mentions it). Not #16.
>
> **Proposed fix:** exit 0 (or a distinct code such as 3) and print `settled: main advanced; integration kept (lanes open: ...)`.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
