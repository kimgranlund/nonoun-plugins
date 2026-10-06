---
id: T-0293
title: "solo_run kills process group and refuses a second live run"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`solo_run.py` ends its whole process group when it is stopped or times out, and refuses a second run in a worktree that already has a live solo run.

## Context
Maison T-0181 ran twice: pkill killed the python wrapper but not the child `claude`, and the second solo started beside the first. File: plugins/sdlc-lite/scripts/solo_run.py (its selftest runs against a stub `claude` on PATH). Docs: docs/maintenance/sdlc-internals.md `scripts/solo_run.py` entry.

## Requirements
- The child runs in its own process group (`start_new_session`). On SIGTERM, SIGINT, SIGHUP to the wrapper and on `--timeout`, killpg TERM, then KILL after 2 s, then exit nonzero. No orphan child survives.
- A lock file inside the worktree's own git dir (not a tracked path) holds the wrapper pid. A second `run` in the same worktree while that pid is alive exits nonzero with one `solo_run.py: another solo run is live (pid N)` line before any session or record. A lock whose pid is dead is cleared and the run proceeds. The lock is removed on every exit.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0 and includes a case with a real child process (a stub `claude` that spawns `sleep`) proving the whole group is gone after a timeout and after SIGTERM to the wrapper.
- [ ] The selftest has a second-run refusal case (live pid), a stale-lock case (dead pid proceeds), and a negative control: a copy of solo_run.py without the group kill leaves the child alive, so the case fails.
- [ ] docs/maintenance/sdlc-internals.md `scripts/solo_run.py` entry describes both behaviors in one or two sentences.
