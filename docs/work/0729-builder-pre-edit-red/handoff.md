---
id: T-0729
title: "Builders record a pre-edit red run for each (red) criterion"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A builder records a pre-edit red run for each `(red)` criterion before editing, so `redck` stops reporting all-retrospective steps.

## Intent
- Do: Make the pre-edit red run a required first action in `plugins/sdlc-lite/agents/builder.md` (and `solo.md` if it has red criteria), naming where to record it so `redck.py` sees it; regenerate definitions.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #64 (quoted):

> **Observed**: `dispatch.py advance` printed `redck: process deviation: red-checkpoint: retrospective ... 5 of 5 (red) criteria without a pre-edit red control` (T-0068 step 1) and `6 of 6` (T-0073 step 1). Verifiers passed anyway.
>
> **Expected**: the builder brief makes the pre-edit red run a required first action (record the failing output before editing), or advance treats an all-retrospective step as a verifier note to re-run red at base.
>
> **Evidence**: advance output for `.sdlc/runtime/tasks/0068-ui-component-skins/step-1` and `.../0073-ui-radius-pin/step-1`.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. The source definition says it (quote the new line in the Outcome) and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` plus `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` leave no diff after your commit.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
