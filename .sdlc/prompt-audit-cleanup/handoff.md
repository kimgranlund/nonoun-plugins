---
id: T-0098
title: "Apply prompt-audit hunks: drop history ids and dates from level-rubric, checks-that-bite, file skills"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
Shipped skill prompts carry no ticket ids or dates that the loading model can't use.

## Intent
- Do: apply the three audit hunks in Context exactly as worded, in plugins/sdlc-lite/skills/.
- Non-goals: CLAUDE.md keeps its decision record (T-0005 stays there); no behavior or check changes.
- Done when: none of the old phrases remain in the three skill files, the new wording is present, and `scripts/check.sh` exits 0.

## Context
Prompt audit, 2026-09-25, user-approved. Apply it after batch 17 merges, to avoid conflicts.
1. skills/level-rubric/SKILL.md: drop `(user decision, T-0005)`. The decision record stays in CLAUDE.md.
2. skills/checks-that-bite/SKILL.md: change "Two measured NCs that went green instead, both from 2026-07-29:" to "Two that went green instead:". Change "Each entry measured in the wild, each a check that passed while examining nothing." to "Each entry is a check that passed while examining nothing."
3. skills/file/SKILL.md step 3.2: change "Example (T-0047): ... duplicate of T-0002 `div crashes on zero divisor`" to "For example, a follow-up ... is a likely duplicate of an open ticket titled `div crashes on zero divisor`".
check.sh must stay green.

## Constraints
CLAUDE.md is not edited.

## Route
Conductor trivial edit (four exact wording swaps given by the approved audit), independently checked by a verifier L1 run in step-1.
