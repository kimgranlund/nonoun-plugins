---
id: T-0369
title: "A conductor can spawn the messenger, and the messenger keeps polling after a report"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0367]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor can spawn the messenger without a hook denial, and the messenger keeps polling so two messages 13 seconds apart both reach its parent.

## Intent
- Do: Mitigations 1, 2 and 8. (1) hooks/block-role-spawn.sh and `dispatch.py prepare` allow `sdlc-lite:messenger` for a conductor session (a one-line allowance with its selftest case, plus a negative case that other non-role agents are still denied) and give it a legible name like `inbox-<repo>-<receiver>`. (2) agents/messenger.md and the generated Codex and Claude text: report each batch to the parent with SendMessage and keep looping in the same turn, or end the turn only when told; one clear rule. (8) State in messenger.md the hook restriction, the persistent loop, the zsh glob pitfall for any shell watcher (use `find`), and that a Monitor-based watcher posts to the user's feed. Builds on T-0367 (same file), so it starts after T-0367 merges.
- Non-goals: model or effort changes; anything outside this ticket's mitigations.
- Done when:
  - A hook-selftest case: a conductor spawning `sdlc-lite:messenger` passes, another role from a conductor still denies (observed failing first).
  - A messages.py or messenger selftest simulates two messages 13 seconds apart reaching the parent in one turn (observed failing first).
  - check.py, tickets.py check, hook-selftest.sh, the affected selftests and both generate --check pass.

## Context
Maison hit all of this on 2026-10-08: the messenger spawn was denied by block-role-spawn.sh, and a one-shot messenger missed a reply sent 13 s after its first report. Source: [maison conductor's report](../../docs/reports/2026-10-08-mailbox-autonomy-bug.md), 2026-10-08, ranked mitigations 1 to 8. A report this large is split: this ticket takes the mitigations named in Do; the rest are T-0369 to T-0371.

## Constraints
No em or en dashes. No push or publish.
