---
id: T-0049
title: "Newest result is picked by mtime, which checkout resets"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P1
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Which result is newest (builder, verifier, planner) is decided from recorded run order, so a fresh clone or a committed .sdlc/ trail reads the same verdicts as the machine that ran them.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Review 2026-09-24: git checkout gives every file the same mtime. In a fresh worktree, bench-summary reported button-geometry as 2/3 steps passed (it picked step-2's older failing verifier-L1.attempt2.md among equal mtimes); on the original checkout it reports 3/3. The same mtime rule decides the newest file in board.py (by_level, the verifier-after-build check), bench-summary.sh, and run.sh's verifier model swap (`ls -t builder-L*`). runs.jsonl already records run order per dir (ts, role, level); since T-0038, reruns are named <role>-<level>-<k>. Suggested: derive "newest" from runs.jsonl order (fall back to name order), never mtime, with a selftest that sets equal mtimes.

## Constraints
The failing test lands before or with the fix, never after.
