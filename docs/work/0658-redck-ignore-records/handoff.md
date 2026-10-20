---
id: T-0658
title: "redck ignores record files when judging the tree dirty"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A builder's red checkpoint is `pre-edit` when the only changed files are sdlc record files: the ticket folder (handoff edits by the conductor, `skips.md`) and the ticket root never make the tree dirty.

## Intent
- Do: (1) In `dirty_paths` (`plugins/sdlc-lite/scripts/redck.py`), also leave out paths under the ticket folder of the handoff (`order.task_dir` of the handoff dir, which follows `work_root:`), so a step handoff in the records dir no longer counts its ticket's `handoff.md` and `skips.md` as source edits. (2) Update the `record` docstring line that lists what is left out. (3) Add a selftest case.
- Non-goals: having `prepare` commit pending record files. Any change to the test prelude rule or to audit statuses.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #18, ui-kit-neue audit 2026-10-20.
- Evidence: 28 builder results reported retrospective red checkpoints caused by conductor handoff edits or a `skips.md` left dirty in the lane (for example `0035-s2 builder-L4-2.md`, `0049-s1 builder-L3.md`); the same cause contributed to the T-0065 step-6 block.
- Partly fixed here: `dirty_paths` (`plugins/sdlc-lite/scripts/redck.py:122`) already leaves out `.sdlc/` and the handoff's own dir (`redck.py:135`). For a step build the handoff lives in the records dir (`.sdlc/runtime/tasks/<task>/step-<n>/`, `resolve` at `redck.py:77`), so the ticket folder under a `work_root:` such as `docs/work/<task>/` (its `handoff.md` and `skips.md`, which stays in the task folder per `plugins/sdlc-lite/scripts/dispatch.py:29`) still counts as dirty. `order.task_dir` (`order.py:110`) maps a records dir back to that folder, `work_root` included.
- The call site is `cmd_record` at `redck.py:200`.

## Constraints
A dirty source path outside the ticket folder and the ticket root still makes the control retrospective; the existing selftest cases keep passing.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/redck.py selftest` exits 0 with a new case: a fixture with `work_root: docs/work` in `.sdlc/config`, ticket folder `docs/work/0001-x/`, and a step handoff with a (red) criterion in `.sdlc/runtime/tasks/0001-x/step-1/`; after editing `docs/work/0001-x/handoff.md` and adding `docs/work/0001-x/skips.md`, `redck.py record` on the step records phase `pre-edit` with `dirty` empty, and with `src.txt` also edited it records `retrospective` with `dirty == ['src.txt']`. The pre-edit half fails with the change reverted (observed negative control, recorded in the Outcome).
2. `git diff --check` exits 0.
