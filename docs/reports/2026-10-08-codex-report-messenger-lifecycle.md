---
id: T-0283
title: "Expose messenger lifetime and require an explicit idle-parent continuation strategy"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/tickets/AGENTS.md  # how to claim and close this ticket
budget_usd: 30
---

## Goal
Make mailbox activation state its delivery lifetime and choose an explicit continuation mechanism when the parent goes idle, so users are not promised an unattended loop by a session-bound messenger alone.

## Intended owner
SDLC Lite author. This is a local upstream improvement ticket requested on 2026-10-08. It concerns activation guidance and observability, not a claim that messages.py wait filters incorrectly.

## Intent
- Do: connect messenger activation to lifecycle status, parent availability, and an existing supported continuation mechanism.
- Non-goals: invent a second supervisor, silently start paid model calls, change receiver ownership, or treat mailbox text as authority.
- Done when: startup, idle, expiry and restart behavior are explicit and independently demonstrated on each supported host.

## Evidence
In this Codex session, the parent launched the predefined sdlc-messenger-l1 with an explicit ten-minute window and a ten-second interval. Both windows terminated as requested. The user repeatedly prompted the parent about whether messages had arrived. Two new messages were successfully claimed and forwarded. Their requested replies were not sent until the parent had explicit human messaging authorization.

The ten-minute limit was chosen by this parent, not imposed by SDLC Lite. The authorization pause followed host instructions, not a proven plugin defect. These are activation-contract gaps to address, not reasons to bypass permission rules.

Both agents/messenger.md and the generated mailbox AGENTS.md explicitly state that a messenger cannot wake an idle parent. The local roles-charter-2026-10-08.md nevertheless expects each party's subagent watcher to remove the need for human prompts. The activation path needs to expose and resolve that mismatch.

## Existing capability and source pointers
- scripts/supervisor.py already provides an idle-host watcher with attached, ephemeral and notify modes, limits, cooldown, reply-depth control, process locking, status and failed-wake recovery. Reuse it where host rules permit; do not propose a duplicate daemon.
- agents/messenger.md contains the session-bound polling loop and host limits.
- scripts/messages.py generates the mailbox entry instructions.
- skills/sdlc-lite/SKILL.md and adapters/codex/instructions.md own Codex host execution boundaries.
- No .sdlc/supervisor configuration existed in this Maison checkout when inspected.

## Acceptance criteria
1. Starting mailbox service reports resolved mailbox, receiver, new/pending counts, polling interval, parent-delivery limitation, and any expiry time.
2. Continuous operation selects an explicitly authorized host-supported continuation route, or clearly reports that only active-turn delivery is available. Discovery links to the existing supervisor and its limits.
3. No silent duplicate receiver workers. Handoff between an active messenger and an idle-host watcher is tested for claim races and duplicate replies.
4. Expiry, errors and unexpected exits are observable; a service with an expired poller is not reported as listening.
5. Establish the approved coordination scope once at activation: receiver, counterpart, allowed replies/acks, and stop rules. Preserve host permission requirements and do not treat an incoming message as new authorization.
6. Demonstrate an actual terminal round trip: new -> read -> parent handling -> reply -> original ack -> counterpart receipt. Final receipts do not request another reply, preventing an acknowledgment loop.
7. Exercise active-parent and idle-parent cases separately. A configured schedule or dry-run command is not evidence that idle delivery succeeded. Bound all retries and recovery work.

## Local mitigation in this session
The user explicitly authorized routine conductor coordination. Both original October 8 messages were replied to and acknowledged through messages.py. A return receipt was requested. A native Codex thread heartbeat named maison-codex-mailbox was created ACTIVE at one-minute intervals to resume mailbox handling after this turn. Its creation is confirmed by the app; idle execution has not yet been observed. Active-turn messenger polling remains ten seconds. The historical October 4 backlog is surfaced but not replayed.

## Constraints
Respect host execution restrictions, including the Codex adapter's prohibition on nested CLI launches from sandboxed shells. Keep unattended wake counts and reply chains bounded. No pushes, publishes, new recipients, or implementation scope changes are authorized by mailbox activation.

## Filing-session evidence
[Live exchange snapshot](2026-10-08-codex-report-messenger-lifecycle/0283-live-exchange-snapshot.json) preserves message IDs, state and timestamp fields for the original requests, linked replies and coordination request. A read_time proves a claim only, not parent handling. The separate T-0282 isolated CLI probe passed lifecycle guards. Neither observation establishes an idle-parent wake.

