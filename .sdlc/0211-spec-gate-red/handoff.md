---
id: T-0211
title: "Spec gate A2: specgate.py red, (red) tag, split and review wiring"
type: chore           # feature | bug | chore | spike | idea
status: dropped
size: L3
priority: P2         # P1 | P2 | P3
depends: [T-0197, T-0201, T-0202, T-0210]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add `specgate.py red` and the `(red)` criterion tag: a control that must be red before its step and green after, run at split time.

## Intent
- Do: Section A (A2). `(red)` is opt-in beside `(guard)`; `steps.py swap` extends tag parity to `(red)`. `specgate.py red <task dir> --step N [--timeout S]` runs a step's `(red)` spans in the current tree under the snapshot steps.py already takes for guards (tree_state, run_guards) and refuses a zero exit (`red-first: step <n>: <span> is green now; it cannot detect the change`), a timeout, or a tree change; it runs in the current tree because builders never commit, so a base checkout lacks earlier steps. `red --base` runs in a detached worktree at $SDLC_BASE_SHA under `<toplevel>/.worktrees/tmp/specgate-<pid>` for the pre-build stage only. `steps.py split --only N` calls `specgate.red` beside its guards, and `steps.py review` and `split` call `specgate.check`. `agents/planner.md` and `skills/handoff-format/SKILL.md` carry the `(red)` text.
- Non-goals: changing any model or effort default; conductor wording beyond a pointer line; a version bump, tag, push, or publish.
- Done when: the changes are built, an independent verifier passed each step, and negative controls fail first: a `(red)` criterion green now is refused; a swap that drops a `(red)` tag is refused; a span that changes the tree is refused; the replay flags the tagged T-0183 step 3 control; the seven judgment findings are not flagged. `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Cost-control addendum to the SDLC Lite design: `docs/specs/sdlc-lite/cost-control.md` v0.2, reviewed in `docs/reports/lean-sdlc-cost-control-review.md`. Measured on 2026-10-04: about $190 over 78 role runs, 4 of 7 plans returned for replan. Owning files and ordering: scripts/specgate.py, scripts/steps.py (split, review, swap), agents/planner.md, skills/handoff-format/SKILL.md, scripts/check.py, scripts/check.sh. One writer per file: waits for T-0197 and T-0201 (steps.py, lint), T-0202 (planner.md) and T-0210. Plan level L3.

## Constraints
Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's (change none), no em dashes, one authoritative location for each fact, checks that can fail with a negative control. Read the design first: docs/specs/sdlc-lite/cost-control.md (v0.2) and docs/reports/lean-sdlc-cost-control-review.md; re-read every cited line number at plan time, since T-0196, T-0197, T-0199, T-0200, T-0201 and T-0202 move them. Conductor wording is T-0199's file (agents/conductor.md): do not restate it, and edit it only as a pointer line after T-0199 merges. Merge main into the build branch before each local merge and keep both sides of check.py and check.sh conflicts. Run roles from the main checkout's run.sh in a separate worktree. No version bump, tag, push or publish.

## Dropped
2026-10-06, by user decision (review of parked tickets): `specgate.py red` runs only at chain split time; solo criteria are not split. specgate.py keeps `check` (T-0210). Red-first for solo is a new ticket if wanted. See docs/reports/parked-tickets-review-2026-10-06.md.

## Deferred (history)
Parked 2026-10-04 by user decision (course correction): the solo-vs-lean evidence showed the default lane is the problem, so tuning the orchestrated chain is frozen until solo has run on real tickets. Revisit with that data. Status blocked, not dropped; handoff otherwise unchanged.
