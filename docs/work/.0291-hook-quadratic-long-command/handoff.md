---
id: T-0291
title: "PreToolUse hooks run super-quadratic on long Bash commands"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every PreToolUse Bash hook finishes a 20 KB heredoc command in under 2 seconds with unchanged blocking.

## Repro
Pipe `{"tool_name":"Bash","tool_input":{"command":<heredoc of n bytes>}}` to `SDLC_ROLE=solo bash plugins/sdlc-lite/hooks/block-disk-scan.sh` (also block-pattern-kill.sh, block-stray-worktree.sh, block-repo-format.sh as builder).

## Expected
Linear time, milliseconds.

## Actual
0.24 s at 1 KB, 1.3 s at 2 KB, 8.8 s at 4 KB, over 40 s at 8 KB.

## Context
Cause: the cheap-exit line `pf=${cmd//[\\\'\"]/}` and the raw-scan line `raw=$(tr ... <<<"${cmd//\\/}")` in four hooks. Bash 3.2 pattern substitution is quadratic for a bracket class, and for a literal backslash pattern when the text holds many backslashes. Fix: `tr -d`.

## Acceptance criteria
1. The hook selftest has a 20 KB case per hook, run under a 2 s timeout, with a pass and a deny control; it fails on the old hooks and passes on the new.
2. Existing hook selftests, check.py, check.sh stay green.

## Constraints
Do not touch the sub-agent wave files. No em dashes.

## Closed

2026-10-06: Fixed: pf= and raw= lines in four hooks now use tr; 20 KB perf case in hook-selftest.sh; verifier L3 pass on the rerun; docs/reports/hook-perf.md
