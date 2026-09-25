---
id: T-0038
title: "A replan overwrites the original plan"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M
priority: P1
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A replan keeps the original plan: the replan's output goes to a new file and the first plan survives.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. After a blocked step, a replan (planner L3 on the task handoff) overwrote the full 15-step planner-L3.md with a plan for step 15 only, leaving the original only in git history. Cause: run.sh writes `$dir/$role-$level.md` (run.sh:45) and overwrites it on a rerun. Suggested: replans write planner-L<n>-replan-<k>.md (or run.sh keeps the previous file), and /chain and board.py read the newest one. The button-geometry-model bench run hit the same problem and worked around it by renaming the file by hand (planner-L3.replan1.md).

## Constraints
The failing test lands before or with the fix, never after.

## Paths (added by the conductor)
All code to change is in this worktree: plugins/sdlc-lite/ (scripts/run.sh around line 44, scripts/board.py which globs planner-L*.md, skills/chain/SKILL.md, skills/handoff-format/SKILL.md, and any other skill or doc that names planner-L<n>.md). Check with plugins/sdlc-lite/scripts/check.sh and board.py's selftest. Repro/Expected/Actual above were left as template text by the reporter; the Context section is the repro: run the planner twice on one task handoff and the second run replaces planner-L3.md. Note: roles for this task are launched by a different checkout's run.sh (/Users/kimba/Projects/nonoun/sdlc-agents), so do not rely on the fix affecting this run.
