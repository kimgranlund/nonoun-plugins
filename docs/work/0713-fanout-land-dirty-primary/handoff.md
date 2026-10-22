---
id: T-0713
title: "fanout.py land leaves lane-close bookkeeping uncommitted in the primary checkout"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Running `fanout.py land` (and the lane close inside it) from the primary checkout leaves that checkout clean: the lane-close bookkeeping (the ticket's `branch:`/`worktree:` lines, `docs/work/ROADMAP.md` or the repo's roadmap, and the `.sdlc/AGENTS.md` router) lands only as a commit, on the integration branch when one is used, never as uncommitted edits in the primary checkout.

## Intent
- Do: in `plugins/sdlc-lite/scripts/fanout.py` (`close_lanes`, about line 1965) and `plugins/sdlc-lite/scripts/lanes.py` (`close_lane`, about line 986), make the close write its bookkeeping in the tree that owns the target branch (the integration worktree when `--into`/an integration branch is used) and commit it there; when the primary checkout is touched at all, commit the change or leave it byte-identical. Add a selftest case reproducing the issue's repro.
- Non-goals: changing what bookkeeping is written.
- Done when: the criteria pass.

## Context
GitHub issue #46 (quoted):

> ## What happened
> Using `fanout.py land` (and the lane close inside it) from the primary checkout, each land that closes a lane leaves the **primary checkout** dirty with uncommitted bookkeeping:
>
> - the ticket's `branch:` and `worktree:` lines removed in `docs/work/<ticket>/handoff.md`;
> - the regenerated `docs/work/ROADMAP.md`;
> - the regenerated router, `.sdlc/AGENTS.md`.
>
> Those same files also change on the integration branch, so a later `git merge --ff-only <integration>` on main refuses, or mixes with the maintainer's own uncommitted work. In one night I reverted these files by hand five times before a fast-forward.
>
> ## Expected
> Lane close writes its bookkeeping only on the integration branch. When it must touch the primary checkout, it commits there, or it leaves the files clean once the integration branch carries the same change.
>
> ## Repro
> 1. Have an integration branch with a lane.
> 2. Run `fanout.py land <lane-branch> --ticket T-x ...` from the primary checkout.
> 3. `git status` in the primary checkout shows the files above as modified.
>
> Seen on sdlc-lite 0.29.0 and 0.30.0.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `fanout.py` selftest case runs a land that closes a lane from the primary checkout and then asserts `git status --porcelain` of the primary checkout is empty and the bookkeeping is committed on the integration branch; with the change reverted, that case fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` and the same for `lanes.py selftest` exit 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Root cause: `lanes.do_close` cleared each ticket's `branch:`/`worktree:` record in the main checkout (regenerating the roadmap and router) and never committed it, while `clear_integration_record` cleared and committed the same record in the integration tree. Reproduced in a throwaway repo (prep, the printed `lanes.py open`, two lands): main showed ` M .sdlc/AGENTS.md`, ` M .sdlc/roadmap.md`, ` M .sdlc/t1/handoff.md`, ` M .sdlc/t2/handoff.md`.
- Fix (`plugins/sdlc-lite/scripts/lanes.py`): the integration tree is cleared first; a ticket it cleared stays byte-identical in main (merging the integration branch brings the clear, and `git merge --ff-only` now succeeds). A clear that still lands in main, with into another branch than main, is committed there as `<ids>: clear lane record <leaf>` (new `commit_clear`, shared with the integration path). Into main keeps the old behavior (`finish` commits it). The usage text says so.
- Selftest: `fanout.py` case 32 asserts main's `git status --porcelain` is empty after the closing land, main still holds the record, and `fanout/f` carries `T-0001, T-0002: clear lane record alpha` with no `branch:` line.
- Negative control (lanes.py reverted to the base): `case 32 T-0713: the land that closes the lane leaves main clean and commits the cleared record on fanout/f, got status=' M .sdlc/AGENTS.md\n M .sdlc/roadmap.md\n M .sdlc/t1/handoff.md\n M .sdlc/t2/handoff.md\n' last commit='T-0001, T-0002: clear lane record alpha'`
- Checks: `fanout.py selftest` PASS and `lanes.py selftest` ok (both through gate_lock), `check.py` exit 0, `check-packaging.py` PASS, `git diff --check 7e5c77c6` exit 0.
