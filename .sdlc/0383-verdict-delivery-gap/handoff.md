---
id: T-0383
title: "A recorded verifier verdict reaches the requesting receiver without a manual step"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When a verifier attempt is recorded, its verdict reaches the role or receiver that requested it with no manual conductor step, and a missed delivery is observable.

## Intent
- Do: Design and build the smallest mechanism: `dispatch.py record` for a verifier (or any role with a named requesting receiver in the dispatch file) writes the verdict message to that receiver in the mailbox with the result path and pass or fail, or prints one required line that a conductor script cannot skip; pick the smaller change and say why. Use the five fault-injection criteria from the Codex supplement .sdlc/tickets/0283-messenger-listener-lifecycle/recorded-verdict-delivery-gap-2026-10-08.md in the maison repo as the test cases (read it first). Cover: an attempt left `running` after a report was written, and a poller that goes idle (maison recurrence: three idle general-purpose pollers in about 2 hours, 4 to 10 minute delays; a conductor Monitor over new/<receiver> delivered a probe in 24 seconds, which is a supported route to document, not a plugin claim).
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - Fault-injection tests (observed failing first): record then no verdict message sent; message sent but poller idle; duplicate delivery; attempt left running.
  - The record-to-verdict gap in maison T-0297 (about 7 minutes, 21:07:14Z record, 21:14:19Z verdict) cannot recur in the fixture.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Maison T-0297 L1 delta verifier: the artifact PASS at 21:07:14Z reached Codex only at 21:14:19Z because the conductor, a manual step, had to send the verdict. Related: T-0369, T-0380 (shipped 0.22.0), maison T-0283 and T-0282. Source: the maison conductor's delivery check of 2026-10-08 (13 unread messages in the maison repo, .sdlc/messages/new/sdlc-lite-author/; RCA ledger /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/rca-ledger-2026-10-08.md). The user's RCA directive there: fix at the origin; workarounds retire only after an installed proof and a live discriminating rerun.

## Constraints
No em or en dashes. No push or publish. Codex host behavior cannot be run live here; mark it unverified.
