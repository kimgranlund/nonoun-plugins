---
id: T-0860
title: "Cut check.sh wall time by sharding its slowest selftests"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-19
branch: lane/T-0860-t0860
worktree: ../sdlc-lite.worktrees/T-0860-t0860
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The full `check.sh` finishes in well under its current 600 s on this machine, with the same cases run.

## Intent
- Do: split the selftests that set the wall time into shards that run as separate pool jobs.
- Non-goals: removing or weakening any case; `--changed` (T-0858); reruns (T-0861).
- Done when: the criteria below hold.

## Context
- User feedback 2026-11-19 (see T-0858). Job times from the last full runs (58 jobs in parallel through `check_pool.py`, wall 600 to 633 s): `fanout` 602 s, `dispatch` 555 s, `lanes` 273 s, `run-selftest` 212 s, `tickets` 206 s, `gate_lock` 143 s, `steps` 140 s, `supervisor` 117 s. The wall time is the longest job, so `fanout` and `dispatch` decide it, then `lanes`.
- Approach: give the `fanout.py`, `dispatch.py` and (if needed) `lanes.py` selftests a `--shard i/n` option (or named groups) that runs a deterministic subset of cases, every case in exactly one shard, and list each shard as its own `job` line in `check.sh`. A plain `selftest` with no option still runs every case. Check first whether cases depend on earlier cases' state; where they do, shard at the boundaries that are independent. Measure before choosing n; also check whether the machine's core count or `gate_lock` serialises these jobs, and say what you found.
- Each shard must print its case count, and the sum over shards must equal the unsharded count: add that as a check (a small job or a `check.py` item) so a case cannot fall out of every shard.
- T-0858 edits `check.sh` in parallel (option parsing, one job line); keep your edits to the job list. Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Measure and find the shard boundaries.
2. Add sharding to the selftests and the job lines.
3. Add the case-count closure check, update the `check.sh` usage comment, `plugins/sdlc/AGENTS.md` if it names job counts, and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
(Replan: a verifier cannot run the full `check.sh` or a 600 s unsharded selftest inside its foreground cap, so the factory ran the full suite on the lane head and the verifier checks the shards.)
- `.sdlc/runtime/tasks/0860-faster-full-suite/check-full.log` (the factory's full `bash plugins/sdlc/scripts/check.sh` run in this lane) starts with a `head: <sha>` line whose commit holds the same `plugins/sdlc/scripts` tree as HEAD (`git diff --quiet <sha> HEAD -- plugins/sdlc/scripts`), has no `FAIL` job line, and ends with `check: N jobs ok in <T>s` with T at most 360 and `exit=0`.
- `python3 plugins/sdlc/scripts/shards.py selftest` exits 0, and `python3 plugins/sdlc/scripts/shards.py check plugins/sdlc/scripts/check.sh` exits 0 and prints, per sharded script, shard counts that sum to the unsharded count. With one `--shard` job line removed from a scratch copy of `check.sh`, the same `check` exits 1 (observed red).
- All nine shard jobs pass when run together in one foreground command, each in the background with its exit code collected by `wait`: `fanout.py selftest --shard 1/4` to `4/4`, `dispatch.py selftest --shard 1/3` to `3/3`, `lanes.py selftest --shard 1/2` and `2/2`. Each shard prints its case count.
- No case was removed or loosened: for `fanout.py`, `dispatch.py` and `lanes.py`, the sorted, indent-stripped selftest lines at Base sha and at HEAD differ only by the shard wiring and the renames the solo report names (spot-check at least fanout).
- `git diff --check $SDLC_BASE_SHA -- plugins/sdlc CHANGELOG.md docs/references` is clean.

## Constraints
- No case removed, skipped or loosened.
- `--fast` keeps its job set apart from renamed shards.
