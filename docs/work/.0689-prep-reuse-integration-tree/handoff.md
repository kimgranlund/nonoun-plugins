---
id: T-0689
title: "fanout.py prep --integration reuses an existing integration worktree"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py prep --integration <branch>` and the `fanout.py land` calls it prints work with an integration branch that is already checked out in its own worktree (as `lanes.py open <name> --kind integration` leaves it), instead of refusing because git cannot check the branch out twice.

## Intent
- Do: (1) in `preflight` (`plugins/sdlc-lite/scripts/fanout.py:756`), when the integration branch is checked out in a worktree other than the main checkout, use that worktree as `integ_dir` (skip the refusal at fanout.py:876 and the `integ_dir exists` refusal at fanout.py:879 for it) and print `integration worktree: <path> (reused)`; keep refusing when it is checked out in the main checkout. (2) In `land_preflight` (fanout.py:2300), accept the same existing worktree as `integ_dir` instead of refusing at fanout.py:2338 (`land works in <lanes-dir>/integration`), with the same main-checkout refusal; `merge.lock` stays under the lanes dir. (3) A selftest case: `lanes.py open <name> --kind integration`, then `prep --integration <that branch>` exits 0 and names the reused path, and `land` of a finished lane merges into that worktree; the case fails with the change reverted.
- Non-goals: reusing a worktree on a different branch; changing where `lanes.py` puts an integration lane.
- Done when: the criteria pass.

## Context
Source: GitHub issue #42, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
The documented `lanes.py open integration --kind integration` leaves the branch checked out, then `fanout.py prep --integration <that branch>` exits 2 with `integration branch fanout/2026-10-20d is checked out in <integration tree>; git worktree add cannot check it out twice`; the conductor opened every lane by hand (3 occurrences).
On main the refusal text is at `plugins/sdlc-lite/scripts/fanout.py:876` to 877 in `preflight`, which `cmd_prep` (fanout.py:2141) calls. The issue names only prep, but `land_preflight` refuses the same case at fanout.py:2338, so fixing prep alone would move the failure to the first land; both are in scope. The integration kind of `lanes.py open` is described at `plugins/sdlc-lite/scripts/lanes.py:34`.

## Constraints
A run with no existing integration worktree behaves as today, creating `<lanes-dir>/integration` at the first land.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with the new case, and the case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
3. `git diff --check 8624f984` exits 0.

## Outcome
`fanout.py prep` and `land` now reuse an integration branch checked out in a worktree other than the main checkout. `preflight(reuse_integ=True)` (prep only) sets `integ_dir` to that worktree and `integ_reused`; `print_prep` prints `integration worktree: <path> (reused)`; `land_preflight` accepts the same worktree as `integ_dir` (merge.lock stays under the lanes dir). A branch checked out in the main checkout still refuses, and `run` is unchanged. New selftest case `case 23 reuse` (lanes.py open --kind integration, then prep exit 0 naming the reused path, then land merges into that tree with no `<lanes-dir>/integration`; plus the main-checkout prep refusal). Verified: the selftest passes (exit 0); a copy with prep and land reverted fails exactly the two reuse cases. `check.py`, `check-packaging.py` and `git diff --check 8624f984` exit 0.

## Outcome

2026-10-20 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 9fb99d1fb79d
- Changed: see commits
- Commits: 1954461 T-0689: fanout prep and land reuse an existing integration worktree
- Check: 1 `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with the new case, and the case fa...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass
- Check: 3 `git diff --check 8624f984` exits 0: pass
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:2398 adds a main-checkout... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:2402 has land_preflight reuse... -> notes.md
