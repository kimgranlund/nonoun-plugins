---
id: T-0865
title: "`gate_lock.py status` shows, for each admitted and queued job, the commit it tests, its working directory and"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0864]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`gate_lock.py status` shows, for each admitted and queued job, the commit it tests, its working directory and the session that owns it, and warns when a job tests a commit far behind its branch.

## Intent
- Do: record the cwd, short HEAD and owner session in each new ledger entry; show them in `status`; add a stale warning.
- Non-goals: cancelling another session's job (no `reap --stale` that kills); changing admission.
- Done when: the criteria below hold.

## Context
- #93: "A full check kept a slot for 83 minutes testing a commit 15 merges behind main", "a branch's queued checks tested a tree 45 commits behind", "a job named `admin-coverage7` came from another session, and nothing in `status` said so." Ask: show `git rev-parse --short HEAD`, the working directory and the owning session or pid; a warning or `reap --stale` for jobs behind their branch.
- `plugins/sdlc/scripts/gate_lock.py`: `run_top` builds the entry `me` at lines 806-807 (id, repo, name, cmd, need, priority, pid, pid_start, pgid, enqueued_at). `repo_identity` (line 580) already runs git in the cwd. `status_data` (line 910) builds grant and queue rows; `cmd_status` (line 943) prints them.
- Design: add optional fields `cwd`, `head` (short sha, empty when not a git tree) and `session` (`CLAUDE_CODE_SESSION_ID`, else `CODEX_THREAD_ID`, else empty) to `me`. Read them with `.get()` everywhere: older plugin versions share the ledger on the same host and write entries without them. `status` shows `head <sha> cwd <path> session <id>` per row when present. Stale warning: for a row with cwd and head, count `git rev-list --count <head>..<upstream or the default branch>` in that cwd with a short timeout; when above a threshold (20 commits) append `(behind <branch> by N)`. A git failure shows nothing, never fails `status`.
- Name the rule for cancelling in the docs only: the owner stops its own job; `status` names who that is.
- #101 (lanes-status-view) will read `cwd` from `status --json` to tie jobs to lanes, so keep the JSON key names as above.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Record `cwd`, `head` and `session` in new entries and show them in `status` and `status --json`.
2. Add the behind-branch warning and selftest cases, including a ledger entry with none of the new fields (an older writer) that still renders.
3. Update the docstring, the `gate_lock.py` entry of `docs/references/sdlc-internals.md` and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- `python3 plugins/sdlc/scripts/gate_lock.py selftest` exits 0 with cases for: a held job shows head, cwd and session; an entry without the new fields renders with no error; a job whose head is behind its branch by more than the threshold shows `behind`. The `behind` case fails on a mutant with the check removed (state the observed red).
- In a temp `SDLC_GATE_DIR` with one holder started in a git repo, `gate_lock.py status --json` shows `cwd` and `head` for it.
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- New ledger fields are optional for every reader; protocol stays `sdlc-gate/2`.
- `status` stays read-only and never stops a process.
