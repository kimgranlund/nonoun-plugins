---
id: T-0382
title: "steps.py widen evaluates the scope span in the lane work tree, not the stale root"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py widen` (and `lint`) evaluate their scope span in the lane work tree when the handoff lives in a shared or stale checkout, so a valid widen is not refused as red.

## Intent
- Do: widen resolves its tree with git_toplevel of the handoff dir, so a shared handoff in the primary checkout makes it evaluate the stale root against the lane base. Add `--tree PATH` (as T-0377 did for `split --only`) and default to the lane work tree when the handoff dir is not in it; apply the same to the `steps.py lint` criterion runs. Reuse T-0377's tree resolution.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - Disposable-repo repro from maison's T-0292 (primary A, linked lane B with the prerequisite, handoff under primary): widen run for the lane accepts the prerequisite; red before the change (observed failing first).
  - widen without `--tree` in the ordinary single-checkout case behaves as before.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Maison T-0292 (reports at .sdlc/tickets/0292-widen-shared-handoff-worktree/handoff.md) seen on T-0152 steps 3 and 5: a conductor scope decision was needed instead each time. Related: T-0377 (split --only --tree, shipped), T-0365 (explicit file list, shipped). Source: the maison conductor's delivery check of 2026-10-08 (13 unread messages in the maison repo, .sdlc/messages/new/sdlc-lite-author/; RCA ledger /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/rca-ledger-2026-10-08.md). The user's RCA directive there: fix at the origin; workarounds retire only after an installed proof and a live discriminating rerun.

## Constraints
No em or en dashes. No push or publish. Codex host behavior cannot be run live here; mark it unverified.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1 | tail -1 | grep -q 'steps selftest: PASS'`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1 | grep -c 'ok: widen: (T-0382)' | grep -qx 7`
- `python3 plugins/sdlc-lite/scripts/check.py >/dev/null 2>&1 && python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check >/dev/null 2>&1`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check >/dev/null 2>&1 && python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check >/dev/null 2>&1`
- `python3 plugins/sdlc-lite/scripts/steps.py widen --help | grep -q -- '--tree'`

## Closed

2026-10-08: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
