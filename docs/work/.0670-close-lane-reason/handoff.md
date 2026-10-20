---
id: T-0670
title: "close verdict reason matches the recorded lane"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A closed ticket's Outcome header never contradicts itself on which lane ran: the reason text and the `lane:` field name the same lane.

## Intent
- Do: (1) `close_reason` in `plugins/sdlc-lite/scripts/fanout.py` picks solo or full from the lane recorded in the ticket's `skips.md` (`- lane:`, the same record `tickets.py` reads with `last_lane`) when one exists, and falls back to `ctx['kinds']` only without a record. (2) The `--reason` route of `cmd_close` in `plugins/sdlc-lite/scripts/tickets.py` refuses, writing nothing, when the reason says `delivered by the full chain lane` but the recorded lane is solo, or `delivered by the solo agent` but the recorded lane is full or lean, naming both lanes.
- Non-goals: changing the lane record format; follow-up filing on a reason close (T-0651).
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #30, ui-kit-neue audit 2026-10-20.
- ui-kit-neue `docs/work/.0088-context-navigation/handoff.md` Outcome: `lane: solo L2 · verdict: closed by reason (delivered by the full chain lane; ...)`; same shape in `.0085-context-forms/handoff.md:42`.
- The reason text: `close_reason` at `plugins/sdlc-lite/scripts/fanout.py:951`; it reads `ctx['kinds'].get(t.id, ('', None))` at line 958, so a ticket missing from `kinds` (or recorded as solo by another path) falls to the `delivered by the full chain lane` text at line 961. Call site `plugins/sdlc-lite/scripts/fanout.py:1727-1729`; `record_solo_lane` is written only when `ctx.get('land')` and the kind is solo (line 1723).
- The header lane: `plugins/sdlc-lite/scripts/tickets.py:3413` maps `last_lane(skips_text)` (`lean` as `full`) into the Outcome `lane:` field.
- Selftest home for the fanout side: case 15 at `plugins/sdlc-lite/scripts/fanout.py:3909-3919`.

## Constraints
A reason with no lane wording (for example `done elsewhere`) closes as today. A ticket with no lane record keeps today's reason text.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with a new case: a ticket whose `skips.md` records `- lane: solo` closed with `--reason "delivered by the full chain lane; x"` exits 1 naming `solo` and `full`, and writes nothing; the same with `--reason "done elsewhere"` closes. The refusal case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with a case-15 assertion that a ticket absent from `kinds` but with a solo lane record gets a `solo agent` reason.
3. `git diff --check` exits 0.

## Outcome

- `tickets.py close --reason` refuses (nothing written) when the reason says `delivered by the full chain lane` or `delivered by the solo agent` and the lane recorded in skips.md differs; no lane wording or no record closes as before. New `reason_lane` helper, selftest case (k4).
- `fanout.py close_reason` takes the ticket folder and reads a solo lane from its skips.md before `ctx['kinds']`; case 15 gains two assertions.
- Checks: tickets.py selftest exit 0 (case (k4) fails with the refusal disabled), fanout.py selftest exit 0, check.py exit 0, `git diff --check` exit 0.

## Outcome

2026-10-20 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 2bb7a1a320e7
- Changed: see commits
- Commits: 340c275 T-0670: close verdict reason matches the recorded lane
- Check: 1 `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with a new case (solo record + fu...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with a case-15 assertion that a ti...: pass
- Check: 3 `git diff --check` exits 0: pass
- Follow-up: note: plugins/sdlc-lite/scripts/tickets.py:3552 also refuses delivered by... -> notes.md
