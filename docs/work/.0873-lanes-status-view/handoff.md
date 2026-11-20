---
id: T-0873
title: "`lanes.py status` answers 'is anything stuck or about to collide' for every open lane in one table"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0872, T-0865]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`lanes.py status` answers "is anything stuck or about to collide" for every open lane in one table.

## Intent
- Do: add a read-only `status [--json]` command with one row per plugin lane.
- Non-goals: a cross-repo view (`fleet_status.py` owns that); process health (`fleet_doctor.py` already flags a stalled lane role by pid and cwd, lines 17-32 and 137-159); changing `list` output.
- Done when: the criteria below hold.

## Context
- #101: with five lanes the reporter looped `git log --oneline <base>..HEAD | wc -l` and `git status --short | wc -l` by hand. Proposed columns: branch, ahead and behind its `--into`, clean merge (`git merge-tree`), uncommitted files, last commit time and last file change, a gate_lock job from that worktree queued or running, the paths it touches so overlaps show.
- `plugins/sdlc/scripts/lanes.py`: `list_lanes` (line 2217) builds rows from `discover(ctx)` with lane, path, branch, kind, state, into, locked; `lane_paths(ctx, d)` (line 2268) gives the changed paths since base; `overlap` uses it. Reuse both.
- Columns: lane, branch, ahead/behind into (`git rev-list --left-right --count`), merges cleanly (`git merge-tree --write-tree <into> <branch>` exit code; git 2.38 or later, else `?`), uncommitted count, last commit age, newest mtime of an uncommitted file, gate (from `gate_lock.py status --json`: a grant or queue row whose `cwd`, added by gate-lock-status-owner, is under the lane path), and `overlaps <lane>` when its paths intersect another lane's. `--json` for tools.
- It must stay fast: one git call per column per lane, no fetch.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Add `status` with the columns above and `--json`.
2. Add selftest cases with two lanes touching one shared path: ahead counts, one uncommitted file, the overlap named on both rows, a conflicting pair showing not clean; and a lane with a fake gate ledger entry (temp `SDLC_GATE_DIR`) showing its gate state.
3. Document it in the `lanes.py` docstring usage, the `lanes.py` entry of `docs/references/sdlc-internals.md`, and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- The lanes selftest shard holding the new cases exits 0; with the overlap column stubbed out, the overlap case fails (state the observed red).
- In a throwaway repo with two live lanes, `lanes.py status --json` parses and lists both.
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- Read-only: no fetch, no lock, no write.

## Outcome

2026-11-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: fa7d546d900a
- Changed: see commits
- Commits: 7171060 T-0873: lanes.py status shows every lane's progress, drift and overlap (#101)
- Check: 1 The lanes selftest shard holding the new cases exits 0; with the overlap column stubbed out, the ...: pass
- Check: 2 In a throwaway repo with two live lanes, `lanes.py status --json` parses and lists both: pass
- Check: 3 `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean: pass
- Follow-up: note: plugins/sdlc/scripts/lanes.py case_status: the docstring says "a... -> notes.md
- Follow-up: note: no em dashes in the added lines checked with grep on the diff. -> notes.md
