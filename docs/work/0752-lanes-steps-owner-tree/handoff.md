---
id: T-0752
title: "lanes.py and steps.py read and write records through the owner-tree helper"
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
Every read and write of records dir, base-sha, ticket bookkeeping (branch:, worktree:) in `plugins/sdlc-lite/scripts/lanes.py` and `plugins/sdlc-lite/scripts/steps.py` goes through the owner-tree helper from T-0749, so a writer and its reader can no longer pick different checkouts.

## Intent
- Do: replace each local choice of tree for those kinds with a call to the helper; keep current behaviour (the selftests that pin T-0713, T-0717, T-0720, T-0722, T-0723 and later fixes stay green). Where a fallback only existed to paper over a tree mismatch the helper now settles, remove it.
- Non-goals: other scripts; new features; changing what is recorded.
- Done when: the criteria pass.

## Context
Split from T-0734 (root-cause review 2026-10-22): 8 issues share one cause, the tools span three checkouts (primary, integration, lane worktree) and each script picks its own: #46/#57 (lane close writes main, land merges integration), #55 (prepare --tree writes main, land reads lane), #58 (config on integration, land reads main), #59 (closed folder on integration, open copy in lane), #49 (build base vs lane start), #47 (end tree before a review fix). Each fix so far added a fallback. Settled behaviour to keep: T-0713, T-0717, T-0720, T-0722, T-0723, T-0740, T-0744, T-0745, T-0747, T-0748.

## Acceptance criteria
1. `git grep -nE "records_dir|base-sha|end-sha|merge_gate|light_scope" plugins/sdlc-lite/scripts/lanes.py and plugins/sdlc-lite/scripts/steps.py` shows each read and write of those kinds going through the helper; the Outcome lists any deliberate exception with its reason.
2. A selftest case writes one kind from one tree and reads it from another through the script's own entry point and passes; with the helper call bypassed it fails (state the FAIL line).
3. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/{lanes,steps}.py selftest` exits 0 for lanes and steps, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
