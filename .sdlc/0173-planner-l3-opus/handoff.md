---
id: T-0173
title: "Move planner L3 from Fable xhigh to Opus xhigh"
type: chore           # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-09-30
---

## Goal
Planner L3, which plans cross-cutting work and every replan, runs on Opus xhigh instead of Fable xhigh, and every rule that depended on the old family follows.

## Context
User decision, 2026-09-30, to fit the Claude table to the Max plan. Fable was 5% of the 912 recorded role runs and 31% of recorded cost (`$164` of `$537`), and planner L3 was the largest item (18 runs, `$103`). Claude only; the Codex planner L3 (`gpt-6-astra` high) does not change.

Change, `plugins/sdlc-lite/scripts/run.sh`: `planner:L3)` becomes `model=opus; effort=xhigh`. Follow the dependents:

1. `skills/level-rubric/SKILL.md`: the planner table row for L3 and any sentence that says planner L3 is Fable.
2. The plan-reviewer family rule in `run.sh` (lines near 205 to 215) and `agents/plan-reviewer.md`: the reviewer is Opus high and moves to Fable high after an Opus planner. With planner L3 on Opus, every required L3 review now runs on Fable high. Keep the rule and say so in the rubric; this moves some Fable spend from the planner to the reviewer and is not a saving of all of it.
3. `scripts/check.py`: the table comparison and any family-rule check.
4. `scripts/run-selftest.sh` line 166 builds a fixture planner result with `model=fable effort=xhigh`; update the fixtures that exercise the plan-reviewer family rule so one case still covers a Fable planner and one an Opus planner.
5. `docs/codex-role-execution.md` and `docs/validation/` are not edited except to add a dated note.

Replan wording: the rubric says any replan uses planner L3; it stays, now on Opus xhigh.

## Constraints
Only planner L3 changes model and effort in `run.sh`. Keep a negative control for the family rule. Run `check.py`, `run-selftest.sh`, and the full `check.sh`. Live check: one planner L3 run and one plan-reviewer run through `run.sh` showing planner `opus xhigh` and reviewer `fable high`.
