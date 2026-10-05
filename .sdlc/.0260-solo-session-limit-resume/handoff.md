---
id: T-0260
title: "Solo long commands capped at 30 min and session-limit stops leave no resume"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo stopped by the 30 minute background cap or a session limit leaves a resume marker the conductor can act on.

## Context
Two reports. 1) A solo's long foreground command is backgrounded by Claude Code and capped at 30 min regardless of the Bash timeout. 2) Session-limit stops leave `driver failed rc=1` with only a WIP commit and no resume; `run.sh` on a 429 session limit exits 1 with no resume marker.
Scope: file and design the marker and the guidance. No fix in this ticket's filing.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Closed

2026-10-05: run.sh and solo_run.py leave a resume marker and hint on a session limit; selftests added; verifier L3 pass in verify-defect-fixes-0.20.10
