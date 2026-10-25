---
id: T-0773
title: "Lane commits never add a node_modules symlink; open warns when lane_setup is unset"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #81 reports no longer happens (title: Lane commits never add a node_modules symlink; open warns when lane_setup is unset).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/lanes.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #81 (quoted):

> **Observed:** a repo without `lane_setup:` in `.sdlc/config` got lanes with no dependencies; a `node_modules` symlink added by hand was committed by the lane's `git add -A` because `.gitignore`'s `node_modules/` (directory pattern) does not match a symlink, and the land's naming check then failed on it.
>
> **Root cause:** `lane_setup` (T-0692, #41) works but is opt-in with no warning; the lane commit (`scripts/lanes.py:1253`, `scripts/fanout.py:1436`) excludes logs and local settings but not a `node_modules` symlink (the plugin already warns a symlink is no fix, `fanout.py:1198-1207`).
>
> **Proposed fix:** add `/node_modules` (no trailing slash) to the lane's `info/exclude` the way `lanes.py:1540` does for local settings, and warn at `lanes.py open` when `package.json` exists but `lane_setup` is unset.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `lanes.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Reproduced on main: a `node_modules` symlink in a lane is committed by finish and by fanout's lane commit, and land's host-lane auto-commit swept both it and an untracked `scratch-note.txt` (case 30b red output showed both in the lane tree).
- Fix: `lanes.py open` adds `/node_modules` to the git common dir's `info/exclude` (the issue's proposal), so status, a builder's `git add -A`, finish's commit and fanout's `LANE_ADD` all skip the symlink. `fanout.py land` adds the same exclude before it commits a host lane, because a host lane never ran `open`. A pathspec exclude was tried and dropped: `git add -A -- . ':(exclude)node_modules'` exits 1 when the path is also ignored.
- `lanes.py open` prints `note: package.json but no lane_setup: in .sdlc/config; ...` when `package.json` exists and `lane_setup:` is unset; quiet when set.
- Untracked files: land now prints `land: committing untracked: <files>` (first 10, then `+N more`) before the host-lane commit, so a stray scratch file is visible before it merges. A short list, not a refusal; the solo's legitimate new files are on it too.
- Tests: `lanes.py` case `node_modules` (finish with a symlink, open note with and without `lane_setup`); `fanout.py` case 25 (symlink in a headless lane) and case 30b (host lane: symlink absent from the commit, scratch-note named).
- Negative control: with the `info/exclude` lines and the note removed from `lanes.py`, the lanes selftest prints `FAIL: node_modules: node_modules: want main with the committed fin2.txt and no node_modules symlink | node_modules: open with package.json and no lane_setup want the note`. With the land and open excludes removed, the fanout selftest prints `FAIL ... case 25 lane commit: artifacts excluded ...` and `case 30b host worktree (T-0773): the land commit holds y.txt but no node_modules symlink ... tree=[..., 'node_modules', 'scratch-note.txt', 'y.txt']`.
- Checks: `gate_lock.py run ... lanes.py selftest` exit 0, `fanout.py selftest` PASS, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check d49b31c2` exit 0.
- Not changed: the solo agent text and `run-operations.md` still show the plain `git add -A -- . ':(exclude,glob)...'` line; the exclude makes it safe for any lane opened by `lanes.py`.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: d49b31c2ba41
- Changed: see commits
- Commits: e76db01 T-0773: lane commits never add a node_modules symlink; open warns when lane_setup is unset
- Check: 1 A `lanes.py` selftest case reproduces the issue's report and passes; with the change reverted it ...: pass
- Check: 2 lanes selftest via gate_lock exits 0, `check.py` exits 0, `check-packaging.py` passes, `git diff ...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/lanes.py:1427 add_exclude is idempotent -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/lanes.py:257 /node_modules is anchored at... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/lanes.py:1584 the line goes into the... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:2819 builds a full lanes.Ctx on... -> notes.md
