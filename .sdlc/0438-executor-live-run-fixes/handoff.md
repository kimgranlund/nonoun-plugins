---
id: T-0438
title: "Plan-doc executor: close the live-run gaps (host base, stop record, recover scope, integration branch, verifier record, ticket fields)"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
claimed_by: claude 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A smaller driver runs a plan doc to done with no maintainer hand-fixes, in the cases the 2026-10-11 live run and rehearsal hit.

## Intent
- Do: fix items 2 to 8 of `docs/reports/2026-10-11-plan-doc-live-run.md` (rehearsal section), smallest change each: (2) `fanout.py prep` prompt tells the solo to first run `git merge --ff-only <base sha>` so a claim commit not on origin is visible, with a selftest; (3) `plan_done.py` gains a documented resume that clears a stop record (or the run rules name `rm` of `plan-state.json` as the maintainer step); (4) `dispatch.py recover` run by the driver is scoped to the plan's open ticket folders; (5) `fanout.py land` or the run rules delete `fanout/<date>` after a non-ff merge; (6) `plan_done.py` or the run rules read a verifier record from the landed lane; (7) `plan_check.py plan` accepts any `[A-Z]-\d+` measure id in Done when and the format doc says a measure prints one bare number; (8) the run rules name the ticket fields to set from a step (`size`, `status: ready`, `verify`).
- Non-goals: model or effort rows, a Haiku row, the crash drill (separate run).
- Done when: each item has a selftest case that fails before and passes after; `check.sh` exits 0; one more rehearsal plan runs to `plan done` with no hand step.

## Context
Evidence: `docs/reports/2026-10-11-plan-doc-live-run.md`. Executor files: `plugins/sdlc-lite/scripts/{plan_check,plan_doc,plan_done,fanout,dispatch}.py`, `plugins/sdlc-lite/skills/run-plan/`. Host fact: sub-agent worktrees are made from origin/main (observed a9d42334 after the push), not local HEAD. If item 2 is judged a host limit, the fallback is a run rule that pushes the claim, which needs the maintainer's authorization.

## Constraints
No push, tag or publish by any role. Keep changes small; one lane, one ticket, split by item only if a verifier fails.
