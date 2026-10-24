---
id: T-0763
title: "dispatch status and steps next from main see a host lane's records"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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
Root cause: fanout prep writes the host record `<lanes root>/host/<id>-solo.lane.json` for the tree `.claude/worktrees/<id>-solo` it predicts, but Claude Code names the tree `agent-<agent id>`. `wtroot.lane_record` reads a host record by the tree it names, so no tree matched until `fanout.py land` rebinds the record after a merge (live036 T-0003 never merged); `dispatch.py status` and `steps.py next` read the main checkout.

Replan (the one replan): the first build guessed the tree in wtroot (`_unbound_host_lane`); the verifier showed it binds ticket A to ticket B's tree. Now the binding is deterministic: `fanout.rebind_host_record` (extracted from `land_lanes`, which now calls it) renames the provisional record to `agent-<agent_id>.lane.json` on that tree's branch, keeping into and base; `dispatch.py record` and `advance --agent-id` on a prep solo dispatch call it through `rebind_solo_host`, only when `.claude/worktrees/agent-<agent_id>` is a listed worktree and the provisional record exists. The wtroot lookup stays exact (record names the tree). Doc: `docs/references/sdlc-internals.md` (fanout sub-agent lanes paragraph). Main merged in first (T-0756, T-0760 kept).

Checks:
- New cases: `wtroot.py owner-selftest` `a provisional host record binds no agent-* tree it does not name ... (T-0763)`; `dispatch.py selftest` `T-0763 two prep solos in flight, before advance: A is unbound ...` and `T-0763 advance --agent-id on A's prep solo rebinds host/T-0763-solo.lane.json to agent-aaa ...; B stays unbound` (ok).
- Red controls: with the `rebind_solo_host` call reverted, the full dispatch selftest exits 1 with `FAIL: T-0763 advance --agent-id on A's prep solo rebinds ...`; with the old guess restored in wtroot, `FAIL: a provisional host record binds no agent-* tree it does not name: records stay in primary until dispatch.py rebinds it (T-0763)`, and the two-solos setup run standalone binds A to agent-aaa before advance (status lists A's builder, so the `before advance` case fails).
- Through gate_lock: dispatch selftest exit 0 (PASS), fanout selftest exit 0 (PASS), wtroot selftest ok; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 12f046a9` exit 0.

Re-verify fix (verifier-L2-2): `fanout.py land` called `rebind_host_record` again after record/advance had rebound the record, rewriting it with the land-time base and printing a false `rebound from` line. `rebind_host_record` is now a no-op (returns None, writes nothing) when `<leaf>.lane.json` exists and the provisional record does not; `land_lanes` and `rebind_solo_host` print only a returned line. New assertion in `fanout.py selftest` case 30b: record --agent-id y rebinds to agent-y, main moves on, land keeps base_sha and prints no `rebound from`. Red with the guard removed: `fanout selftest: FAIL` on `case 30b host worktree (T-0763): record --agent-id y rebinds ... keeps its base_sha and prints no second rebound line`. Through gate_lock: fanout selftest exit 0, dispatch selftest exit 0; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 12f046a9` exit 0.

Open: before the solo's advance or record, status and next from main still read main (no agent id yet; by design). `steps.py next` on a solo task dir with no builder result asks for a handoff level, as for any lane; not in scope.

## Outcome

2026-10-24 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: a71e43a24934
- Changed: see commits
- Commits: 69901be T-0763: land keeps a host record that record/advance already rebound; 9b0079e T-0763: rebind a prep solo's host record at record/advance --agent-id; e59f14b T-0763: dispatch status and steps next from main see a host lane's records
- Check: 1 selftest case: a host-worktree ticket's records are seen by status and next from the primary chec...: pass
- Check: 2 gate commands: pass
- Follow-up: note: the case 30b selftest assertion was not seen red with the guard... -> notes.md
