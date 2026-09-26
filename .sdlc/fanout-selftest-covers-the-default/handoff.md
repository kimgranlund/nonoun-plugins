---
id: T-0104
title: "fanout selftest covers the default .worktrees/fanout lanes dir only..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0090
---

## Goal
`fanout.py selftest` proves that a full stub-driver run with the default lanes dir (`<toplevel>/.worktrees/fanout`, no `--lanes-dir`) makes lane commits, merges, and closes tickets while leaving `git status` clean in the main tree.

## Context
Follow-up from T-0090 (fanout-lanes-in-worktrees-dir/filer-L1.md):

fanout selftest covers the default `.worktrees/fanout` lanes dir only with `--dry-run`; add a full stub-driver run there that checks lane commits, merge and close keep `git status` clean in the main tree.

## Constraints
fanout.py run behavior does not change; only its selftest grows. `scripts/check.sh` stays green. The selftest keeps using throwaway repos and a stub driver (no model calls).
