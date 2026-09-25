---
id: T-0069
title: "Merge-step conflict-marker guard flags a lane line that legitimately starts with seven < or >"
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0064
---

## Goal
The merge-step conflict-marker guard (the `(guard)` line with `<<<<<<<` in the `merge-step` template) fails only on conflict markers the merge itself introduced, and passes a merge whose lane branch legitimately added a line starting with seven `<` or `>` to a touched file. Done when check.py's behavior probe proves both: the legit-lane-line merge passes, and a merge commit that kept real git conflict markers still fails, alongside the existing empty, marker, and clean probes.

## Context
Follow-up from T-0064 (merge-step-conflict-marker-guard/filer-L1.md), filed by hand because `tickets.py close` marked it a duplicate of T-0064 itself (see T-0071):

Merge-step conflict-marker guard still flags a line on the lane branch that legitimately starts with seven `<` or `>` in a touched file; restrict it to markers that git's merge left in the file, or document the false positive.

## Constraints
- Restricting the guard is preferred over documenting the false positive (ticket text lists it first); document instead only if no restriction is sound, and say why in the plan.
- The two template copies (agents/planner.md and skills/handoff-format/SKILL.md) stay byte-identical and pass `steps.py lint`; builder.md stays in step.
- The guard stays a single shell command span, runs from the git toplevel, scans only files the merge touched (no whole-tree scan), handles file names with spaces, and passes an empty merge.
- A hint, not a decision: a line git's merge left in the file is new versus both parents (`git diff-tree --cc` marks such lines `++`), while a lane line exists in HEAD^2.
- `scripts/check.sh` stays green. Never commit, push, or publish.

## Acceptance
- check.py probe gains a legit-lane-line case (passes) and a real-conflict-kept case (fails); both bite (a negative control shows the old guard fails the legit case).
- CLAUDE.md, sdlc-lite-author.md, and any doc that describes the guard's criterion match the new behavior.
