---
id: T-0025
title: "Bench tasks and results live in the project"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A project keeps its own bench tasks, results and logs, so a plugin update never removes them.

## Intent
- Literal ask: bench tasks, results and logs belong to the project, not the plugin cache, so a plugin update never removes them.
- Do: give `scripts/bench.sh`, `scripts/bench-summary.sh` and `skills/bench/SKILL.md` one shared rule for the bench dir: an explicit option (`--bench-dir DIR`, or env `SDLC_BENCH_DIR`) wins; else `<project>/bench/` when it exists (project = `git rev-parse --show-toplevel` of the current dir); else the plugin's own `bench/` (`${CLAUDE_PLUGIN_ROOT}/bench`). Tasks, results and logs all resolve under that one dir. bench.sh passes the resolved dir to the headless /bench session (e.g. via `SDLC_BENCH_DIR`) and to bench-summary.sh so all three agree. Update docs that describe the bench paths (repo `CLAUDE.md` Commands line, `.claude/agents/sdlc-lite-author.md` if it names them, `bench/tasks/README.md` if it names paths).
- Non-goals: moving this repo's existing bench tasks or results; changing the task file format, grading, or the summary columns; a separate results dir option (one bench dir holds all three).
- Done when: with a temp git repo that has `bench/tasks/x.md`, the resolver picks that dir; with no project `bench/`, it picks the plugin's `bench/` (this repo's dev bench keeps working unchanged); the explicit option overrides both; `bench-summary.sh` reads results from the resolved dir; `scripts/check.sh` passes (shellcheck included).

## Context
Asked by the setup-sdlc-lite-generative-ui session (gen-ui-system-svelte-lite keeps `bench/tasks/svelte-switch-component.md`). In 0.3.0, `skills/bench`, `scripts/bench.sh` and `scripts/bench-summary.sh` all use `${CLAUDE_PLUGIN_ROOT}/bench/{tasks,results,logs}`, which live in the plugin cache for installed users, so an update removes both tasks and history. Suggested: a `--tasks-dir` (and results dir) option, defaulting to `<project>/bench/` when it exists, else the plugin's own `bench/` (which keeps this repo's dev bench working).

## Constraints
- This repo's dev bench (`plugins/sdlc-lite/bench/`) must keep working with no flags: the repo root has no `bench/`, so the fallback applies.
- bench.sh must never write logs into the plugin cache when a project bench dir is in use.
- Bash stays compatible with macOS bash 3.2 (no associative arrays, no `mapfile`).
