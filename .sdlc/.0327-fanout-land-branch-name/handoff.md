---
id: T-0327
title: "fanout land misreads host worktree branch names worktree-agent-<id> as external lanes (T-0287 finding 3)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py land` recognizes host-named worktree branches `worktree-agent-<agent_id>` (under `.claude/worktrees/agent-<agent_id>`) as the solo or full lane they belong to and closes the ticket.

## Intent
- Do: Finding 3 in docs/reports/subagent-mode-live-2026-10-07.md: land treated each lane as an external lane `full`, merged them, then refused to close for lack of a filer file. Map the host branch to its lane through the dispatch record's agent_id instead of the branch name. Done when a selftest with host-style branch names lands and closes a solo lane, and an unknown branch is still treated as external (observed).
- Non-goals: any model or effort change; the account-switch criterion of T-0287.
- Done when:
  - The observed result above holds; `check.py`, `tickets.py check` and the touched script selftests pass.

## Context
Found by the T-0287 live run on branch subagent-w5. Files: plugins/sdlc-lite/scripts/fanout.py.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-06: built by fanout lane, merged by hand
