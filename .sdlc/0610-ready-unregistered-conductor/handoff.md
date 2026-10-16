---
id: T-0610
title: "lanes.py ready exits 1 in a fresh repo: no conductor registered"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A worker's `lanes.py ready` in a freshly onboarded repo exits 0, or the setup that makes it pass is part of onboarding.

## Context
Found by the two-host rehearsal (T-0592, `docs/reports/2026-10-15-two-host-rehearsal.md`). In a repo started with `tickets.py --root .sdlc new`, the first `lanes.py ready` pinned `refs/sdlc/ready/<id>` and unlocked the lane, then printed `not sent to conductor: messages.py: receiver conductor is not registered (registered: none)` and exited 1. Nothing in `tickets.py new`, `roadmap` or `lanes.py open` registers the conductor mailbox, so every first ready in a new repo fails the same way. After `messages.py register --name conductor --harness claude` the rerun exited 0. The ref and the unlock already happened, so the exit 1 only reports the missing notice; a worker that treats exit 1 as failure stops when its work is in fact pinned.

## Intent
- Do: pick one: register a default conductor on first use (open or ready), or have ready warn and exit 0 when no conductor is registered and the ref is pinned, or name the register step in the onboarding output. Update the lane-lifecycle docstring and spec section for ready.
- Non-goals: changing the mailbox format.
- Done when: the criteria pass.

## Constraints
The ref pin and unlock stay as they are.

## Acceptance criteria
1. (red) A lanes.py selftest case opens a lane in a fresh fixture repo with no registered conductor, runs `ready`, and expects the chosen outcome; `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0.
