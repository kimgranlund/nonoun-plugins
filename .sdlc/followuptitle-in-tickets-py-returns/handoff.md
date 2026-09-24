---
id: T-0014
title: "follow_up_title in tickets.py returns an empty title when the bullet..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0013
---

## Goal
`tickets.py close` never files a follow-up ticket with an empty or mangled title. Two defects, both in `plugins/sdlc-lite/scripts/tickets.py`:
1. `follow_up_title` (around line 310) takes the first sentence even when it is empty, so `follow_up_title('. ' + 'x'*80)` returns `''`. Per the T-0013 step spec (`.sdlc/follow-up-titles-truncated/step-1/handoff.md`, rule "if the first sentence ... is non-empty and <= 70 chars"), an empty first sentence must be skipped: fall through to the whole-word `...` cut (or use the next non-empty sentence if that is simpler and still fits the spec). The title must never be empty for non-empty input.
2. In `cmd_close` (around line 360) the cleanup `re.sub(r'[`*_\[\]()]', '', item)` deletes every underscore, so a code name like `follow_up_title` becomes `followuptitle` in the title (this ticket's own title came out that way). Underscores inside a word must survive; underscores used as markdown emphasis delimiters (`_word_`, `__word__`) may still be removed.

Done when: both are fixed, `selftest` has assertions that fail on the current code for each (red-then-green), and `scripts/check.sh` passes.

Clarify (unattended, 2026-09-24): Goal was the template placeholder; scope set from the Context bullet plus the review note under Constraints. Gap named, not blocking: whether the slug should also keep underscores is out of scope (slugs must match `^[a-z0-9]+(-[a-z0-9]+)*$`).

## Context
Follow-up from T-0013 (follow-up-titles-truncated/filer-L1.md):

`follow_up_title` in tickets.py returns an empty title when the bullet starts with `. `: it should skip an empty first sentence as the T-0013 step spec says (e.g. `follow_up_title('. ' + 'x'*80)` returns `''`)

## Constraints
Existing title rules from T-0013 stay as they are for every other input (<= 70 chars returned whole; a non-empty first sentence that fits is used without its final `.`; else a whole-word cut ending in `...`, at most 70 chars). Slug generation does not change. Existing selftest cases keep passing.

Note (review 2026-09-24): the follow-up title cleanup also strips underscores from code names; this ticket's own title came out as "followuptitle" and was fixed by hand.
