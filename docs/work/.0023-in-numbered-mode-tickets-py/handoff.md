---
id: T-0023
title: "In numbered mode, tickets.py new and close refuse when any existing..."
type: idea            # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0016
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0016 (ticket-numbered-folders/filer-L1.md):

In numbered mode, tickets.py `new` and `close` refuse when any existing `NNNN-` folder has the wrong id, not only the ticket being written; confirm this is the intended scope

## Constraints
What must not change. "None" if none.

## Decision needed
Only the user can settle this. Two readings disagree:
- T-0016 Intent: "`new` and `close` in numbered mode run the same rule on the tickets they write" (narrow).
- Built (T-0016 planner-L3 step 3, selftest case 7): numbered `new` and `close` refuse when any existing `NNNN-` folder has a mismatched id, following the "fix the problems above first" contract every other ticket problem uses (broad).

Options:
1. Keep broad (recommended): no code change. It matches how `new`/`close` already refuse on any bad ticket, and `check`/`roadmap` refuse the same way. Record the decision and close.
2. Narrow: drop `numbered` from the pre-check `problems(ts)` calls in `cmd_new`/`cmd_close` in `scripts/tickets.py`, keep it in `stamp()`, and flip selftest case 7 to expect success.

## Decision
2026-09-24, user: keep broad. Numbered `new` and `close` refuse when any existing NNNN- folder has a mismatched id, the same contract as every other ticket problem. No code change.
