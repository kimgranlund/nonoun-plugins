---
id: T-0530
title: "Lane record on the ticket (maison T-0546)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0541, T-0542]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

verifier: L3

## Goal
Lane record on the ticket, closing maison T-0546 observations 15, 30, and 31.

## Intent
- **Files:**
  - `plugins/sdlc-lite/scripts/lanes.py` (`open_lane`, `close_lane`, `list_lanes` around line 978)
  - `plugins/sdlc-lite/scripts/tickets.py` (a `branch:` field, shown on the roadmap and router active line; an "Open a lane" procedure)
  - `plugins/sdlc-lite/scripts/board.py`
  - `plugins/sdlc-lite/skills/handoff-format/run-operations.md`
- **Behavior:**
  - `lanes.py open --ticket` writes `branch:` and `close` removes it.
  - `list --all` matches a manual worktree to its ticket by `branch:` and shows the ticket's newest verifier verdict, so verified, unmerged work is visible.
  - `lanes.py open` already applies the claim rule, which covers "dispatch on an unclaimed ticket" once lanes open through it.
- **Done-when:** `python3 plugins/sdlc-lite/scripts/lanes.py selftest` and `tickets.py selftest` exit 0 with these new cases:
  - A manual worktree on `fix-0520`, plus a ticket with `branch: fix-0520` and a passing `verifier-L2.md`, gives a `list --all --json` row with ticket `T-0520` and verdict `pass`. Without the `branch:` line the row has no ticket (negative control).
  - `open --kind solo --ticket T-0001` writes `branch: lane/...` and `close` removes it.

## Context
- Source: maison `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (the numbered observations named above) and the triage `.sdlc/.0525-maison-0546-triage/architect-L1.md` (group D; read its Constraints and Risks).
- Maison's hand-written rules are the working reference: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/AGENTS.md`, `.sdlc/tickets/AGENTS.md`, `.sdlc/writing-rules.md` in that repo. Read only; never edit maison.
- Tickets A, C, B, G, D all edit `plugins/sdlc-lite/scripts/tickets.py`; they run one after another in that order (depends chain).

## Constraints
Preserve reference-safe closure, cross-worktree id uniqueness and explicit follow-up selection. A new or changed check needs a positive case and an observed negative control.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 and prints `ok: branch list:` (a manual worktree on `fix-0520` with a ticket `branch: fix-0520` and a passing `verifier-L2.md` gives a `list --all --json` row with ticket `T-0520` and verdict `pass`; the same setup without the `branch:` line gives a row with ticket null) and `ok: branch record:` (`open --kind solo --ticket T-0001` writes `branch: lane/T-0001-one` after `claimed_by:`, close removes it).
2. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with the `branch:` cases: `record_branch` writes the line after `claimed_by:`, the router active line ends `, branch <b>`, the roadmap Status cell ends `(branch <b>)`, and the removal restores both byte for byte.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap` leaves `.sdlc/AGENTS.md` unchanged (the committed router carries the new "Open a lane" procedure).

## Outcome

2026-10-14 · lane: solo L2 · verdict: pass · verifier: verifier-L3 (fable) · base: 678d28c3b050
- Changed: see commits
- Commits: f0a07a6 T-0530: Lane record on the ticket (maison T-0546)
- Check: 1 `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with `ok: branch list:` and `ok: br...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with the `branch:` cases: pass
- Check: 3 `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass
- Check: 4 `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap` leaves `.sdlc/AGENTS.md` unch...: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/board.py: listed under the handoff's... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/solo_run.py:561 and... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/lanes.py:719 and :1013: close and list... -> notes.md
- Follow-up: decide: .sdlc/.0541-records-readers/skips.md and... -> notes.md
- Follow-up: decide: .worktrees/tmp/0530-verifier-L3/: the throwaway git clone --shared... -> notes.md
