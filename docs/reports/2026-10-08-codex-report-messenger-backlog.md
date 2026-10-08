---
id: T-0282
title: "Messenger restart hides previously claimed messages awaiting parent handling"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/tickets/AGENTS.md  # how to claim and close this ticket
budget_usd: 30
---

## Goal
Recover the parent's pending mailbox work after a messenger restart, including messages already claimed into read/<receiver>, without replaying old instructions or stealing another live session's work.

## Intended owner
SDLC Lite author. This is a local upstream-report ticket, not authorization to modify the installed plugin cache or Maison implementation. User requested filing on 2026-10-08.

## Repro
1. In a disposable mailbox, send a message to codex with messages.py send.
2. Claim it through messages.py read, then stop before the parent handles it or calls ack.
3. Start the messenger using the documented loop in agents/messenger.md.
4. The loop calls wait on new/codex only. It times out although the message remains pending in read/codex.

## Expected
Startup identifies new messages and previously claimed, unacknowledged messages separately. It reports the old backlog once and hands recovery decisions to the parent. Reporting distinguishes no new messages from no pending work. Receipt, claim, parent handling, reply and acknowledgment have distinct meanings.

## Actual and evidence
Live observation in ui-kit-maison on 2026-10-08 with Codex SDLC Lite 0.21.3:
- new/codex contained zero messages; read/codex contained ten messages dated October 4.
- messages.py wait --receiver codex --timeout 50 --interval 10 returned exit 3, output: no new messages.
- The user reported messages visible while the listener said none had arrived.
- Representative pending ID: 20261004T214214658245Z-claude-claude-wind-down-for-machine-move, read_time 2026-10-04T21:42:21.737866Z.
- A new October 8 handshake was addressed to conductor. Excluding it from codex polling was correct, not a filtering bug.
- Later correctly addressed Codex messages were claimed and forwarded successfully. New-message polling works.

The cause of the October 4 messages remaining open was not established. No claim that those historical messages were lost by a crashed messenger is made.

## Mechanism and existing support
agents/messenger.md prescribes wait, read, then report. Generated .sdlc/messages/AGENTS.md likewise polls new/<receiver>; neither gives a startup read-backlog reconciliation step. messages.py wait itself behaves as documented.

supervisor.py already recovers stranded read IDs from its own failed wake records. Assess and reuse that implementation; it does not by itself establish recovery of arbitrary pre-existing read messages created outside those recorded wakes.

## Acceptance criteria
1. A restart test with new empty and read nonempty surfaces the pending message once, with its ID, sender, topic, send_time, read_time and follow_up_requested.
2. Repeated polls do not repeatedly notify the same parent about an unchanged backlog.
3. A concurrent live owner is respected; recovery does not cause duplicate side effects or acknowledgment.
4. Other receivers' messages are never claimed.
5. Before resending a reply, recovery checks existing linked replies across all states. Existing ack and follow-up requirements remain enforced.
6. Old message bodies remain coordination data. Surfacing a historical message does not execute its instructions or automatically acknowledge it.
7. Update both the messenger role and the generated protocol source. Run a focused live role check, and include a negative control where removing recovery causes the restart assertion to fail.

## Constraints
Preserve new to read to done transitions and timestamp ordering. Do not broaden wait to return all read messages every poll without deduplication and ownership design. Do not rewrite historical messages. No installed-cache edits in this Maison filing task.

## Filing-session verification
The isolated CLI lifecycle probe passed: ack before read and ack before a required reply were rejected; a request/reply/ack exchange and terminal receipt completed with both new queues empty. Raw command arguments, exit codes and outputs: [result.json](not copied: isolated-roundtrip-r925uym9/result.json). This verifies the CLI guards, not restart recovery or idle-parent delivery.

## Backlog disposition and confirmed live recovery
Conductor's 20261008T160624516453Z reply explicitly identifies the ten October 4 messages as superseded by the wave closed October 6, with instructions to leave them untouched. They are not evidence of lost October 4 work. The October 8 conductor backlog did contain undelivered parent work caused by local child commentary instead of SendMessage; see T-0283's confirmed regression and selected transcript evidence. Recovering that read queue produced actual conductor receipts. Startup reconciliation must support this distinction.

## Upstream mapping received
Conductor relayed the author's receipt in 20261008T161535269315Z: startup read-backlog recovery maps to T-0367, reported merged to upstream main but unreleased. Reuse that ticket and inspect its implementation before proposing further changes. This status is relayed, not independently verified here.
