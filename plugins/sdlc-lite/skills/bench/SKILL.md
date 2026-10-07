---
name: bench
description: "Benchmark the agent team: run each saved task through /chain in a throwaway worktree, grade it with the real solution's hidden tests, and compare pass rate, cost, and attempts across runs. Use after changing a role, a level table, or a rubric."
argument-hint: "[task name]"
allowed-tools: Bash, Agent, Read, Write, Grep, Glob
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

For every role launch, set `SDLC_ROUTING_REASON` to the selected role/level rationale, including the recorded cause of any escalation or replan. Read shared run operations at `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/run-operations.md` for readiness, attempt records, and safe recovery.

Arguments: `$ARGUMENTS`

First, before any `cd`, resolve the bench dir once from the session's starting directory: `BENCH=$(${CLAUDE_PLUGIN_ROOT}/scripts/bench-dir.sh)`. It honors `SDLC_BENCH_DIR` as set by `bench.sh`, then `<project>/bench/`, then the plugin's `bench/`. Keep the absolute path for the rest of the run.

Tasks live in `$BENCH/tasks/<name>.md` (format in `$BENCH/tasks/README.md` or the plugin's `bench/tasks/README.md`). If there are none, say so and stop. Every role of a bench task is dispatched as a sub-agent through the /chain flow: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prepare <role> <level> <handoff.md>`, an `Agent` call with the printed `subagent_type`, `name`, `description`, `model`, `prompt`, and `run_in_background` unchanged, then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py record <dispatch_file>` with the sub-agent's final message on stdin (`${CLAUDE_PLUGIN_ROOT}/agents/conductor.md`, "How you run roles", has the contract; on Codex a role runs through `SDLC_BACKEND=codex ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh <role> <level> <handoff.md>`). Headless (`claude -p`, including `scripts/bench.sh`, which sets `SDLC_HEADLESS=1`): `prepare` prints `run_in_background: false`, so spawn in the foreground, wait for the result in the same turn, and never end your turn while a role is running, because ending the turn ends the session and abandons the run; any other headless launcher (a dogfood script) must set `SDLC_HEADLESS=1` itself, and `hooks/block-background.sh` denies background Bash, Agent, and Monitor calls then. In an interactive session a role, or a bench task's full /chain, can take 15 to 30 minutes: spawn with `run_in_background: true`, end the turn, and the completion notification re-invokes the session. Never poll with `sleep`. Once notified, read the result from `<role>-<level>.md`.

Run each task (or only the named one) in turn:

1. `git -C <repo> worktree add --detach <mktemp -d> <base>`. Builders skip permissions, so never run in the user's working tree. `cd` into the worktree and run `setup`.
2. Write everything from `## Goal` down to `.sdlc/bench-<name>/handoff.md`. Never show the agents the header fields, the solution, or the hidden tests.
3. Run the /chain flow on that handoff, skipping the file stage. Stop the task (record `blocked`) wherever /chain would ask the user.
4. Grade: copy each `test_paths` file from `tests_from` (`git -C <repo> show <tests_from>:<path> > <path>`), run `check`, and write `grade.md` in the task dir: `hidden_check: pass|fail`, the exit code, and the last 20 lines of output.
5. Move `.sdlc/bench-<name>` to `$BENCH/results/<YYYY-MM-DD>-<name>/`, then `git -C <repo> worktree remove --force` the worktree and `git -C <repo> worktree prune`.

Then run `${CLAUDE_PLUGIN_ROOT}/scripts/bench-summary.sh --bench-dir "$BENCH"` and report its table, plus the change from each task's previous run. The hidden check is the real score; the verifier's verdict is reported next to it, and any case where the verifier passed but the hidden check failed is flagged 🔴 (the verifier missed a defect).
