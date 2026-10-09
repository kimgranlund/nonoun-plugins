---
id: T-0394
title: "dispatch.py prepare refusal for solo names the solo_run.py and fanout.py prep paths"
type: chore
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py prepare` refusing the role `solo` names how to start a solo ticket instead, so a conductor does not guess.

## Intent
- Do: in scripts/dispatch.py (the `role == 'solo'` refusal near line 549) add one line to the error: start solo through `solo_run.py run --task-dir <dir> --tier L2 --no-worktree`, or `fanout.py prep` for a lane.
- Non-goals: changing which roles prepare accepts.
- Done when:
  - A dispatch selftest case, observed failing first: the refusal for `solo` contains `solo_run.py run --task-dir` and `fanout.py prep`.
  - dispatch.py selftest and check.py pass.

## Context
ultimate-tokens conductor, 2026-10-08: its first solo dispatch through the Agent tool failed the spawn gate until it found solo_run.py.

## Constraints
No em or en dashes. No push or publish.
