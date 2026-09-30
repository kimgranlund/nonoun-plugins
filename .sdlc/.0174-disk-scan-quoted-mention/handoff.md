---
id: T-0174
title: "block-disk-scan.sh denies a quoted mention of a scan inside a compound command"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-09-30
---

## Goal
`block-disk-scan.sh` refuses a whole-disk scan inside a role run but does not refuse a command that only mentions one inside quotes, and a test that failed before the fix passes after it.

## Repro
Observed by the independent release verifier for 0.20.0 (`.sdlc/release-0.20.0/step-1/verifier-L3-2.md`, Hooks bullet), with `SDLC_ROLE=builder` set and the hook fed PreToolUse JSON from a file:

- A compound command whose only `find /` sat inside a single-quoted `printf` argument was denied, exit 2.
- The same quoted mention alone exited 0, which matches the hook's own header ("quoted mentions pass").

The exact compound command was not recorded. Reconstruct it first, for example `printf '%s' 'find / -name x' | wc -c`, and confirm it reproduces before changing anything.

## Expected
The hook allows it, since nothing scans the disk.

## Actual
The hook denies it with its whole-disk scan message.

## Context
The hook matches scans after masking quoted strings in other role-run hooks (`block-publish.sh` masks heredoc bodies, quoted contents and comments). Check whether `block-disk-scan.sh` does the same masking for compound commands and whether the two hooks should share one implementation. Claude Code only; the Codex side has no hooks.

## Constraints
The failing test lands before or with the fix, in `scripts/hook-selftest.sh`, together with a positive case that a real scan is still denied. Do not loosen the real-scan cases.

## Closed

2026-09-30: Not reproduced as a false positive. A quoted find / inside a compound command exits 0 for pipes, redirects, && chains and jq. The denial appears only when the command also holds a heredoc or a shell word (bash, sh, eval), which block-disk-scan.sh denies on purpose (header, line 48). The verifier command likely held bash check.sh. No hook change.
