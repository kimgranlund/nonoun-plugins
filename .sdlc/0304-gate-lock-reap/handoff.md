---
id: T-0304
title: "gate_lock.py reap suggests orphaned browser processes"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0303]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`gate_lock.py reap`: list leftover browser processes from finished runs, suggest-only by default. USER DECISION. Build on T-0303's gate_lock.py (same file; wait for it to land). Do NOT build any red-under-load re-run rule.

## Requirements
- `gate_lock.py reap [--older-than MIN] [--kill]` lists processes matching chrome-headless-shell, chromium (Chromium/Chrome for Testing), playwright, and vite preview whose parent pid is 1 or no longer exists and whose age exceeds the threshold (default 30 min). Default prints the list and kills nothing. `--kill` TERMs (then KILLs after 2 s) only those, printing each pid it stops. A process with a live parent is never listed as killable and never killed.
- docs/maintenance/sdlc-internals.md `gate_lock.py` entry gets one sentence.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 with reap cases using a fake orphan (a process named to match, reparented to pid 1 by double fork or a dead parent, age threshold set to 0): listed by default and still alive, killed by `--kill`; a matching process with a live parent is neither listed killable nor killed.
- [ ] Negative control shown once: without the parent check the live-parent case fails.
