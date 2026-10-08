---
id: T-0370
title: "Mailbox receivers registry, default sender identity and a handshake command"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0367]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`messages.py send` knows who it is sending to and from, and a handshake proves a reader is alive before a conductor relies on the mailbox.

## Intent
- Do: Mitigations 4, 5 and 6. A registry `.sdlc/messages/receivers.json` (name, harness claude|codex|human, repo, reader session or none, last seen, default expiry); `send` refuses an unknown receiver and prints the receiver's harness and reader; `list --receivers` shows live and orphaned mailboxes and `expire` offers to close orphans. `--sender` defaults to `<repo>-<harness>-conductor` with `conductor` kept as an alias. `messages.py handshake --receiver NAME` sends a ping with a nonce, waits up to N seconds, and reports `reader alive` or `no reader`. Document the Codex reader recipe (a `wait` loop under /goal) next to the Claude one. Do not change `wait` semantics. Mitigation 3 (a cross-session wake) is a design question and out of scope here.
- Non-goals: model or effort changes; anything outside this ticket's mitigations.
- Done when:
  - Selftests: send to an unregistered receiver is refused; send to a reader-less receiver warns; handshake reports both states; default sender names repo and harness (observed failing first).
  - check.py, tickets.py check, hook-selftest.sh, the affected selftests and both generate --check pass.

## Context
Maison sent a handshake to maison-testing when the user meant the Codex session, and 7 messages sat unread for a day because no reader polled. Names on the wire carry no harness or repo. Source: [maison conductor's report](../../docs/reports/2026-10-08-mailbox-autonomy-bug.md), 2026-10-08, ranked mitigations 1 to 8. A report this large is split: this ticket takes the mitigations named in Do; the rest are T-0369 to T-0371.

## Constraints
No em or en dashes. No push or publish.
