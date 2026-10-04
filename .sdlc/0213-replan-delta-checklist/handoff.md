---
id: T-0213
title: "Replan handoff, planner checklist, scoped plan review, replans metric"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L
priority: P2         # P1 | P2 | P3
depends: [T-0199, T-0200, T-0201, T-0202, T-0211]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Make a replan cheap: a scripted replan handoff, a planner checklist from the findings corpus, a scoped plan review, and a `replans` metric.

## Intent
- Do: Section C. `steps.py replan-handoff <task dir>` is the scripted form of the chain's `plan review: replan: <finding>` append into handoff.md (not a second file); it refuses when no `replan` verdict counts after the newest plan. `agents/planner.md` gains a checklist, one line per finding class with a dated citation (every design row or goal clause has a criterion; every untagged criterion is red at the start of its step; every called function is named with its failure input; every new file is in the layout record that enumerates files; a slow guard has a `guard timeout:` line). `agents/plan-reviewer.md`: after `specgate.py check` passes review only judgment items, and a re-review after a delta reads T-0200's merged view and the findings it answers. `footprint.py` gains `replans` (non-stale planner results beyond the first plus replan verdicts). The existing stop after two replan verdicts stays and the conductor's hard stop is T-0199 text (d). Regenerate Codex agents. Record, as an open question for the user and without changing any default, the option to run delta re-reviews at lower reviewer effort.
- Non-goals: changing any model or effort default; conductor wording beyond a pointer line; a version bump, tag, push, or publish.
- Done when: the changes are built, an independent verifier passed each step, and selftest for replan-handoff on a seeded task dir with a replan verdict and a negative control that it refuses without one; footprint selftest for replans including a stale rerun; replay: the checklist as a rubric on the four replanned plans names at least half the judgment findings, otherwise the checklist is removed and the ticket reports it. `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Cost-control addendum to the lean SDLC design: `docs/lean-sdlc/cost-control.md` v0.2, reviewed in `docs/validation/lean-sdlc-cost-control-review.md`. Measured on 2026-10-04: about $190 over 78 role runs, 4 of 7 plans returned for replan. Owning files and ordering: scripts/steps.py (replan-handoff), agents/planner.md, agents/plan-reviewer.md, scripts/footprint.py, generated Codex agents, skills/chain/SKILL.md, scripts/check.py. Waits for T-0199, T-0200 (delta format), T-0201 (planner.md, lint), T-0202 (planner.md) and T-0211. Plan level L3.

## Constraints
Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's (change none), no em dashes, one authoritative location for each fact, checks that can fail with a negative control. Read the design first: docs/lean-sdlc/cost-control.md (v0.2) and docs/validation/lean-sdlc-cost-control-review.md; re-read every cited line number at plan time, since T-0196, T-0197, T-0199, T-0200, T-0201 and T-0202 move them. Conductor wording is T-0199's file (agents/conductor.md): do not restate it, and edit it only as a pointer line after T-0199 merges. Merge main into the build branch before each local merge and keep both sides of check.py and check.sh conflicts. Run roles from the main checkout's run.sh in a separate worktree. No version bump, tag, push or publish.
