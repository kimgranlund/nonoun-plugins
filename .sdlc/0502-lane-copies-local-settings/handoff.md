---
id: T-0502
title: "lanes.py: a new lane worktree gets the gitignored .claude/settings.local.json (agent-ui retro row 7)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`lanes.py open` copies the gitignored `.claude/settings.local.json` of the starting checkout into a new lane worktree, so Bash allow lists apply and the user is not prompted.

## Repro
1. In a repo with a gitignored `.claude/settings.local.json` holding a Bash allow list, open a lane with `lanes.py open`.
2. List the lane's `.claude/`.

## Expected
The file is present in the lane, byte for byte.

## Actual
Absent: a worktree starts from tracked files only, so allow lists did not apply and the user was prompted (agent-ui, 3 worktrees copied by hand).

## Context
Origin: agent-ui conductor message 2026-10-12 and /Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/fleet-retro-2026-10-12-12.md, row 7. Precedent: `.sdlc/config` is copied untracked into fanout lanes (`fanout.py`). Fix in `plugins/sdlc-lite/scripts/lanes.py` open, with a copy-if-present step and no overwrite of an existing file.

## Constraints
Red check: a `lanes.py selftest` case with an ignored settings file (absent in the lane today). Never copy any other ignored file; never log the file's contents.
