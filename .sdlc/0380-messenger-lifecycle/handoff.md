---
id: T-0380
title: "Mailbox activation states its delivery lifetime and an explicit idle-parent continuation route"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0369]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Starting the mailbox service states what it will and will not deliver, picks an explicit continuation route when the parent goes idle, and proves a full round trip without an acknowledgment loop.

## Intent
- Do: the seven acceptance criteria of the Codex lifecycle report ([report](../../docs/reports/2026-10-08-codex-report-messenger-lifecycle.md), maison T-0283, evidence in docs/reports/2026-10-08-codex-report-messenger-lifecycle/): (1) mailbox activation reports resolved mailbox, receiver, new and pending counts, polling interval, the parent-delivery limitation and any expiry time; (2) continuous operation selects an explicitly authorized, host-supported continuation route (link to the existing supervisor.py and its limits) or reports that only active-turn delivery is available; (3) no silent duplicate receiver workers, with a tested handoff between an active messenger and an idle-host watcher for claim races and duplicate replies; (4) expiry, errors and unexpected exits are observable, and a service with an expired poller is not reported as listening; (5) the approved coordination scope is set once at activation (receiver, counterpart, allowed replies and acks, stop rules) and an incoming message never counts as new authorization; (6) a terminal round trip is demonstrated: new, read, parent handling, reply, original ack, counterpart receipt, with final receipts not requesting another reply; (7) active-parent and idle-parent cases are exercised separately, and a configured schedule or dry-run is never evidence that idle delivery succeeded; retries and recovery are bounded.
- Non-goals: model or effort changes; changing `wait` semantics; claiming idle wake works.
- Done when:
  - Selftests cover criteria 1, 3, 4 and 6 (observed failing first); 2, 5 and 7 are procedure text in agents/messenger.md and the mailbox AGENTS.md with a check.py phrase guard.
  - check.py, tickets.py check, messages.py selftest, both generate --check pass.

## Context
Forwarded by the maison conductor from Codex, 2026-10-08 (maison T-0283, plus 0282 which is T-0367 here). Idle wake observation to record, not to rely on: Codex's native one-minute heartbeat resumed an idle Codex chat once (16:16:27Z) and claimed a queued message; the user then paused the heartbeat because the scheduled-prompt entries cluttered the chat. Idle wake is observed once, currently disabled, and not proven reliable. This ticket builds on T-0369 (spawn, persistent loop, parent address and delivery) and T-0370 (registry and handshake); do not duplicate them. The Codex host cannot be run here, so mark live Codex behavior unverified.

## Constraints
No em or en dashes. No push or publish.
