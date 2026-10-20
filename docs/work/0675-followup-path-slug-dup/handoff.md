---
id: T-0675
title: "close drops follow-ups whose leading file path matches a filed ticket's slug"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py close` marks a follow-up as a duplicate only when it is the same finding as an existing ticket, so unrelated bullets that start with the same file path reach NOTES.md or a ticket instead of being dropped.

## Intent
- Do: in `cmd_close` (`plugins/sdlc-lite/scripts/tickets.py`, the follow-up loop near line 3768), build the duplicate key from the text after any leading path-like words (tokens containing `/` or a file extension), or drop the slug-prefix comparison and match on the full normalized title only; pick the smaller change that keeps the existing `(p)` and `(s2)` selftest cases passing.
- Non-goals: changing how a filed ticket's slug is chosen.
- Done when: the criteria pass.

## Context
Reported by the agent-ui conductor (0.25.1, still on main at 0.28.0). `base_ = '-'.join(re.findall(r'[a-z0-9]+', plain.lower())[:5])`, and `dup` matches when `kbase == key`. Bullets starting `packages/agent-ui/a2ui/src/...` all slug to `packages-agent-ui-a2ui-src`. Once one is filed (agent-ui T-0384), every later bullet with that path is marked "duplicate of T-0384" and goes to neither notes.md nor a ticket. In agent-ui T-0193's close, 3 unrelated findings were lost, including a decide item.

## Constraints
A true duplicate (same normalized title) is still marked duplicate.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with a new case: a ticket filed from a bullet starting `pkg/a/b/c.ts: x is wrong` exists, and closing another ticket with follow-up `pkg/a/b/c.ts: y is unrelated` sends that follow-up to notes.md, not "duplicate of". The case fails with the change reverted.
2. The existing `(p)` duplicate case still passes.
3. `git diff --check <base sha>` exits 0.
