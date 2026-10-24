---
id: T-0751
title: "fanout.py reads config and records through the owner-tree helper"
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
Every read and write of `.sdlc/config` keys (merge_gate, light_scope), records dir, base-sha, lane-close state in `plugins/sdlc-lite/scripts/fanout.py` goes through the owner-tree helper from T-0749, so a writer and its reader can no longer pick different checkouts.

## Intent
- Do: replace each local choice of tree for those kinds with a call to the helper; keep current behaviour (the selftests that pin T-0713, T-0717, T-0720, T-0722, T-0723 and later fixes stay green). Where a fallback only existed to paper over a tree mismatch the helper now settles, remove it.
- Non-goals: other scripts; new features; changing what is recorded.
- Done when: the criteria pass.

## Context
Split from T-0734 (root-cause review 2026-10-22): 8 issues share one cause, the tools span three checkouts (primary, integration, lane worktree) and each script picks its own: #46/#57 (lane close writes main, land merges integration), #55 (prepare --tree writes main, land reads lane), #58 (config on integration, land reads main), #59 (closed folder on integration, open copy in lane), #49 (build base vs lane start), #47 (end tree before a review fix). Each fix so far added a fallback. Settled behaviour to keep: T-0713, T-0717, T-0720, T-0722, T-0723, T-0740, T-0744, T-0745, T-0747, T-0748.

## Acceptance criteria
1. `git grep -nE "records_dir|base-sha|end-sha|merge_gate|light_scope" plugins/sdlc-lite/scripts/fanout.py` shows each read and write of those kinds going through the helper; the Outcome lists any deliberate exception with its reason.
2. A selftest case writes one kind from one tree and reads it from another through the script's own entry point and passes; with the helper call bypassed it fails (state the FAIL line).
3. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 for fanout, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Change: `plugins/sdlc-lite/scripts/fanout.py` gets `owner_dirs(ctx, kind, ticket, lane)` (the existing trees of `wtroot.owner_rule(kind)['trees']`, named by `wtroot.owner_trees`) and `owner_root` (ctx root mapped into the owner tree). `config_root` is removed.
- config (`merge_gate`, `light_scope`): run and prep preflight and land preflight set `ctx['cfg_root']` through `owner_root(..., 'config')`; `light_refusal` and `gate_class` read only that (no `ctx['root']` default). Per the table's owner, run and prep now read the integration worktree's config when they reuse one (the #58 note for `fanout.py run`); with no integration worktree yet it is the primary, as before.
- records: `land_ticket` copies from and carries to, and `branch_verdict` falls back to, the trees of the `records` row (lane, then primary); `merge_gate_close` copies the trail and records from the row's lane and mirrors closed records to the row's primary (was `ctx['top']`, wrong when run from a worktree).
- lane-close: the three `lanes.close_lane` calls take `cwd` from the `lane-close` row (primary; was the current tree).
- Helper gap (not edited, T-0750 owns wtroot.py): `owner_trees` finds the integration and lane trees only through a lane record, so a landed branch with no `.lane.json` (the T-0722 fixture) gets primary for config. `owner_dirs` fills a None slot from the run's own `integ_dir` and lane worktree. A `trees=` override on `owner_tree` would remove that. `wtroot.OWNERS` config row (lines 308-309) still names `config_root` and the `fanout.py run` disagreement; the internals table row is updated, OWNERS needs the same edit.
- Exceptions kept: `branch_base` reads `base-sha` from git objects on the lane ref, not a checkout. `end-sha` does not occur in fanout.py. prep's dispatch records (`subagent_dispatch`, `solo_record`, the `.dispatch.json` write) go to the tree prep runs in before any lane exists, which the row's fallback names primary when prep runs there. `verifier_files`, `price_solo_row` and `host_branch_ticket` take a task dir or search every tree. Integration-internal moves (`merge_gate_close` close read, `move_closed_records`, run's seeding of lane records from `ctx['top']`) stay in one tree. The T-0720 primary verdict fallback stays (settled by T-0750's writer, and its selftest pins it).
- Criterion 2: new selftest case `T-0751 owner tree`: the integration worktree commits `merge_gate: light`, main lacks it, `fanout.py prep --light-gate true` from primary passes. Negative control (scratch copy, preflight `cfg_root = root`): `fanout selftest: FAIL`, `- T-0751 owner tree: prep --light-gate reads merge_gate: light from the reused integration worktree, not the primary checkout, got rc=2 err='fanout: --light-gate needs a `merge_gate: light` line in .../light-integ/.sdlc/config ...'`, the only failing case.
- Checks: `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0 (`fanout selftest: PASS`); `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check 257cf42c` exit 0.
