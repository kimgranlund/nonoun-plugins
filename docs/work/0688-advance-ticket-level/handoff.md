---
id: T-0688
title: "dispatch.py advance handles ticket-level completions"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py advance` moves a ticket forward after a ticket-level completion (a solo, a ticket verifier, a ui-designer review), not only after a `step-<n>/` builder or verifier, so the conductor can call one command for every completion.

## Intent
- Do:
  1. In `advance` (`plugins/sdlc-lite/scripts/dispatch.py`, near line 1927): after a solo dispatch records (the `solo_dispatch` branch, line 1936), prepare the ticket verifier when the solo dispatch carries a `verifier` command (L2 and L3, set by `solo_run.py` near line 189) and print its dispatch JSON, at the level `steps.ticket_verifier` gives and against the dispatch's `tree`; an L1 solo (no `verifier`) prints `next: close <task dir> (python3 <scripts>/tickets.py close <task dir>)`.
  2. For a handoff outside a `step-<n>/` dir (the branch near line 1947): read the verdict with `verdict_word`. A ticket verifier `pass` prints `next: close ...` as above; a verifier `fail` prints `stop: fail <result path>; send its ## For the next attempt to the solo by name, then advance the solo's dispatch again`; a ui-designer review prints `next: <verdict> <result path>` for `pass` or `pass-with-notes` and `stop: changes-required <result path>` otherwise. Any other role keeps today's `next: <hint>` line.
  3. Update the `advance` usage lines (dispatch.py:6-8) and the `advance` sentences in `plugins/sdlc-lite/agents/conductor.md` (How you run roles, item 3, "a handoff outside a `step-<n>/` dir prints `next: <hint>`") and `plugins/sdlc-lite/skills/fanout/SKILL.md` line 52 so they say advance covers ticket-level completions.
- Non-goals: closing the ticket or sending the SendMessage from inside `advance`; changing the step-dir path; changing `record`.
- Done when: the criteria pass.

## Context
Source: GitHub issue #32 (finding on #9), ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- `advance` was used 0 times in 0.28.1 (0 of 3 completions). It only advances `step-<n>/` handoffs, which were 109 of 413 role completions (26%) in 0.27; the other 304 were ticket-level (solo 87, ticket verifier, ui-designer review 73, planner). For those it records and prunes, then prints only a hint.
- On main (8624f984): `advance` prints `next: a solo ticket; run its verifier or close it (tickets.py close)` for a solo (dispatch.py:1937) and `next: <dir> is not a step dir; read <result> and pick the next role` otherwise (dispatch.py:1948). The solo dispatch JSON already holds the ready verifier command in its `verifier` field (`plugins/sdlc-lite/scripts/solo_run.py:189`, null for L1).
- `verdict_word(d, attempt)` (dispatch.py:1810) returns the verdict key from the result through `results.key_value`.
- Existing selftest cases for advance: dispatch.py near line 3822 (`T-0645 advance on a verifier fail/pass/invalid`). They must keep passing.

## Constraints
The step-dir behavior of `advance` and its existing selftest cases are unchanged. `advance` still prepares at most one role per call and never closes a ticket.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with new cases: (a) advance on an L2 solo dispatch prints a verifier dispatch JSON whose `dispatch_file` exists; (b) advance on a ticket-level verifier `pass` prints a line starting `next: close` and writes no new dispatch file; (c) advance on a ticket-level verifier `fail` prints a line starting `stop: fail`. Each new case fails with the `advance` change reverted.
2. `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0.
3. `grep -n "advance" plugins/sdlc-lite/agents/conductor.md` shows the sentence naming ticket-level completions, and `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `git diff --check <base sha>` exits 0.
