---
id: T-0108
title: "A dry run of a role whose agent declares skills planner, architect..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0095
---

## Goal
A dry run (`SDLC_DRY_RUN=1`) of a role whose agent declares skills leaves no `mktemp` skill file behind.

## Context
Follow-up from T-0095 (role-worktrees-left-behind/filer-L1.md):

A dry run of a role whose agent declares skills (planner, architect, verifier) leaves its `mktemp` skill file behind in `run.sh`; remove it on dry-run exit.

## Constraints
None.

## Done (conductor, trivial edit)
- `plugins/sdlc-lite/scripts/run.sh`: right after `skill_file=$(mktemp)`, `trap 'rm -f "$skill_file"' EXIT`, so the dry-run `exit 0` (and the missing-skill `exit 2`) remove it; the later `on_exit` trap replaces it and still removes the file.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: a dry run of verifier L1 must print an `--append-system-prompt-file` path that no longer exists. Negative control: with the trap removed the selftest fails with `dry run left its skill file behind`.
- `scripts/check.sh`: exit 0.

## Acceptance criteria
1. `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: PASS`.
2. With the new `trap 'rm -f "$skill_file"' EXIT` line removed from a scratch copy of run.sh, the selftest's new check fails with `dry run left its skill file behind` (restore the file afterwards; leave the tree as found).
3. `plugins/sdlc-lite/scripts/check.sh` exits 0.
4. The change is limited to run.sh, run-selftest.sh, and this handoff (`git diff --stat`).
