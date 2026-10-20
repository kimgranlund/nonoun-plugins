---
id: T-0583
title: "Driver loop wakes on role completion or state change, not timed polling"
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor running a plan or wave wakes when a role finishes or the board changes, not on a timer, so idle "nothing moved" turns go away.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, item 5. maison's 10-minute check prompts repeated "nothing moved" dozens of times. Claude Code already re-invokes the parent when a background sub-agent finishes. The waste is in timed status loops layered on top. Idea ticket: shape before building.

## Intent
- Do: propose the smallest mechanism, for example a `supervisor.py`/`messages.py` event that the conductor's loop waits on, plus a built-in plan-driver prompt, and the change to `/board` or skill guidance that retires fixed-interval polling.
- Non-goals: building it in this ticket.
- Done when: a design note in the Outcome names the mechanism, the files it touches, and a measurable before/after (turns per wave).

## Constraints
None.

## Acceptance criteria
1. The Outcome holds the design: mechanism, files, and the metric to measure.

## Outcome

Design note, 2026-10-19. No code in this ticket; the build is a follow-up ticket.

### Where the waste comes from
- The wake channel already exists. On Claude Code a background Agent or background Bash re-invokes the session when it ends (`plugins/sdlc-lite/agents/conductor.md:40`), and `conductor.md:79` already forbids timed status polling. A headless driver (`run-plan`, fanout under `SDLC_HEADLESS=1`) blocks in the foreground and has no timer either.
- The gap is the layer on top. `plan-loop` still sells "a status loop" in its description, `skills/plan-loop/references/loop-rules.md:16` uses `/loop 20m a status update ...` as its example, and `plan_check.py check_loop` (`plugins/sdlc-lite/scripts/plan_check.py:244`) passes any fixed-interval status prompt. maison's 10-minute check is that pattern: each fire re-rendered an unchanged board.
- No new event source is needed. `messages.py wait` is itself a 1 to 5 second poller capped at 600 s, and `supervisor.py watch` wakes a headless host for mailbox mail; neither is a conductor wake, and adding a third poller would move the waste, not remove it.

### Mechanism (smallest change)
1. Guard: `check_loop` gains a FAIL `status-polls-running-work` when the loop has a fixed interval and the prompt reads as a status or driver loop (`status|board|progress|moved|waiting on|land|dispatch`). The message says: end the turn, the role's completion notification wakes you; for a plan, use the driver prompt below.
2. Built-in driver prompt: `plan-loop` and `run-plan` name one interactive driver turn, in words: "run `plan_done.py <plan>`; exit 1: dispatch the first open item in the background, then end the turn; exit 0, 2 or 4: stop and report". It has no interval: the completion notification is the only wake. `/board` prints once per wake, after `dispatch.py record`, not on a clock.
3. State-change no-op (optional, only if a dynamic loop must stay, for example to watch lanes another session owns): `board.py --changed` exits 0 when any row differs from the per-root state file `board.py` already keeps (`board.py:68`, `state_path` at `board.py:442`) and 3 when nothing changed, printing nothing. A fire that gets 3 ends in one tool call with no report.

### Files the build ticket touches
- `plugins/sdlc-lite/scripts/plan_check.py` (`check_loop`, plus a selftest case and its negative control)
- `plugins/sdlc-lite/skills/plan-loop/SKILL.md` and `references/loop-rules.md` (drop the status-loop example, route "watch a running wave" to the driver prompt)
- `plugins/sdlc-lite/skills/run-plan/SKILL.md` (the interactive driver turn)
- `plugins/sdlc-lite/scripts/board.py` (`--changed`, only with item 3)
- `plugins/sdlc-lite/scripts/traces/detectors/cost.py` (new finding `idle-wakes`, next to `polling-loop`)
- Unchanged: `supervisor.py`, `messages.py`, `conductor.md:79` (the rule already in force).

### Metric
- Idle wakes per wave: conductor turns started by a loop or cron fire whose `board.py --summary` line equals the previous turn's and that make no dispatch, record, land or close call. The `idle-wakes` detector counts them per wave from the conductor transcript.
- Turns per wave: all conductor turns from the first dispatch to the last close in the wave.
- Before: maison's 0597 wave, measured by running the detector over its conductor transcript (the lesson says "dozens"; no exact count is recorded). After: 0 idle wakes per wave, and turns per wave at most dispatches plus completions plus one close-out turn.
- Negative control: `/loop 10m status update since the last run; stop when all lanes landed` piped to `plan_check.py loop` must FAIL with `status-polls-running-work`; the same prompt with no interval and a non-status loop (`/loop 1h rotate logs; stop when ...`) must still pass.

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: docs/work/0583-event-driven-driver/handoff.md Metric: the "before" baseline is a measurement procedure (run the idle-wakes detector over maison's 0597 transcript), not a recorded number; acceptable for a design ticket, and the build ticket should record the figure. | note: docs/work/0583-event-driven-driver/handoff.md Mechanism item 1: the proposed regex term `land` also matches "landed"/"upland"; the build ticket's selftest should include a non-status loop containing such a word to check it does not over-fire.) · verifier: verifier-L2 (sonnet) · base: ab9c6afd1857
- Changed: see commits
- Commits: ad6d50c T-0583: design note for an event-driven driver loop
- Check: 1 The Outcome holds the design: mechanism, files, and the metric to measure: pass
