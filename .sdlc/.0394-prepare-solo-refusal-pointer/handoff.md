---
id: T-0394
title: "dispatch.py prepare refusal for solo names the solo_run.py and fanout.py prep paths"
type: chore
status: done
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

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and includes the case `preflight: the solo refusal names the solo_run.py and fanout.py prep paths`.
- `python3 plugins/sdlc-lite/scripts/dispatch.py prepare solo L2 <handoff.md>` exits 2 and its stderr contains `solo_run.py run --task-dir` and `fanout.py prep`.
- `python3 plugins/sdlc-lite/scripts/dispatch.py prepare builder L9 <handoff.md>` still exits 2 with the unchanged usage line and no solo pointer.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.

## Closed

2026-10-08: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
