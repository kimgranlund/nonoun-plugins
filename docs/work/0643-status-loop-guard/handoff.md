---
id: T-0643
title: "plan_check fails fixed-interval status loops; driver prompt replaces them"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor watching running work is woken by role completion, never by a fixed-interval status loop: `plan_check.py loop` rejects such a loop and the plan skills offer an interval-free driver turn instead.

## Intent
- Do: (1) `check_loop` in `plugins/sdlc-lite/scripts/plan_check.py` gains FAIL `status-polls-running-work` for a fixed-interval loop whose prompt reads as a status or driver loop, with a message pointing to the driver prompt. (2) `skills/plan-loop/SKILL.md` and `references/loop-rules.md` drop the status-loop example, and `skills/run-plan/SKILL.md` names the interactive driver turn: run `plan_done.py <plan>`; exit 1: dispatch the first open item in the background and end the turn; exit 0, 2 or 4: stop and report. (3) A new `idle-wakes` finding in `plugins/sdlc-lite/scripts/traces/detectors/cost.py`, next to `polling-loop`, counts loop or cron fired conductor turns with an unchanged board and no dispatch, record, land or close.
- Non-goals: `board.py --changed` (optional item 3 of the T-0583 design; a separate ticket if a dynamic loop must stay). No change to `supervisor.py`, `messages.py` or `conductor.md`.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Design: `docs/work/.0583-event-driven-driver/handoff.md` `## Outcome` (verified 2026-10-19). Source lesson: maison's 10-minute check prompted "nothing moved" dozens of times. Verifier note: the status regex term `land` also matches "landed" and "upland"; test that a non-status loop containing such a word still passes. Before figure: run the `idle-wakes` detector over a maison 0597 conductor transcript if one is readable and record the count in the Outcome; if none is readable, say so.

## Constraints
Loops that are not status loops keep passing. Existing `polling-loop` behavior is unchanged.

## Acceptance criteria
1. `echo '/loop 10m status update since the last run; stop when all lanes landed' | python3 plugins/sdlc-lite/scripts/plan_check.py loop` exits non-zero and prints `status-polls-running-work` (red before the change: it printed `ok: loop plan passes`).
2. `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0 and covers: the status loop above fails, the same prompt with no interval passes, and `/loop 1h rotate logs on the upland host; stop when done` passes.
3. `python3 plugins/sdlc-lite/scripts/traces.py selftest` exits 0 with a case where `idle-wakes` fires on two unchanged fired turns and stays silent when a turn dispatches.
4. `grep -n '/loop 20m a status update' plugins/sdlc-lite/skills/plan-loop/references/loop-rules.md` finds nothing, and `grep -n 'plan_done.py' plugins/sdlc-lite/skills/run-plan/SKILL.md` names the driver turn.
5. `git diff --check` exits 0 and `python3 scripts/check-packaging.py` exits 0.
