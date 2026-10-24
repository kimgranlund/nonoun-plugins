---
id: T-0753
title: "Solo briefs give no exported SDLC_BASE_SHA for criteria that name it"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo sub-agent whose ticket criteria name `$SDLC_BASE_SHA` runs them against the right base: its brief names the base and says to `export SDLC_BASE_SHA=<base> &&` before such a span, as the `dispatch.py prepare` brief does for builder and verifier since T-0735.

## Repro
1. `cd /tmp && git -C <any repo> diff --name-only ""` exits 128 (`fatal: ambiguous argument ''`); inside `test -z "$(...)"` it passes vacuously.
2. A solo brief from `solo_run.py run` (sub-agent path) has no `Base sha:` line at all; the `fanout.py prep` solo brief (`SOLO_SYNC`, fanout.py about line 2159) has `Base sha: <sha>` but no export instruction.

## Expected
Both solo briefs carry the base and the export instruction; a selftest case in `solo_run.py` and `fanout.py` asserts it.

## Actual
A solo span such as `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . | grep -v x)"` runs with the variable unset in a sub-agent shell.

## Context
Found in the T-0735 run.sh-assumption audit. run.sh exported SDLC_BASE_SHA to its role; a sub-agent inherits only the parent session's environment. Which base a solo brief should name (the lane fork point, the claim commit) is the open choice; a guess: the fanout `base_sha` for lanes, `git rev-parse HEAD` at `solo_run.py run` time otherwise.

## Constraints
The failing test lands before or with the fix, never after.
