---
id: T-0025
title: "Bench tasks and results live in the project"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A project keeps its own bench tasks, results and logs, so a plugin update never removes them.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Asked by the setup-sdlc-lite-generative-ui session (gen-ui-system-svelte-lite keeps `bench/tasks/svelte-switch-component.md`). In 0.3.0, `skills/bench`, `scripts/bench.sh` and `scripts/bench-summary.sh` all use `${CLAUDE_PLUGIN_ROOT}/bench/{tasks,results,logs}`, which live in the plugin cache for installed users, so an update removes both tasks and history. Suggested: a `--tasks-dir` (and results dir) option, defaulting to `<project>/bench/` when it exists, else the plugin's own `bench/` (which keeps this repo's dev bench working).

## Constraints
What must not change. "None" if none.
