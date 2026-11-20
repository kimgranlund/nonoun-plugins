---
id: T-0869
title: "A verifier prepared in a lane that merged its integration branch gets a Base sha that keeps the integration br"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0860]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A verifier prepared in a lane that merged its integration branch gets a Base sha that keeps the integration branch's other tickets out of its diff.

## Intent
- Do: make `fork_floor` use the lane's recorded `into` branch when the lane record names one, before the primary checkout's HEAD.
- Non-goals: changing the named `base:` line, the recorded base-sha rules or the host-lane cut point.
- Done when: the criteria below hold.

## Context
- #86: lane fanout/2026-10-21-bootchunk merged its integration branch (`fanout.py sync`, commit 55e4d5fd). The next `dispatch.py prepare verifier` rewrote base-sha to bc306c8d, a commit on the integration side, and the verifier's diff-scope guard failed on four test files other tickets had landed on the integration branch. Suggested fix: "let `fork_floor` use the integration branch recorded in the lane record".
- `plugins/sdlc/scripts/dispatch.py`: `fork_floor` (lines 485-496) is `git merge-base HEAD <main checkout HEAD>` (or `SDLC_BASE_REF`). In the base resolver (lines 545-640), `below_floor(stored)` drops the recorded base when the floor is newer (line 612), and the fallback sets `start = floor` with the message "the lane merged main after its start" (lines 626-631). `lane_record_base` (line 502) already reads the lane record through `wtroot.lane_record(top, top)`; the record has an `into` field (`lanes.py` FIELDS, line 283).
- Design: in `fork_floor`, when `SDLC_BASE_REF` is unset and the lane record names `into` that resolves, use `git merge-base HEAD <into>`; else keep the primary checkout HEAD. After a sync merge, that merge base is the integration tip the lane merged, so the diff holds only the lane's own work, before and after the merge. When the base moves, the existing `say` line should name the old and new base and the ref used.
- T-0860 shards the dispatch selftest (555 s unsharded); add the case to the shard that holds the T-0748 lane-merged-main cases (around lines 3851-3924) and run that shard.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Read `into` from the lane record in `fork_floor` as above.
2. Add a selftest case: lane A opens from main with `into` an integration branch; another branch lands a file on the integration branch; lane A merges the integration branch; `prepare verifier` gives a Base sha whose diff to HEAD holds lane A's files and not the other file. Keep the T-0748 main-merge cases green.
3. Note the rule in the `dispatch.py` entry of `docs/references/sdlc-internals.md` and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- The `dispatch.py selftest` shard holding the new case exits 0 (name the shard command in the report); with `fork_floor` reverted to the primary HEAD only, the new case fails (state the observed red).
- `python3 plugins/sdlc/scripts/dispatch.py selftest` with no shard option exits 0 (run once, at the end).
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- Run the `run.sh` parity cases if the base logic is shared with `run.sh` (`AGENTS.md`: a gate change in one needs the same change in the other).
