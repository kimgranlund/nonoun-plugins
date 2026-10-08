---
id: T-0371
title: "dispatch.py guards assume one session: own-pid attempt block and repo-wide stray worktree check"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0363]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py prepare` and `record` stop tripping on the caller's own session and on unrelated peers' worktrees and branches.

## Intent
- Do: Mitigation 7, also the maison retro rows on both. `prepare`: an attempt whose recorded pid is the calling session's own is ignored (not blocked, no need for `run_lifecycle.py recover`). `record`: the stray worktree and branch check compares against the role's own tmp prefix and branch prefix, not the whole repo's lists. Reuse the existing selftest style in dispatch.py. Coordinate with T-0368 (prune flag) and T-0363, which also edit dispatch.py: start after both merge.
- Non-goals: model or effort changes; anything outside this ticket's mitigations.
- Done when:
  - Selftests: an attempt carrying the caller pid does not block the next prepare; an unrelated stray worktree or branch no longer warns in record while the role's own stray still does (observed failing first).
  - check.py, tickets.py check, hook-selftest.sh, the affected selftests and both generate --check pass.

## Context
Maison needed `run_lifecycle.py recover` twice for an attempt holding its own pid and saw stray-worktree noise on every record, with 0.21.2 plugin text; the 0.21.1 recover fix (764c5436) names or recovers a stale attempt but still blocks the own-pid case. Retro rows 9 and 11 in docs/reports/2026-10-08-fleet-retro-06.md. Source: [maison conductor's report](../../docs/reports/2026-10-08-mailbox-autonomy-bug.md), 2026-10-08, ranked mitigations 1 to 8. A report this large is split: this ticket takes the mitigations named in Do; the rest are T-0369 to T-0371.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-08: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
