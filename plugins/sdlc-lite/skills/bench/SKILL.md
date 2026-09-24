---
name: bench
description: Benchmark the agent team: run each saved task through /chain in a throwaway worktree, grade it with the real solution's hidden tests, and compare pass rate, cost, and attempts across runs. Use after changing a role, a level table, or a rubric.
argument-hint: [task name]
allowed-tools: Bash, Read, Write, Grep, Glob
---
Arguments: `$ARGUMENTS`

Tasks live in `${CLAUDE_PLUGIN_ROOT}/bench/tasks/<name>.md` (format in `bench/tasks/README.md`). If there are none, say so and stop. Run every `run.sh` call in the foreground with the Bash tool's `timeout` set to 600000 or more, never `run_in_background`, and never end your turn while a role is running: in a headless session, ending the turn ends the session and abandons the run.

Run each task (or only the named one) in turn:

1. `git -C <repo> worktree add --detach <mktemp -d> <base>`. Builders skip permissions, so never run in the user's working tree. `cd` into the worktree and run `setup`.
2. Write everything from `## Goal` down to `.sdlc/bench-<name>/handoff.md`. Never show the agents the header fields, the solution, or the hidden tests.
3. Run the /chain flow on that handoff, skipping the file stage. Stop the task (record `blocked`) wherever /chain would ask the user.
4. Grade: copy each `test_paths` file from `tests_from` (`git -C <repo> show <tests_from>:<path> > <path>`), run `check`, and write `grade.md` in the task dir: `hidden_check: pass|fail`, the exit code, and the last 20 lines of output.
5. Move `.sdlc/bench-<name>` to `${CLAUDE_PLUGIN_ROOT}/bench/results/<YYYY-MM-DD>-<name>/`, then `git -C <repo> worktree remove --force` the worktree and `git -C <repo> worktree prune`.

Then run `${CLAUDE_PLUGIN_ROOT}/scripts/bench-summary.sh` and report its table, plus the change from each task's previous run. The hidden check is the real score; the verifier's verdict is reported next to it, and any case where the verifier passed but the hidden check failed is flagged 🔴 (the verifier missed a defect).
