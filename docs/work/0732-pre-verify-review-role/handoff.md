---
id: T-0732
title: "Project hook for a required review role between build and verify"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py advance` and `steps.py next` route a build through a project-declared review role (for example `pre_verify_role: ui-designer L1` with `pre_verify_paths:`) before the verifier when the diff touches those paths.

## Intent
- Do: Design and build per the issue; proposed for the maintainer to schedule.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #61 (quoted):

> ## Idea
> Some repos require a review role between build and verify. ui-kit-neue's AGENTS.md says that a recipe or token change "gets a ui-designer review (mode: review) of its recipe before the verifier runs".
>
> `dispatch.py advance` on an L2 solo, and `steps.py next` after a builder, go straight to the verifier. So the conductor has to route around `advance` by hand on every such ticket: plain `record`, write a review handoff, prepare the ui-designer, record it, then prepare the verifier. Tonight that happened about 10 times.
>
> ## Proposal
> A project config hook, for example `pre_verify_role: ui-designer L1` plus `pre_verify_paths: packages/styles/src/** packages/tokens/src/**` in `.sdlc/config`:
> - `advance` and `steps.py next` print `review` and prepare that role with a generated review handoff when the diff touches those paths;
> - a `changes-required` verdict routes back to the builder or solo;
> - a `pass` routes to the verifier.
>
> ## Evidence
> ui-kit-neue G6 to G9, roughly 10 recipe or token tickets each routed by hand.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `dispatch.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
