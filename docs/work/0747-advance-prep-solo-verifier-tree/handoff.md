---
id: T-0747
title: "advance prepares a prep solo's verifier on the lane worktree"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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
