---
id: T-0728
title: "Planner runs each new-behavior criterion red at base before returning"
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
A planner result whose new-behavior criteria are already green at base is caught before it reaches review: the planner definition makes the red-at-base run a required final check, and `steps.py lint` (or the planner's own check command) flags criteria the planner did not record as red.

## Intent
- Do: Tighten `plugins/sdlc-lite/agents/planner.md` rule 1 into a required last action (run every `(red)` / new-behavior criterion at base and drop or fix any that pass), and regenerate definitions. If cheap, add a lint check; keep it to one change.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #62 (quoted):

> **Observed**: in one run, plans for T-0068 and T-0073 came back from `steps.py review` as `replan` for `red-at-base` criteria (e.g. `! grep -nE "[0-9]+%,|0\.38" button.css` already green at base). Each cost a planner L3 run; one ticket hit the replan cap and needed the person.
>
> **Expected**: agents/planner.md requires the planner to run each `(red)` criterion against the base tree (as the reviewer and `steps.py review` do) and fix it before returning.
>
> **Evidence**: `.sdlc/runtime/tasks/0068-ui-component-skins/planner-L2.md`, `.sdlc/runtime/tasks/0073-ui-radius-pin/planner-L2.md` and the review outputs; trace detector `replan-loop` (6 findings).
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
Changed `plugins/sdlc-lite/agents/planner.md` rule 1 (generated planner -L1/-L2/-L3 and the Codex planner TOMLs regenerated). New text:

> Your last action before returning is to run every `(red)` and new-behavior criterion once more at the build-start base (in a detached worktree copy of HEAD when the tree is not base) and fix or drop any that exits 0, because `steps.py review` sends a plan with a green `(red)` span back for a replan.

The in-file wording is "in a `git worktree add --detach <tmp> HEAD` copy". Checks: `check.py` exit 0, `check-packaging.py` exit 0. No lint added: `steps.py review` already runs `(red)` spans at base.

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 0e63ead0204d
- Changed: see commits
- Commits: 572e788 T-0728: planner runs new-behavior criteria red at base as its last action
- Check: 1 The source definition says it (quote the new line in the Outcome) and `claude_roles.py generate` ...: pass
- Check: 2 `check.py` exits 0, `check-packaging.py` passes, `git diff --check <base sha>` exits 0: pass
- Follow-up: fix-now: plugins/sdlc-lite/agents/planner.md:29 the new line writes the... -> notes.md
- Follow-up: note: plugins/sdlc-lite/agents/planner.md:29 the new line does not... -> notes.md
- Follow-up: note: plugins/sdlc-lite/agents/planner.md:29 the new "last action"... -> notes.md
- Follow-up: note: docs/work/0728-planner-red-at-base-check/handoff.md Outcome quote... -> notes.md
- Follow-up: note: redck.py deviations printed no process deviation: lines -> notes.md
