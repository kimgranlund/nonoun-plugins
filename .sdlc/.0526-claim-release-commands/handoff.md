---
id: T-0526
title: "Claim and release commands, plus claim lint (maison T-0546)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Claim and release commands, plus claim lint, closing maison T-0546 observations 1, 2, 3, 22.

## Intent
- **Files:** `plugins/sdlc-lite/scripts/tickets.py`: a new `claim <id> --by <agent> [--handover --reason TEXT]` and `release <id>`; `problems` and `cmd_check` warnings; the "Claim a ticket" text in `ROUTER_PROCEDURES` (around line 1558). Also `plugins/sdlc-lite/skills/ticket/SKILL.md`.
- **Behavior:**
  - `claim` writes `status: claimed` and `claimed_by: <agent> <YYYY-MM-DD>` directly after `created:`, then runs roadmap.
  - `--handover` replaces the value and appends one dated body line.
  - `check` warns on a trailing comment on the claim line, on a claim line out of place, and on a claim older than `claim_days:` (config, default 7) when the folder has no running attempt.
  - When a ticket problem makes `new` refuse, the message names that ticket and the one-line fix.
- **Done-when:** `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with these new cases:
  - `claim` on a fixture puts the line after `created:` and regenerates the roadmap.
  - A claim line with a trailing comment produces a warning naming the ticket. The same fixture without the comment produces none (negative control).
  - A 10-day-old claim with no running attempt is listed. The same claim beside a running attempt is not.
  - `new` succeeds beside a ticket that has both `status: claimed` and `claimed_by:`.

## Context
- Source: maison `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (the numbered observations named above) and the triage `.sdlc/.0525-maison-0546-triage/architect-L1.md` (group A; read its Constraints and Risks).
- Maison's hand-written rules are the working reference: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/AGENTS.md`, `.sdlc/tickets/AGENTS.md`, `.sdlc/writing-rules.md` in that repo. Read only; never edit maison.
- Tickets A, C, B, G, D all edit `plugins/sdlc-lite/scripts/tickets.py`; they run one after another in that order (depends chain).

## Constraints
Preserve reference-safe closure, cross-worktree id uniqueness and explicit follow-up selection. A new or changed check needs a positive case and an observed negative control.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0, and the selftest holds the Done-when cases: `claim` puts `claimed_by:` directly after `created:` and regenerates the roadmap; a trailing comment on the claim line warns naming the ticket while the same claim without it does not; a 10-day-old claim with no running attempt is listed while the same claim beside a `*.running` file is not; `new` succeeds beside a ticket with `status: claimed` and `claimed_by:`.
- Each new case bites: disabling the claim lint, the running-attempt exemption, the claim line placement, the handover rewrite, or the roadmap write after `claim` makes the selftest fail.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0 (the regenerated `.sdlc/AGENTS.md` router is current).
- The router "Claim a ticket" procedure and `plugins/sdlc-lite/skills/ticket/SKILL.md` describe `claim`, `--handover --reason`, `release`, and the `claim_days:` lint; a `new` refused by a ticket problem names that ticket folder and a one-line fix.
- `git diff --check` exits 0.

## Closed

2026-10-13: solo L2 built, verifier L2 pass, merged from fanout/wave64-a; gate red was the ticket skill hint length, fixed in the lane
