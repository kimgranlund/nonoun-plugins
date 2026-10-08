---
id: T-0390
title: "messages.py send defaults the sender to a name a reply can reach"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A reply to a message sent with the default sender reaches a registered receiver.

## Intent
- Do: in scripts/messages.py, `send` defaults the sender to `<repo>-<harness>-conductor` (T-0370), which is not a registered receiver, so a reply from the other harness is addressed to an unregistered alias. Pick the smaller change and say why: (a) on first send, register the default sender in receivers.json as an alias of the repo's registered conductor receiver (or as its own receiver with the same reader), or (b) default the sender to the registered conductor name and keep `<repo>-<harness>-conductor` only as a display field. `reply` must route to a registered receiver in both cases, and `list --receivers` shows the alias once.
- Non-goals: changing `wait`; model or effort changes; renaming existing receivers.
- Done when:
  - A selftest: send with the default sender, then reply from the receiver, lands in a registered mailbox that has a reader entry (observed failing first); an explicit `--sender` still works.
  - check.py, tickets.py check, messages.py selftest, both generate --check pass.

## Context
Maison conductor, 2026-10-08: on 0.22.0 `send` defaulted the sender to ui-kit-maison-claude-conductor, not a registered receiver, so a follow-up reply from Codex would have routed to an unregistered alias; Codex observed it on a status message. The maison conductor asked to attach it to the registry ticket, which is T-0370, already closed and shipped, so this is its follow-up. Related: T-0369, T-0380.

## Constraints
No em or en dashes. No push or publish. Codex host behavior cannot be run here; mark it unverified.
