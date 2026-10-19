---
id: T-0370
title: "Mailbox receivers registry, default sender identity and a handshake command"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
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

verifier: L3

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/messages.py selftest` exits 0 and prints `ok: registry: send to an unregistered receiver is refused`, `ok: registry: send to a reader-less receiver warns, a live one prints its reader`, `ok: sender: default names repo and harness, conductor kept`, `ok: handshake: reader alive and no reader` and `ok: receivers: list shows live and orphaned, expire closes orphans`.
- Those five cases fail against the pre-change script (observed: `git show HEAD:plugins/sdlc-lite/scripts/messages.py` as the CLI under test gives FAIL for each).
- `send` to a receiver absent from `.sdlc/messages/receivers.json` exits 1 and writes nothing; `reply` to an unregistered sender still works.
- `send` prints the receiver's harness, repo and reader on stderr and warns when the reader is `none`; stdout stays the message path.
- Without `--sender`, the sender is `<repo>-<harness>-conductor`; `--sender conductor` is stored as `conductor`; with no flag and no detectable harness the send is refused.
- `handshake --receiver NAME` prints a line starting `reader alive` and exits 0 when a reader claims the ping, and a line starting `no reader` and exits 3 on timeout; it does not call `cmd_wait` and `wait` is unchanged.
- `list --receivers` shows `live`, `no-reader` and `orphaned`; `expire` names orphans on stderr; `expire --orphans` closes them and touches no registered receiver.
- The mailbox `AGENTS.md` template documents the Codex reader recipe (a `wait` loop under `/goal`) beside the Claude one.
- `python3 plugins/sdlc-lite/scripts/check.py`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, `bash plugins/sdlc-lite/scripts/hook-selftest.sh`, `bash plugins/sdlc-lite/scripts/run-selftest.sh`, `python3 plugins/sdlc-lite/scripts/supervisor.py selftest`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` all exit 0.
- No em or en dash in the diff; `git diff --check` is clean.

## Closed

2026-10-08: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
