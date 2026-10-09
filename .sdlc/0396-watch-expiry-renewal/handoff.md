---
id: T-0396
title: "conductor mailbox watch expires after 30 minutes and Codex messages go unclaimed"
type: bug             # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor's mailbox watch does not lapse silently: it is renewed before its 30 minute expiry, or a bounded foreground drain covers the gap, without repeated user-feed heartbeats.

## Intent
- Do: read the messenger agent, messages.py (wait, status, beat, handshake) and the conductor "How you run roles" mailbox text; decide between expiry-linked renewal (re-arm the Monitor before the 30 minute limit) and a bounded foreground drain, implement the smaller one, and make `messages.py status` or `handshake` report a lapsed watch (reader alive false) instead of a healthy idle poller.
- Non-goals: model or effort changes; periodic heartbeats into the user feed.
- Done when:
  - A selftest case, observed failing first: a registered receiver whose watch has passed its expiry is reported lapsed by status or handshake, and the chosen renewal or drain path clears it.
  - messages.py selftest, check.py and tickets.py check pass.

## Context
Maison and Codex, 2026-10-09: the Claude Monitor watcher expired after 30 minutes unnoticed, Codex messages sat unclaimed from 02:05 UTC and handshake 55111767 timed out at 02:18 while the poller agent showed idle. Reproduction with timestamps: maison .sdlc/tickets/0283-messenger-listener-lifecycle/claude-watch-expiry-reproduction-2026-10-09.md.

## Constraints
No em or en dashes. No push or publish.
