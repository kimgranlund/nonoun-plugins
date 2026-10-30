---
id: T-0821
title: "lanes.py who, overlap warning, and ticketless land for live lanes"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0819]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Three lane helpers let a live session share a repo with a factory session: `lanes.py who` names the active factory session, `lanes.py list` warns about file overlap with a planned edit, and the factory can land a ticketless live lane behind its land gate.

## Context
- Design agreed with the user on 2026-10-30: with a factory session in the repo, a live session works as a worker in its own lane; the factory stays the only writer of main (the "Hosts in one repo" bullet of `plugins/sdlc/AGENTS.md`). Builds on the renamed tree (T-0819; plugin `sdlc`, agents `sdlc:factory`, `sdlc:live`, `sdlc:hybrid`).
- Today: `lanes.py open <name> --no-claim` opens a lane with no ticket; `lanes.py ready` pins the review sha, unlocks and notifies the factory (T-0590, T-0694); `lanes.py finish` requires a verifier verdict, so a ticketless lane cannot land through it. Mailbox registry: `.sdlc/messages/receivers.json` (`messages.py list --receivers`); run markers `*.running` under `.sdlc/runtime/tasks/`.

## Do
1. `lanes.py who [--json]`: prints `factory <session or receiver> <evidence>` for an active factory session in this repo (a live mailbox receiver of harness claude whose reader is a factory session, or a `*.running` marker owned by a live process, or an open fanout or solo lane), else `none`, exit 0 either way.
2. `lanes.py list --overlap <path>...`: prints each open lane whose diff from its base touches one of the paths, one line per lane and path, exit 0.
3. `lanes.py finish <lane> --no-ticket`: for a lane with no ticket, land behind the configured land gate with no verdict step, no close, then close the lane; refuse when the lane diff touches a `hash_bound:` path unless a verifier result is given with `--verifier-agent-id`.

## Acceptance criteria
- `python3 plugins/sdlc/scripts/lanes.py selftest` exits 0 with new cases: `who` reports `none`, then `factory` with a fixture receiver; `--overlap` reports a lane touching the path and not one that does not; `finish --no-ticket` lands a ticketless lane and refuses one touching a `hash_bound:` path. Each new case fails before the change.
- `python3 plugins/sdlc/scripts/check.py` exits 0.
