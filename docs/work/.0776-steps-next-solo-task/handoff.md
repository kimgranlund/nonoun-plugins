---
id: T-0776
title: "steps.py next works on a solo ticket task folder"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py next <task dir>` on a solo ticket (no planner, no builder step) reads the level from the ticket handoff and reports the solo/verifier state, from main and from the lane, instead of failing.

## Intent
- Do: reproduce first (a selftest case built from the observation), then the smallest fix in `plugins/sdlc-lite/scripts/steps.py` and its docs.
- Non-goals: other rehearsal findings.
- Done when: the criteria pass.

## Context
Observed: `steps next: no builder result and no .../runtime/tasks/add-div/handoff.md to read a level from` (rc=1), both from main and on the lane-redirected path; the handoff is `.sdlc/add-div/handoff.md`, not under runtime/tasks. T-0763 noted the same as out of scope.

Evidence: the second 0.36 release rehearsal 2026-10-25 (sdlc-lite b7c64749) in /Users/kimgranlund/Projects/nonoun/live036b (state kept, read-only); report /Users/kimgranlund/Projects/nonoun/live036b-run/report.md, log /Users/kimgranlund/Projects/nonoun/live036b-run/log.md.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `steps.py` selftest case reproduces the observation and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`steps.py next` on a solo ticket's task dir (ticket handoff with front matter `size:`, no `level:` line, no planner or builder result) now reads the solo report the way prep and dispatch write it: `<id>-solo.md` in the records dir (no `-L<n>`, no result header, no `## Output`, usually no runs.jsonl row; an older `solo-L<n>.md` still works), with the tier and the verifier from the newest solo `*.dispatch.json` (`dispatch.solo_dispatch`; a null `verifier` is an L1 solo, as `dispatch.advance_solo` reads it) and blocked from the report's first non-blank line (`dispatch.solo_blocked`). Routes: no report -> `solo L<size>`; blocked -> `stop`; no verifier -> `close` for L1, else `verify L<ticket verifier level>`; verifier pass -> `close`, fail -> `stop`, no verdict -> `reverify`. The records dir (`.sdlc/runtime/tasks/<name>`) given as the argument maps to the task folder for the handoff. The handoff comes from the dir given, the task folder or the lane twin, the results through `records_of` (T-0755). The step-dir routes (T-0766, T-0781) are unchanged. Docs: `next` usage text in `steps.py`, `skills/chain/references/step-rules.md`.

Read-only run in /Users/kimgranlund/Projects/nonoun/live036b with this tree's steps.py, `steps.py next .sdlc/add-div` and `steps.py next .sdlc/runtime/tasks/add-div`, both exit 0 and both print:
```
close
reason: newest verifier verifier-L2.md passed; close the ticket
read: .sdlc/runtime/tasks/add-div/T-0003-solo.md
read: .sdlc/add-div/handoff.md
read: /Users/kimgranlund/Projects/nonoun/live036b/.sdlc/runtime/tasks/add-div/verifier-L2.md
```

Checks: `steps.py selftest` through gate_lock exit 0; `check.py` exit 0; `scripts/check-packaging.py` exit 0; `git diff --check f7d88cd3` exit 0.
Negative control (the `next_action` solo hook reverted in a scratch copy): selftest FAIL, 11 cases; the add-div case reads `FAIL: next solo (T-0776): the live036b add-div shape (T-0003-solo.md, verifier-L2.md pass, runs.jsonl with only the verifier row) -> close`.
Not covered: a lane records dir that holds only a solo report and its dispatch record (no result file, no runs.jsonl) is not taken as the records owner by `records_of`/`order._legacy`; it counts once a verifier result or runs.jsonl is there. A ticket handoff present only in the lane tree is not found either (no ticket id above the path in main).

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: f7d88cd3b486
- Changed: see commits
- Commits: 0960c28 T-0776: read the solo report the way dispatch writes it; 1d61316 T-0776: steps.py next works on a solo ticket task folder
- Check: 1 A `steps.py` selftest case reproduces the observation and passes; with the change reverted it fai...: pass
- Check: 2 selftest through gate_lock exits 0, `check.py` exits 0, `check-packaging.py` passes, `git diff --...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/steps.py:3283 and :3317 call... -> notes.md
- Follow-up: note: import dispatch is local to solo_report/solo_ticket_action and... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/tickets.py:2396 also has a solo_reportd... -> notes.md
