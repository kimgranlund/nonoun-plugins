---
id: T-0142
title: "Stop the ticket treadmill: loose-ends step, fast lane, filer fix-now-or-drop, one-ticket cap"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P1         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
Small related work gets finished in the session that found it. A new ticket exists only for work that is out of scope, large, or needs the user.

## Intent
- Do: ship all four parts in the Context (loose-ends step in /chain, a `/fix` fast-lane skill routed by the conductor for size-S asks, filer Follow-ups tagged `fix-now` / `decide` / `note`, and a code-enforced cap of one follow-up ticket per `tickets.py close` with the rest going to `.sdlc/notes.md`), plus the doc and check.py updates listed there.
- Non-goals: no change to `close --reason`, `--ack-warnings`, `--rewrite-refs`, the dry-run digest confirmation, the level tables, or fanout's merge flow; no retry ladder in the loose-ends step.
- Done when: `tickets.py selftest` proves the cap (a second eligible follow-up is refused as a ticket and lands in `.sdlc/notes.md`; `note` items never become tickets), check.py guards the new filer tags and the loose-ends and fast-lane wording, the named docs agree, and `scripts/check.sh` is green.
- Gaps named (unattended clarify, not blocking): the ticket allows a `/fix` skill or a `/chain --fast` mode; prefer a `/fix` skill unless the planner finds a concrete reason otherwise. How close tells a user-approved `decide` item or a real bug/risk from other items is the planner's design (for example a tag on the filer line that the conductor sets after the user answers "ticket").

## Context
User decision, 2026-09-26: "the endless ticket filing ... tasks or issues [should] be fully completed in sessions instead of filing more tickets and enduring the full lifecycle". Today most batches were follow-ups that earlier batches filed: the filer proposes 1 to 3 per ticket, and each runs plan, build, verify, file and close at $1 to $4. The user chose all four of these:

1. **Loose-ends step in /chain.** After the last planned step passes and before /file, the conductor collects small follow-ups within the task's scope (from builder Notes, verifier notes, and the filer's draft) and runs them as one extra step on the same branch: builder at the lowest fitting level, then a verifier. Anything that fails once is reported, not retried up the ladder.
2. **Fast lane for small fixes.** A size-S item (docs, lint tweak, one test, one-file fix) skips the planner and filer: the conductor writes the step handoff itself (Do plus 1 to 3 criteria), runs builder L1 or L2 and a verifier L1, and closes the item inline with `tickets.py close --reason`. It needs no ticket if none exists yet. Add a `/fix` skill (or a /chain `--fast` mode) and route small asks there.
3. **Filer: fix now or drop.** agents/filer.md's Follow-ups section changes: each item is tagged `fix-now` (goes to the loose-ends step), `decide` (the conductor asks the user once, in the close-out AskUserQuestion round), or `note` (appended to `.sdlc/notes.md`, never a ticket). Only items the user answers "ticket" to become tickets.
4. **Hard cap.** `tickets.py close` files at most one follow-up ticket per task, and only for a `decide` item the user approved, or a real bug or risk. Extra items go to `.sdlc/notes.md`. Enforce this in code, with a selftest.

Keep what exists: `close --reason`, `--ack-warnings`, `--rewrite-refs`, and dry-run confirmation. Update CLAUDE.md, the conductor, chain, file, ticket, handoff-format and level-rubric where they describe follow-ups. check.py guards the new wording.

## Constraints
What must not change. "None" if none.
