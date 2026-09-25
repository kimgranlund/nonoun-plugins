---
id: T-0085
title: "Recurring-finding rule: question the plan or rule, not the last attempt (planner replan, conductor escalation)"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
When the same finding recurs, the chain asks whether the plan or rule is wrong before retrying.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer projects-workspace-optimizer (user's workspace-optimizer session), 2026-09-25: port from harness@nonoun-plugins 3.19.6, which the user keeps disabled at user scope, so sdlc-lite must carry what it needs.

Source: ~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/thinking-depth-rules/SKILL.md (87 lines). level-rubric escalates only by bumping a level after repeated fails. Fold the recurring-finding test into level-rubric / chain step 4 and the planner replan rules; do not port the whole skill.

## Constraints
What must not change. "None" if none.
