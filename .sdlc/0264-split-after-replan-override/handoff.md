---
id: T-0264
title: "steps.py split has no override after a replan verdict"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Decide an override for `steps.py split` after a replan verdict.

## Context
split refuses with "a rejected plan is never split". In the field specgate refused a plan over 13 duplicate-criterion findings, and there was no way to proceed short of rewriting the plan. Needs a decision: an explicit flag, or specgate not counting duplicates as a rejection.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Decision
Take the explicit flag: `steps.py split <task dir> --override-review "<reason>"`. The ticket's two options sit at two different gates, and only one lacks an escape.
- `specgate.py check` runs before the plan-reviewer and already has `SDLC_SPECGATE=off` (recorded in runs.jsonl), so a duplicate-criterion refusal there was never a dead end. A duplicate span is also a real finding (the repeated criterion is already green at the earlier step, so it cannot detect the later step's change), shipped with its own negative control in T-0210. Thirteen verbatim repeats is not evidence of a false positive, so specgate keeps counting duplicates.
- `steps.py split` after a `replan` review had no escape at all, whatever produced the verdict. That is the gap the flag closes.
- Idiom copied from `SDLC_LANE_OVERRIDE`: a required reason, recorded where the next role reads it (`review override: <review file>: <reason>` under `## Plan review` in the task handoff, the section planner rule 9 already reads).
- The record makes the override stick, so `split --only N` in /chain 4.2 and `steps.py review` need no second flag. A newer plan-reviewer result ends it.
- A `blocked` review is never overridden (it names decisions only the user can make). The override is the user's call: the conductor never uses it on its own, and an unattended run keeps stopping on `replan`.

## Done when
`steps.py split --override-review "<reason>"` splits a plan whose newest review says `replan`, records the override, and stays refused for `blocked`, an empty reason, and a newer review; `steps.py selftest` proves each case; the contract records that quote the refusal say so.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, and its output holds `ok: (r) --override-review splits a replan review (a dir target)` and `ok: (r) negative: --override-review never overrides a blocked review`.
- `python3 plugins/sdlc-lite/scripts/steps.py split --help | grep -qF -- --override-review`
- `grep -qF -- --override-review plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF -- --override-review plugins/sdlc-lite/agents/conductor.md`
- `grep -qF -- --override-review docs/maintenance/sdlc-internals.md`
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- `python3 scripts/check-packaging.py` exits 0.
- `git diff --check` exits 0.
