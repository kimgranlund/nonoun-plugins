---
id: T-0729
title: "Builders record a pre-edit red run for each (red) criterion"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
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

## Outcome
Rule 11 (redck record before the first edit) already existed but sat at the end of the list, after "implement the step". Added a First action line to `plugins/sdlc-lite/agents/builder.md` (Brief section) and regenerated the builder-L1..L5 and Codex definitions. `solo.md` already runs `specgate.py red` and `redck.py record` before the first edit (step 2), so it is unchanged.

New line: "First action: when the handoff has a `(red)` criterion, run `redck.py record` (rule 11) before any edit, a new test, generator or formatter run included; a record taken after any edit is stored as retrospective and leaves a process deviation."

Checks: `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check 7ec0d4bb` exit 0; claude_roles.py and codex_roles.py generate rerun leaves no diff.

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 7ec0d4bb698b
- Changed: see commits
- Commits: 62cb430 T-0729: builders record a pre-edit red run as their first action
- Check: 1 The source definition says it (quote the new line in the Outcome) and `python3 plugins/sdlc-lite/...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes...: pass
- Follow-up: decide: plugins/sdlc-lite/agents/builder.md:10 says to record "before any... -> notes.md
- Follow-up: note: redck.py deviations on the artifacts dir printed nothing rc=0; this... -> notes.md
