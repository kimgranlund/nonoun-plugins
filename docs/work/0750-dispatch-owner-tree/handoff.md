---
id: T-0750
title: "dispatch.py reads and writes records through the owner-tree helper"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0749]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every read and write of records dir, base-sha, end-sha in `plugins/sdlc-lite/scripts/dispatch.py` goes through the owner-tree helper from T-0749, so a writer and its reader can no longer pick different checkouts.

## Intent
- Do: replace each local choice of tree for those kinds with a call to the helper; keep current behaviour (the selftests that pin T-0713, T-0717, T-0720, T-0722, T-0723 and later fixes stay green). Where a fallback only existed to paper over a tree mismatch the helper now settles, remove it.
- Also: make the helper's host-record lookup in `wtroot.py` honour `lanes_root:` the way `lanes.config` (lanes.py about line 373) and `lanes.discover` do, so routing `dispatch.lane_record_base` through it keeps finding host lanes (T-0749 verifier decide); add a helper selftest case with `lanes_root:` set. This ticket is the only one of T-0750 to T-0752 that edits `wtroot.py`.
- Non-goals: other scripts; new features; changing what is recorded.
- Done when: the criteria pass.

## Context
Split from T-0734 (root-cause review 2026-10-22): 8 issues share one cause, the tools span three checkouts (primary, integration, lane worktree) and each script picks its own: #46/#57 (lane close writes main, land merges integration), #55 (prepare --tree writes main, land reads lane), #58 (config on integration, land reads main), #59 (closed folder on integration, open copy in lane), #49 (build base vs lane start), #47 (end tree before a review fix). Each fix so far added a fallback. Settled behaviour to keep: T-0713, T-0717, T-0720, T-0722, T-0723, T-0740, T-0744, T-0745, T-0747, T-0748.

## Acceptance criteria
1. `git grep -nE "records_dir|base-sha|end-sha|merge_gate|light_scope" plugins/sdlc-lite/scripts/dispatch.py` shows each read and write of those kinds going through the helper; the Outcome lists any deliberate exception with its reason.
2. A selftest case writes one kind from one tree and reads it from another through the script's own entry point and passes; with the helper call bypassed it fails (state the FAIL line).
3. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 for dispatch, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Helper: `dispatch.owned_records(directory, tree, kind)` asks `wtroot.owner_tree(kind, <ticket id>, <execution tree>)` and returns the records dir of the handoff dir at the same path in that tree. `prepare` (records, lock, settle, `next_stem`, `row_before`, the time gate's `ticket_minutes`), `build_base` (base-sha read), the base-sha write, the end-sha read and clear, and the end-sha writes in `record` and `record --update` all go through it.
- Table owner followed: records, base-sha and end-sha are owned by the lane. `prepare --tree <lane>` for a main-checkout handoff now records in the lane twin (#55). Before this, it recorded in primary. A handoff run from a lane cwd (T-0381) also records in the lane now.
- Fallback removed: the T-0717 twin base-sha read in `build_base` is gone, because the owner dir is already the twin. The twin handoff read for a named `base:` stays, since handoff is not a routed kind. `lane_record_base` now calls `wtroot.lane_record` and no longer goes through `lanes.discover`.
- wtroot: `lanes_root`, `host_dirs` and `lane_record` find host records under a `lanes_root:` line the way `lanes.config` and `lanes.host_dirs` do, legacy roots included. Host dirs are resolved once per `owner_trees` call. `owner_trees` also takes the current linked tree as the lane when no lane record lists the ticket, as its docstring already said. Without this, a lane with no record would have sent its records to primary.
- Deliberate exceptions in the criterion-1 grep. Each one reads the records dir of a path its caller names, so the caller picks the tree: `step_build` (plan_done, newest builder), `handoff_records` and the status `try` hint (CLI arguments), `prune_solo_name` (fanout picks the dirs), the `build_base` twin `task_dir` lookup (handoff, not records), and the selftest `R`. `ticket_minutes` reads the union of the handoff dir's records and the owner's records, deduplicated by attempt_id, so runs recorded before T-0750 still count. `merge_gate` and `light_scope` do not occur in dispatch.py.
- Still open: #49 is settled only for the tree mismatch. A verifier with nothing recorded still gets the lane start. #47 is about timing, not tree choice, so it is unchanged. `budget.report` (budget.py) reads runs.jsonl outside this scope.
- Fixtures moved, intent kept: the T-0381 cases write their recorded base in the lane twin (`lbase`), the T-0748 lane4 cases in `R(lw4 ...)`, and primary base-sha is cleared before them. Those fixtures had encoded the #55 mismatch.
- Criterion 2: new case `owner tree (T-0750): base-sha written by prepare --tree <lane> from the main checkout is read by a verifier prepared inside the lane`, which passes. The control replaced the helper call with `owner = None` in a detached copy (`<worktree root>/tmp/T-0750-negctl`). Result: `FAIL: owner tree (T-0750): base-sha written by prepare --tree <lane> from the main checkout is read by a verifier prepared inside the lane, got builder rc=2 base=None, verifier rc=0 base=6802a7424e53 (start 6802a7424e53, built 8ca2706b19a7)`. The T-0381 and T-0717 lane base-sha cases also fail in the copy.
