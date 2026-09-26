---
id: T-0098
title: "Apply prompt-audit hunks: drop history ids and dates from level-rubric, checks-that-bite, file skills"
type: chore           # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
Shipped skill prompts carry no ticket ids or dates that the loading model can't use.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Prompt audit, 2026-09-25, user-approved. Apply it after batch 17 merges, to avoid conflicts.
1. skills/level-rubric/SKILL.md: drop `(user decision, T-0005)`. The decision record stays in CLAUDE.md.
2. skills/checks-that-bite/SKILL.md: change "Two measured NCs that went green instead, both from 2026-07-29:" to "Two that went green instead:". Change "Each entry measured in the wild, each a check that passed while examining nothing." to "Each entry is a check that passed while examining nothing."
3. skills/file/SKILL.md step 3.2: change "Example (T-0047): ... duplicate of T-0002 `div crashes on zero divisor`" to "For example, a follow-up ... is a likely duplicate of an open ticket titled `div crashes on zero divisor`".
check.sh must stay green.

## Constraints
What must not change. "None" if none.
