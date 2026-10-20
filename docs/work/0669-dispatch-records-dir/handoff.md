---
id: T-0669
title: "Dispatch and skip records go to the records dir, not the work root"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ticket's work-root folder holds only tracked ticket records: solo dispatch records go to the records dir, close leaves no undotted sibling folder, and `tickets.py check` flags an undotted folder that has no `handoff.md`.

## Intent
- Do: (1) `fanout.py prep` writes the solo `<name>.dispatch.json` to `order.records_dir(taskdir, create=True)` instead of the task folder, as `solo_run.dispatch_json` already does, and `branch_base` reads it from there (or falls back as it does when none is committed). (2) `tickets.py close` (both the verified and the reason path), after the dot-rename, moves any files left in an undotted `<NNNN>-<slug>` sibling into the records dir and removes the empty folder, printing one line per move. (3) `tickets.py check` warns `warning: <folder>: undotted folder with no handoff.md` for such a folder in the work root.
- Non-goals: moving existing folders in other repos (check's warning is the migration path). Changing `order.records_dir`.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #29, ui-kit-neue audit 2026-10-20.
- Evidence: 11 git-ignored `docs/work/00NN-*/T-00NN-solo.dispatch.json` folders (0014 to 0062) and a tracked `docs/work/0012-.../skips.md`, all for closed tickets; `ls docs/work` showed 14 open-looking folders against 3 open tickets.
- Partly fixed here: `solo_run.dispatch_json` writes to the records dir (`plugins/sdlc-lite/scripts/solo_run.py:203`), and close moves `skips.md` into the records dir (`move_skips`, `plugins/sdlc-lite/scripts/tickets.py:2155`, called at `tickets.py:3506` and `:3685` before `d.rename(dot)` at `:3508` and `:3687`). Still writing into the task folder: `fanout.py prep` at `plugins/sdlc-lite/scripts/fanout.py:2066-2068` (`taskdir / f"{d['name']}.dispatch.json"`). `branch_base` (`fanout.py:2506-2530`) reads a committed solo dispatch record from the lane branch's task folder; records-dir files are git-ignored, so keep its fallback to the fork point and say so in its docstring.
- The spawn gate already looks in the Artifacts dir first, then beside the handoff (`plugins/sdlc-lite/hooks/block-role-spawn.sh:103-118`); the solo prompt (`SOLO_SUBAGENT_PROMPT`, `fanout.py:499`) has a `Handoff:` line but no `Artifacts dir:` line, so add one naming the records dir, or the gate will not find the moved record. Run `bash plugins/sdlc-lite/scripts/hook-selftest.sh`.
- `order.py records-dir <dir>` prints the records dir (`plugins/sdlc-lite/scripts/order.py:440`). `tickets.py check` is `cmd_check` at `tickets.py:3840`; its warning list starts at `tickets.py:3855`.

## Constraints
The spawn gate still finds every solo record. Tracked files in a folder are never deleted; only untracked or ignored record files move. A legacy task dir that keeps records in place (`records_dir` returns the folder itself) is left alone.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with a case that `fanout.py prep` leaves no `*.dispatch.json` in the task folder and one in its records dir; it fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with cases: close of a ticket with an undotted sibling holding a `*.dispatch.json` leaves no undotted folder and the file in the records dir; `check` on a work root with an undotted folder and no `handoff.md` prints `undotted folder with no handoff.md`. Both fail with the change reverted.
3. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0, including a case where the spawn gate finds a solo record in the Artifacts dir.
4. `git diff --check` exits 0.
