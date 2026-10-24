---
id: T-0755
title: "steps.py next and plan_done read step records from the tree that owns them"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A /chain step run with `dispatch.py prepare --tree <lane>` advances: `steps.py next`, `resume` and `plan_done.py` read the step's builder and verifier records from the tree that owns them (the lane twin, per the Owner trees table), the same place `dispatch.py record` now writes them (T-0750).

## Intent
- Do: route `steps.records_of` and `step_handoff`, the `plan_done.py` reads, and `dispatch.py status` (T-0750 verifier: from main it printed `no attempts` while the lane twin held the running verifier) through `wtroot.owner_tree('records', ...)` the way `steps.base_sha` already does (`steps.owned`, T-0752). Keep the current behaviour for a task with no lane.
- Non-goals: other kinds; other dispatch.py commands.
- Done when: the criteria pass.

## Context
T-0750 (2026-10-24) moved records, base-sha and end-sha for a ticket with a lane into the lane twin, including `prepare --tree <lane>` from the primary checkout (#55). T-0752 left `steps.records_of` and `step_handoff` reading the tree of the dir they are given, as a deliberate exception, so `steps.py next` run from primary would not see a verdict recorded in the lane.

## Acceptance criteria
1. A `steps.py` selftest case: a builder and verifier result recorded in the lane twin for a primary task dir with a lane record; `steps.py next <primary task dir>` reports the step done; with the helper call bypassed it fails (state the FAIL line). Same for `plan_done.py` if it reads records itself, and for `dispatch.py status <primary task dir>` listing the lane twin's attempt.
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 (and `plan_done.py selftest` if it has one, and `dispatch.py selftest`), `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- `steps.records_of` (reads only) now reads the records dir in the checkout that owns `records` for the ticket (`steps.owned`, the same `wtroot.owner_tree` route as `base_sha`) when that twin holds records, else the tree of the dir given (unchanged for a task with no lane). `step_handoff` also looks at the same place in the ticket's other trees (`steps.tree_twins`, `wtroot.owner_trees`), so a lane twin step dir finds a step handoff written in primary. `create=True` writes are unchanged.
- `plan_done.verifier_problem` reads the ticket's records through `steps.records_of`.
- `dispatch.py status` on a handoff or step dir reads `dispatch.owned_records` when that holds attempts; `recover` is unchanged.
- Docs: `docs/references/sdlc-internals.md` (the T-0752 note and the `records` row of the Owner trees table) and the dispatch.py docstring.
- New selftest cases, each with an in-suite or one-off negative control. With `steps.owned` returning its input and `owned_records` replaced by the local records dir:
  - steps: `FAIL owner tree (T-0755): next on the main step dir reads the builder and verifier results in the lane twin -> done` (the T-0752 swap case fails too, as expected)
  - plan_done: `FAIL: plan_done: owner tree (T-0755): the verifier pass in the ticket's lane twin is read, prints plan done`
  - dispatch: `FAIL: owner tree (T-0755): status on a main-checkout task dir lists the attempt in its ticket's lane twin, got 'no attempts in .../rr/.sdlc/runtime/tasks/t755'`
- Checks: steps, plan_done and dispatch selftests (through gate_lock) exit 0; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 02ccf3a8` exit 0.

## Outcome

2026-10-24 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: cb628a7a383d
- Changed: see commits
- Commits: f720dd8 T-0755: steps.py next and plan_done read step records from the tree that owns them
- Check: 1 steps selftest case (lane twin records, `next` on the primary step dir reports done; bypass fails...: pass
- Check: 2 gates: pass
- Check: 3 Own flow unchanged: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/steps.py:581: note: records_of is... -> notes.md
