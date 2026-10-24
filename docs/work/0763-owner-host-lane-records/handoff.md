---
id: T-0763
title: "dispatch status and steps next from main see a host lane's records"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
From the main checkout, `dispatch.py status <task dir>` and `steps.py next <task dir>` of a ticket running in a Claude Code host worktree read its records from the host worktree (the owner tree), as they do for a lanes.py or fanout lane (T-0750, T-0755).

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/dispatch.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: from /Users/kimgranlund/Projects/nonoun/live036, `dispatch.py status .sdlc/add-div` printed `no attempts in .../live036/.sdlc/runtime/tasks/add-div` and `steps.py next .sdlc/add-div` exited 1 `no builder result and no .../runtime/tasks/add-div/handoff.md to read a level from`, while the records were in `.claude/worktrees/agent-a05ad66023f64f17f/.sdlc/runtime/tasks/add-div`. Check whether `wtroot.owner_trees` finds the host lane for the ticket (host record under `<lanes root>/host/`, `lanes_root:`), and fix the lookup.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A selftest case (wtroot, dispatch or steps): a ticket whose only lane is a host worktree with a host record; status and next from the primary checkout see its records; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Root cause: fanout prep writes the host record as `<lanes root>/host/<id>-solo.lane.json` for the tree `.claude/worktrees/<id>-solo` it predicts, but Claude Code names the tree `agent-<agent id>`; `wtroot.lane_record` looks a host record up by tree leaf, so no tree matched until `fanout.py land` rebinds the record after a merge (live036 T-0003 never merged). `wtroot.owner_trees` therefore fell back to primary for records, and `dispatch.py status` and `steps.py next` read the main checkout.

Fix: `wtroot._unbound_host_lane` (called from `owner_trees` when no tree's record lists the ticket): a host record listing the ticket whose name is no listed tree binds to the one host-owned `.claude/worktrees/agent-*` tree with no record; of several, the one holding the solo report `<lane>.md` under a `runtime/tasks/` dir; still ambiguous, none (primary, as before). No dispatch.py or steps.py logic changed. Doc: `docs/references/sdlc-internals.md` owner-tree paragraph.

Checks:
- New cases: `wtroot.py owner-selftest` (three T-0763 cases: one unbound tree, two unbound trees with no report stay primary, two with the report pick it) and `dispatch.py selftest` `host lane (T-0763): status and next on a main-checkout task dir read the records in the agent-<id> host worktree ...` (ok).
- Negative control, change reverted: `FAIL: a provisional host record and one unbound agent-* tree: that tree is the lane, from primary (T-0763)` and `FAIL: two unbound agent-* trees: the one holding the solo report <lane>.md is the lane (T-0763)`; the dispatch case's scenario run standalone on the reverted tree printed `no attempts in .../r/.sdlc/runtime/tasks/t763` and `steps next: no builder result ...` rc 1 (the full dispatch selftest was not rerun reverted).
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0 (PASS); `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0 (PASS); `git diff --check 12f046a9` exit 0; `wtroot.py selftest` ok.

Open: `steps.py next` on a solo task dir with no builder result still asks for a handoff level (same as for a lanes.py lane); not in scope.
