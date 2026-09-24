---
id: T-0014
title: "follow_up_title in tickets.py returns an empty title when the bullet..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0013
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0013 (follow-up-titles-truncated/filer-L1.md):

`follow_up_title` in tickets.py returns an empty title when the bullet starts with `. `: it should skip an empty first sentence as the T-0013 step spec says (e.g. `follow_up_title('. ' + 'x'*80)` returns `''`)

## Constraints
What must not change. "None" if none.

Note (review 2026-09-24): the follow-up title cleanup also strips underscores from code names; this ticket's own title came out as "followuptitle" and was fixed by hand.
