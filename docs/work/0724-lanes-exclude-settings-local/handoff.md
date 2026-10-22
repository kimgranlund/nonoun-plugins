---
id: T-0724
title: "Lanes never stage .claude/settings.local.json"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A lane worktree never stages `.claude/settings.local.json`, and land or settle tolerate it being untracked.

## Intent
- Do: `lanes.py` copies the file into each lane (about line 1513). Also add `.claude/settings.local.json` to the worktree's `info/exclude` (or the common `info/exclude`) when it is not already ignored.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #60 (quoted):

> **Repro**: a worktree acquires an untracked `.claude/settings.local.json` (host settings); a merge/commit in the lane with `git add -A` stages it; later `fanout.py land` or settle runs in a checkout where the same file is untracked.
>
> **Expected**: lanes never stage host-personal settings; land/settle tolerate them.
>
> **Actual**: the file reached integration via a lane merge, then `fanout: ... is not a fast-forward of main: error: The following untracked working tree files would be overwritten by merge: .claude/settings.local.json` (settle) and `merge failed: ... untracked working tree files would be overwritten` (T-0076 land).
>
> **Evidence**: `fanout/logs/land.jsonl` (T-0076); settle of 2026-10-22. Fix idea: lanes.py open/land add `.claude/settings.local.json` to the worktree's info/exclude.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `lanes.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`lanes.py open` now adds `.claude/settings.local.json` to the common `info/exclude` when `git check-ignore` does not already ignore it, so a lane's `git add -A` never stages the copied host settings. Selftest case `local settings unignored` reproduces the repro (repo without the ignore line); the selftest env also sets `XDG_CONFIG_HOME` so a developer's global ignore cannot mask the case.

- Negative control (exclude step disabled): `FAIL: local settings unignored: local settings unignored: git add -A in the lane want only new.txt staged, got ['.claude/settings.local.json', 'new.txt']`, selftest exit 1.
- With the change: `lanes.py selftest` through gate_lock exit 0; `check.py` exit 0; `scripts/check-packaging.py` exit 0; `git diff --check 2c630e96d7118051929a27ff477b62c4f056350d` exit 0.
