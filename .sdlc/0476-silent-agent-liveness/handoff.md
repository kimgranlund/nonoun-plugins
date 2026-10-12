---
id: T-0476
title: "dispatch.py started and status last-activity age for silent agents (T-0470 finding 5)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A running attempt whose sub-agent transcript has not been written for 30 minutes shows as `silent` in `dispatch.py status`, with its last-activity age.

## Repro
Make a running attempt with a stored agent id and a fake `subagents/agent-<id>.jsonl` dated 2 h back; run `dispatch.py status`.

## Expected
`running`, `last activity 2h`, `silent`.

## Actual
`running` and nothing else.

## Context
Origin: T-0470 investigation, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`. Report item 5. Two pieces: `dispatch.py started <dispatch.json> --agent-id ID` writes the id into the running attempt at spawn (today the id lands only at `record`, `dispatch.py:1055`); `status` reads the transcript mtime (`dispatch.py:463-471`, `:1009`). The conductor wording (`agents/conductor.md:38`, the stop, `record --no-result`, `prepare` ladder) is T-0461 scope.

## Constraints
The failing test lands before or with the fix, with an observed-red control. No prompt wording change.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, including the T-0476 cases: `started` stores the agent id in a running attempt; `status` of a running attempt with a transcript 2 h old prints `last activity 2h` and `silent`; negative controls (2 min old, 29 min old, no transcript) print no `silent` (and no `last activity` when no transcript).
- Observed red: with the `started` and `status` changes removed, those cases fail (recorded: 5 FAIL before the change).
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- No agent or skill prompt wording changed (`git diff --stat` touches only `dispatch.py`, `docs/references/sdlc-internals.md`, and this ticket folder).
