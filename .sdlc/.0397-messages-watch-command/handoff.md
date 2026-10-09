---
id: T-0397
title: "messages.py watch polls, beats and renews in one process"
type: feature        # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0396]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A documented `messages.py watch` (or equivalent) polls the mailbox, beats on every poll and renews before the 30 minute Monitor expiry in one process, so `status` reflects a working reader.

## Intent
- Do: add the watcher command and document it in the messenger and conductor mailbox text. Registration with `activate` plus a Monitor shell loop with no beat reports a working reader as stalled within 3 x interval; the command removes that gap. Build on T-0396's lapsed-watch reporting; do not redo it.
- Non-goals: model or effort changes; user-feed heartbeats.
- Done when:
  - A selftest case, observed failing first: a receiver run through `watch` for longer than 3 x interval is reported alive by `status`, and one that stops is reported stalled.
  - messages.py selftest, check.py and tickets.py check pass.

## Context
Maison and Codex, 2026-10-09 02:30 UTC: after `messages.py activate --receiver conductor --worker conductor-monitor --kind watcher --interval 20`, status reported the worker stalled within 60 s because activation is the only beat. Workaround in use: the Monitor loop runs `messages.py beat` every 20 s poll. Follow-up to T-0396.

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/messages.py selftest` exits 0 and prints `ok: watch: one process polls, beats and renews, so status reads listening` (the case runs `watch` for 4.6 s at a 1 s interval and a 3 s window, so listening needs both beat and renew, then reads stalled after the watcher is killed).
- `python3 plugins/sdlc-lite/scripts/messages.py watch --help` exits 0 and lists --receiver, --worker, --interval and --timeout.
- `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0.
- The mailbox AGENTS.md template in messages.py (Watch expiry bullet) and `plugins/sdlc-lite/agents/messenger.md` document `watch`; `claude_roles.py generate --check` and `codex_roles.py generate --check` pass.

## Closed

2026-10-08: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
