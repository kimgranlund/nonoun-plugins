---
id: T-0747
title: "advance prepares a prep solo's verifier on the lane worktree"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
For an L2 or L3 solo dispatched by `fanout.py prep`, `dispatch.py advance` prepares the ticket verifier on the lane's worktree (the tree and handoff copy the solo built in), the same tree the verifier command `prep` prints names.

## Intent
- Do: in `plugins/sdlc-lite/scripts/dispatch.py` `advance_solo` (about line 2215) and/or `fanout.solo_record` (about line 2180), record the lane tree in the solo dispatch file and have advance prepare the verifier with that tree (`prepare --tree <lane>` semantics). Add a selftest case from a prep-written solo file at L2. Keep T-0717's base resolution.
- Non-goals: L1 solos (no verifier step).
- Done when: the criteria pass.

## Context
T-0744 verifier-L2 (landed):
- decide: plugins/sdlc-lite/scripts/dispatch.py:2215 for an L2 or L3 prep solo, advance_solo prepares the ticket verifier against `handoff`, which `solo_record` sets to the main checkout's handoff (fanout.py:2180), not the sub-agent worktree; observed in the e2e run (verifier prompt `Handoff:` names the main-checkout path). The builder's Outcome already flags it as open; a new ticket.

## Acceptance criteria
1. A `dispatch.py` selftest case: advance on an L2 prep solo dispatch prepares a verifier whose brief `Tree:` and `Handoff:` name the lane worktree; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- `fanout.solo_record` takes the checkout `prep` ran in and records `tree` (`<top>/.claude/worktrees/<name>`) as a hint; `prep` passes `ctx['top']`.
- `dispatch.solo_lane_tree` settles the real worktree when `advance` runs (the host may name it `agent-<id>`): the listed `.claude/worktrees/agent-<agent id>` when `advance --agent-id` is given, else the worktree on branch `worktree-<name>` or `worktree-agent-<id>`, else the recorded tree if it is a listed worktree, else '' (the verifier prepares in main as before, never a refusal). `advance` passes its `--agent-id` through.
- `advance_solo` takes the verifier level from main's handoff (the solo under verification can edit the lane copy), checks a failed-verifier level in both task dirs, and uses the lane copy only for the brief's `Tree:` and `Handoff:`. A tree equal to the main checkout is still cleared; T-0717 base resolution is unchanged.
- Selftest cases (loop of four): `T-0747 advance on an L2 prep solo dispatch (named | lane copy drops the pin | agent-<id> worktree | no worktree) ...`.
- Negative controls, each fix reverted alone: recorded tree only gives `FAIL: ... (agent-<id> worktree) ...` and `FAIL: ... (no worktree) ...`; level read from the lane copy gives `FAIL: ... (lane copy drops the pin) ...`; both end `dispatch selftest: FAIL`.
- Checks: dispatch selftest (gate_lock) exit 0, fanout selftest PASS, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check 34a12178` exit 0.

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 0c63c93192b3
- Changed: see commits
- Commits: e59634c T-0747: resolve the prep solo tree at advance, take the verifier level from main; 9fabdac T-0747: advance prepares a prep solo's verifier on the lane worktree
- Check: 1 A `dispatch.py` selftest case: advance on an L2 prep solo dispatch prepares a verifier whose brie...: pass
- Check: 2 `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py ...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/dispatch.py:2307 the verifier brief's... -> notes.md
