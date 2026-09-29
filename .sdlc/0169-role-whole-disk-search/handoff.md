---
id: T-0169
title: "A role's whole-disk find hung a planner run for 25 minutes"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A role cannot stall its run on a search of the whole filesystem, and a test that failed before the fix passes after it.

## Repro
1. Run `run.sh planner L2` on a task whose planner looks for a tool outside the repository.
2. Observed 2026-09-29 on T-0160: the planner ran `find / -name quick_validate.py -path "*skill*" 2>/dev/null | head -3` inside a Bash call. `find` is `bfs` on this machine. It ran for more than 25 minutes with no output, and the role made no progress.

## Expected
The search is refused or bounded, and the role continues.

## Actual
The run stalled until the maintainer stopped the `bfs` process by its PID. The planner then continued.

## Context
Evidence: the planner-L2 transcript of T-0160 (a `.log` file, ignored by Git and kept only on the maintainer's machine), tool use `toolu_01G5SZnuo2ZwTSdDiaNQFUpu`, heartbeat past 1,500 seconds. `| head -3` did not end the search, because no match was printed.

Options, not decided: a `PreToolUse(Bash)` hook inside role runs that denies `find /` and similar scans rooted at `/` or the home folder, or a line in the role contracts. The hook route follows the existing role-run hooks in `hooks/`, which key off `SDLC_ROLE`.

## Constraints
Claude hook enforcement does not imply Codex enforcement. The failing test lands before or with the fix.
