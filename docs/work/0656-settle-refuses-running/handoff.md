---
id: T-0656
title: "settle --forward refuses while a lane attempt is running"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py settle --forward` never moves an integration branch while a role is still running against it: it refuses and names the running roles, unless `--force` is given.

## Intent
- Do: (1) In `cmd_settle` (`plugins/sdlc-lite/scripts/fanout.py`), before `settle_forward` runs, list the running markers (`<role>-<level>.running` under each tree's `<root>/runtime/tasks/`) in the integration worktree and in every worktree whose lane record has `into` equal to the integration branch (`lanes.discover`); any found refuses with exit 2, nothing merged, printing `settle: running in <tree>: <role>-<level> (<task>)` per marker and naming `dispatch.py status`/`recover` for stale markers. (2) Add `--force` to the settle parser to skip the check, and document both in the module docstring and usage line. (3) Add a selftest case.
- Non-goals: plain `settle` without `--forward` (its close already refuses while lanes are open into the branch). Detecting stale markers by pid.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #16, ui-kit-neue audit 2026-10-20.
- Evidence: 0050-s1-verifier-L1 was spawned at 15:39:57Z and `settle --forward` ran at 15:40:05Z; the verifier failed against the moved base, so builder-L2-2 and verifier-L1-2 had to run. A second settle at 16:05:16Z overlapped two running roles.
- Not fixed here: `cmd_settle` is at `plugins/sdlc-lite/scripts/fanout.py:2627`; the `--forward` branch calls `settle_forward` at `fanout.py:2648` with no running check. The settle parser is at `fanout.py:5386` (`--forward` at `fanout.py:5394`).
- Running markers: `dispatch.py prepare` writes `<role>-<level>.running` in the records dir (`plugins/sdlc-lite/scripts/dispatch.py:1178`); record and recover unlink it (`dispatch.py:613`, `dispatch.py:1537`). `board.py` already globs them per records dir (`plugins/sdlc-lite/scripts/board.py:257`). Lane discovery with `into`: `lanes.discover` (`plugins/sdlc-lite/scripts/lanes.py:476`).

## Constraints
`settle --forward` with no running marker behaves as today; the existing T-0489 settle selftest cases still pass.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with a new case: in the `forward_fixture` repo, a `verifier-L1.running` marker under the integration worktree's `.sdlc/runtime/tasks/t/` makes `settle fanout/x --forward --gate true` exit 2, print `verifier-L1`, and leave main and `fanout/x` unmoved; the same command with `--force` exits 0 and settles. The case fails with the running check removed (observed negative control, recorded in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/fanout.py settle --help` names `--force`.
3. `git diff --check` exits 0.
