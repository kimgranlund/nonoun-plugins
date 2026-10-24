---
id: T-0734
title: "One rule for which checkout owns each sdlc record"
type: chore           # feature | bug | chore | spike | idea
status: dropped     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every sdlc script resolves which checkout (primary, integration, lane worktree) owns a given record, config or bookkeeping file through one helper and one documented rule, so a writer and its reader can no longer disagree.

## Intent
- Do: write the rule in `docs/references/sdlc-internals.md` (one table: kind of state, owning tree, who writes, who reads), covering at least verifier and builder records, base-sha and end-sha, `.sdlc/config` (merge_gate, light_scope), ticket bookkeeping (branch:, worktree:, roadmap, router), and lane-close state. Add one helper (for example `wtroot.owner_tree(kind, ticket, cwd)`) and route `dispatch.py`, `fanout.py`, `lanes.py` and `steps.py` reads and writes of those kinds through it. Keep behaviour that the batch fixes (T-0713, T-0717, T-0720, T-0722, T-0723) already settled; this ticket makes it one rule.
- Non-goals: new features; changing what is recorded.
- Done when: the criteria pass. Split into one ticket per script if the change grows past a solo run.

## Context
Root-cause review 2026-10-22: 8 issues share one cause, the tools span three checkouts and each script picks its own: #46/#57 (lane close writes main, land merges integration), #55 (prepare --tree writes main, land reads lane), #58 (config on integration, land reads main), #59 (closed folder on integration, open copy in lane), #49 (build base vs lane start), #47 (end tree before a review fix). Each fix so far added a fallback.

## Acceptance criteria
1. The rule table exists in `docs/references/sdlc-internals.md` and names the helper.
2. `git grep -nE "records_dir|base-sha|end-sha|merge_gate" plugins/sdlc-lite/scripts/{dispatch,fanout,lanes,steps}.py` shows each read and write of those kinds going through the helper (list any deliberate exception in the Outcome).
3. A selftest case per kind writes from one tree and reads from another and passes; with the helper bypassed, at least one case fails (state it).
4. `dispatch.py`, `fanout.py`, `lanes.py` and `steps.py` selftests (through gate_lock), `check.py` and `check-packaging.py` pass; `git diff --check <base sha>` exits 0.

## Outcome
Split 2026-10-24 into T-0749 (rule and helper), then T-0750 (dispatch.py), T-0751 (fanout.py), T-0752 (lanes.py, steps.py), each a solo run.