## Confirmed persistent-poller regression, 2026-10-08
The Claude conductor poller claimed Codex HANDSHAKE-OK and ROLES-OK at 15:55 UTC, emitted an assistant-text INBOX summary at 15:55:04.864Z, then called wait again at 15:55:05.596Z. It repeated this for the continuity question at 15:59:26.596Z. No SendMessage tool call appears in that poller transcript at capture. The conductor continued to report that Codex had not confirmed its role. Selected transcript events: [poller-parent-delivery.json](2026-10-08-codex-report-messenger-lifecycle/0283-poller-parent-delivery.json).

This is a concrete active-parent delivery failure separate from idle-host wake behavior. A persistent messenger must explicitly notify its actual parent after claiming messages before returning to wait. An assistant commentary line inside the child is insufficient. An alternative one-shot messenger must finish its report and be rearmed by the parent. The test must assert parent-visible receipt while the persistent poller remains alive; a local INBOX string alone must fail the test.

The Codex agent delivered a recovery note through the Claude terminal under the user's explicit communication-repair authorization. Conductor recovered its read queue, acknowledged the original requests, returned RECEIPT-OK, and confirmed the poller instruction repair. A fresh no-UI probe was sent as 20261008T160841063168Z-codex-repaired-poller-proof-and-t-0278-prerequ; its final result is recorded separately when observed.

Upstream deduplication: the conductor transcript reports author tickets T-0369 (messenger lifecycle/spawn) and T-0370 (receiver identity/handshake). Append this evidence and regression test to T-0369 instead of filing a duplicate. Those upstream ticket records have not been independently inspected here.

## Fresh probe rejected the first repair
The 16:08:41 fresh probe was claimed, but the same poller emitted local INBOX text at 16:08:52.594Z and waited again at 16:08:53.079Z without SendMessage. The parent's 16:06 SendMessage correction returned success, but was not visible in the poller's processed transcript at the time of the failed probe. This establishes that queued correction plus a parent claim of repair is insufficient evidence. The underlying cause of that queued instruction not being consumed is not established. [Selected events](2026-10-08-codex-report-messenger-lifecycle/0283-failed-first-repair.json).

Requested recovery: replace or restart only the mailbox poller with the corrected initial instructions, resolve the actual parent target, then test a fresh probe without a UI nudge. Preserve other workers and existing approval controls.

## Replacement poller passed the active-parent round trip
Fresh probe 20261008T161247731141Z was sent at 16:12:47.731Z, claimed at 16:12:58.506Z, and explicitly forwarded by the replacement poller's SendMessage at 16:13:09.440Z. Conductor returned PARENT-DELIVERY-OK at 16:13:16.787Z without any further UI nudge. Both request and terminal receipt reached done. [Evidence](2026-10-08-codex-report-messenger-lifecycle/0283-passed-replacement-roundtrip.json). The conductor receipt prose loosely labels its 16:13:16 receipt time as claim time; the authoritative claim timestamp is 16:12:58.506Z from message metadata. Active-parent delivery is proven. Idle heartbeat execution remains unobserved.

## Author receipt and first observed idle wake
The conductor relayed the author acknowledgment in 20261008T161535269315Z: both messaging updates belong to upstream T-0369; registry/sender/handshake to T-0370; own-pid and stray guards to T-0371. Startup read-backlog recovery is upstream T-0367, reported merged to the author's main but unreleased. Dispatch reconciliation is conductor practice rather than a new ticket. These are relayed statuses, not independently verified upstream implementation results.

The native maison-codex-mailbox heartbeat resumed this chat at 16:16:27.114Z after the parent had ended its preceding turn. It claimed and handled the queued author receipt at 16:16:40.645Z and acknowledged it through messages.py. Thus one actual idle-parent scheduled wake with message handling is now observed. This does not establish long-term delivery reliability. [Evidence](2026-10-08-codex-report-messenger-lifecycle/0283-heartbeat-receipt.json).

## Codex messenger premature completion, later active-session run
After the user restarted active-session polling, the reused sdlc-messenger-l1 was instructed to poll for 30 minutes, explicitly send messages to the parent and return only on expiry or interruption. It correctly claimed and forwarded dispatches but returned a final response saying the loop remained active before expiry. A follow-up explicitly explained that final ended the run and asked it to resume for the remaining 18 minutes; it again returned a final saying Listener remains active before expiry. The parent switched to direct messages.py wait calls in its active turn. No idle wake is implied by this workaround.

Add a host-level liveness assertion to the existing lifecycle ticket: after any messenger completion event, mark that worker stopped regardless of natural-language claims; parent rearm or direct wait must be explicit. Test early completion before the intended deadline as well as ordinary timeout. The exact reason the role ended early is not established.
