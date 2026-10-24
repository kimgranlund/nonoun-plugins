---
id: T-0752
title: "lanes.py and steps.py read and write records through the owner-tree helper"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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

## Outcome
- lanes.py routes its record trees through `wtroot.owner_tree`: `record_tree` (open: the tree owning `branch` for the new lane), `do_close` and `clear_integration_record` (the `branch` owner, resolved before the tree is removed), `carry_lane_records` (from the `records` owner into the `lane-close` owner), `finish` step 1 and 2 (`records` owner) and `ticket_verdict` in `list` (`records` owner for the ticket). New helper `lanes.owner_root`. It asks with the lane tree as cwd (ticket None), so it does not depend on the ticket search; lanes.py does not import back into wtroot, so no cycle.
- steps.py: new `owned(kind, path)` (ticket from the nearest front matter `id:`; local `import wtroot`, path unchanged beside no wtroot.py); `base_sha` reads `base-sha` through it. Docs: `docs/references/sdlc-internals.md` lanes.py and steps.py sections.
- Criterion 1 exceptions: `carry_records` and `runtime_records` (lanes.py 825 to 859) take folders their callers already routed, and fanout.py calls `carry_records` too; `steps.records_of` and `step_handoff` (records reads of every subcommand) stay in the tree of the dir given, because `exec_toplevel` already maps a main step dir to the lane and routing them would change what `next` and `resume` read from main (a new ticket if wanted). No `end-sha`, `merge_gate` or `light_scope` read exists in either script; the lanes.py `.sdlc/config` keys are lane keys, not the `config` kind, and stay a main checkout read. `do_close` still clears `branch:` in main for a ticket the owner tree did not clear (T-0713, the row's fallback tree).
- Kept fallback: a lane whose tree is already gone has no record for the helper to read, so `clear_integration_record` takes the worktree holding its into branch, as before. The helper's host record lookup ignores `lanes_root:` until T-0750 lands, so a host lane under a custom `lanes_root:` resolves to primary here.
- Criterion 2: steps.py selftest `owner tree (T-0752): swap on the main step dir reads the base-sha the lane that owns it recorded` passes; with `owned('base-sha', step_dir)` replaced by `pathlib.Path(step_dir)` it fails: `steps selftest: FAIL, these did not hold: - owner tree (T-0752): swap on the main step dir reads the base-sha the lane that owns it recorded`.
- Criterion 3: `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exit 0, same for steps.py exit 0, `python3 plugins/sdlc-lite/scripts/check.py` exit 0, `python3 scripts/check-packaging.py` exit 0, `git diff --check 257cf42c` exit 0.

## Outcome

2026-10-24 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 257cf42cc71b
- Changed: see commits
- Commits: 28278a1 T-0752: lanes.py and steps.py read and write records through the owner-tree helper
- Check: 1 grep of records_dir|base-sha|end-sha|merge_gate|light_scope routes through the helper, exceptions...: pass
- Check: 2 selftest writes one kind from one tree and reads it from another through the script's entry point...: pass
- Check: 3 selftests, check.py, packaging, diff --check: pass
- Follow-up: decide: Conductor check existing selftests unchanged: the... -> notes.md
- Follow-up: decide: Conductor check plain solo flow: in a throwaway repo I ran the new... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/lanes.py:1431: a host lane under a custom... -> notes.md
