---
id: T-0105
title: "Find out why the T-0072 background hook did not stop the run in..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0103
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0103 (run-result-format-check/filer-L1.md):

Find out why the T-0072 background hook did not stop the run in T-0103 (likely an Agent or Monitor background route); confirm after T-0076 ships.

Evidence, 2026-09-26: in an interactive Claude Code session, a plain Bash call (no run_in_background) running `check.sh` passed the default 120s timeout, and the harness reported "Command did not complete within its 120s timeout and was moved to the background". So Bash auto-backgrounds on timeout without the run_in_background flag, which PreToolUse hooks can't see. A likely fix is launchers setting BASH_DEFAULT_TIMEOUT_MS high, which bench.sh and dogfood do already, plus a check that run.sh and fanout set it too.

## Constraints
What must not change. "None" if none.
