---
id: T-0613
title: "steps.py lint flags another repo's verifier file as the step's own result"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-17
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lint` no longer reports "reads this step's own verifier result" for a criterion that cites a verifier file in another repository (an absolute path outside this repo), and a test that failed before the fix passes after it; the T-0415 own-result case still fails.

## Repro
1. Write a step handoff whose criterion is `` `test -s /Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/runtime/tasks/0247-validate-payload-persona-ids/verifier-L1.md` ``.
2. `python3 plugins/sdlc-lite/scripts/steps.py lint <handoff>`.

## Expected
`steps lint: ok` (the file belongs to another repo's ticket, not this step).

## Actual
`acceptance criterion reads this step's own verifier result, so it can pass only after the verifier passes` and exit 1; renaming to `verifier-L1.attempt.json` fails the same way.

## Context
Found writing the 2026-10-17 fleet retro verify handoff (`.sdlc/runtime/tasks/fleet-retro-2026-10-17/verify/handoff.md`); worked around with a `runs.jsonl` count. Rule text is `plugins/sdlc-lite/scripts/steps.py` lines 148 to 155 (T-0415): any span holding `verifier-L<digit>` with no other `step-<m>/` folder matches. Guess: exempt absolute paths outside the repo root, as the T-0536 rule already does.

## Constraints
The failing test lands before or with the fix, never after.
