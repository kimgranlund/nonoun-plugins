---
id: T-0766
title: "An inherited red from an earlier step of the same lane routes back into the task"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #74 reports no longer happens (title: An inherited red from an earlier step of the same lane routes back into the task).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/steps.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #74 (quoted):

> **Observed:** step 5's builder reported `inherited red: historical-browser-verification.test.ts ...` and `steps.py next` printed `inherited`, which the conductor rules route to "fix main first / ask the user". The red was caused by step 3 of the same lane (it renamed `.mjs` files to `.ts` while a JSON evidence list still named the `.mjs` paths). Main was green.
>
> **Root cause:** builder rule 8 compares only against `$SDLC_BASE_SHA`, the HEAD the step's build started from (`agents/builder.md:25-26`, same in every level variant); nothing checks the lane's merge-base with its target. `steps.py next` trusts the Status line (`scripts/steps.py:3233-3236`). Guidance: `skills/fanout/SKILL.md:72`, `agents/conductor.md:46`, step-rules item 7.
>
> **Proposed fix:** the builder also runs the failing check at the lane's merge-base with its target branch; green there means a distinct `lane red` status that routes back into the task (rebuild or replan). Keep "fix main first" only when main itself is red.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `steps.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
