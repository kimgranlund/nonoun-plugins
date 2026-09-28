---
name: bench
description: "Benchmark the agent team: run each saved task through /chain in a throwaway worktree, grade it with the real solution's hidden tests, and compare pass rate, cost, and attempts across runs. Use after changing a role, a level table, or a rubric."
argument-hint: "[task name]"
allowed-tools: Bash, Read, Write, Grep, Glob
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

First, before any `cd`, resolve the bench dir once from the session's starting directory: `BENCH=$(${CLAUDE_PLUGIN_ROOT}/scripts/bench-dir.sh)`. It honors `SDLC_BENCH_DIR` as set by `bench.sh`, then `<project>/bench/`, then the plugin's `bench/`. Keep the absolute path for the rest of the run.

Tasks live in `$BENCH/tasks/<name>.md` (format in `$BENCH/tasks/README.md` or the plugin's `bench/tasks/README.md`). If there are none, say so and stop. How to run `run.sh` depends on the session. Headless (`claude -p`, including `scripts/bench.sh`, which raises `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`): run every call in the foreground with the Bash tool's `timeout` set to 600000 or more, do not use `run_in_background` there, and never end your turn while a role is running, because ending the turn ends the session and abandons the run. `hooks/block-background.sh` denies Bash `run_in_background` calls and denies any Agent call unless `run_in_background` is explicitly `false` (Agent runs in the background by default, so a missing field counts as background) whenever `SDLC_ROLE` is set or `SDLC_HEADLESS=1`; bench.sh and fanout set `SDLC_HEADLESS=1`, and any other headless launcher (a dogfood script) must set `SDLC_HEADLESS=1` itself. In an interactive session: a role, or a bench task's full /chain, can take 15 to 30 minutes, past the Bash tool's 10-minute cap. Run `run.sh` with `run_in_background: true`, then wait for the completion notification. Never poll with `sleep`. Once notified, read the result from `<role>-<level>.md`. Ending the turn is safe here because the notification re-invokes the session.

Run each task (or only the named one) in turn:

1. `git -C <repo> worktree add --detach <mktemp -d> <base>`. Builders skip permissions, so never run in the user's working tree. `cd` into the worktree and run `setup`.
2. Write everything from `## Goal` down to `.sdlc/bench-<name>/handoff.md`. Never show the agents the header fields, the solution, or the hidden tests.
3. Run the /chain flow on that handoff, skipping the file stage. Stop the task (record `blocked`) wherever /chain would ask the user.
4. Grade: copy each `test_paths` file from `tests_from` (`git -C <repo> show <tests_from>:<path> > <path>`), run `check`, and write `grade.md` in the task dir: `hidden_check: pass|fail`, the exit code, and the last 20 lines of output.
5. Move `.sdlc/bench-<name>` to `$BENCH/results/<YYYY-MM-DD>-<name>/`, then `git -C <repo> worktree remove --force` the worktree and `git -C <repo> worktree prune`.

Then run `${CLAUDE_PLUGIN_ROOT}/scripts/bench-summary.sh --bench-dir "$BENCH"` and report its table, plus the change from each task's previous run. The hidden check is the real score; the verifier's verdict is reported next to it, and any case where the verifier passed but the hidden check failed is flagged 🔴 (the verifier missed a defect).
