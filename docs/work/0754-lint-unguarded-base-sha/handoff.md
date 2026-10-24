---
id: T-0754
title: "steps.py lint flags a criterion that names SDLC_BASE_SHA without a guard"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A plan or handoff criterion that names `$SDLC_BASE_SHA` cannot pass vacuously when the variable is unset: `steps.py lint` refuses a criterion that names it without a `${SDLC_BASE_SHA:?}` guard or an `export SDLC_BASE_SHA=` in the same criterion.

## Intent
- Do: add the lint rule in `plugins/sdlc-lite/scripts/steps.py` next to the existing `SDLC_BASE_SHA` case (about line 6084), with a message that shows the guarded form. Update the planner's criterion guidance in `plugins/sdlc-lite/agents/planner.md` and `skills/handoff-format/SKILL.md` only if they show an unguarded example (keep the merge-step block identical in both; `check.py` compares them), then regenerate agents.
- Non-goals: rewriting existing closed handoffs.
- Done when: the criteria pass.

## Context
T-0735 verifier (2026-10-24): with the variable unset, `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- plugins 2>/dev/null)"` exits 0 (vacuous pass) while the bare `git diff` exits 128 `bad revision ''`. Roles launched by `dispatch.py prepare` have no SDLC_BASE_SHA; T-0735 added only a brief line telling them to export it.

## Acceptance criteria
1. A `steps.py` selftest case: lint refuses a criterion with an unguarded `$SDLC_BASE_SHA` and accepts the `${SDLC_BASE_SHA:?}` and `export SDLC_BASE_SHA=<sha> &&` forms; with the rule removed the refusal case fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/steps.py lint` passes on every open handoff under `docs/work/` (fix any open one it flags).
3. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
