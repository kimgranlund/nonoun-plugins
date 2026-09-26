---
name: fanout
description: "Run ticket lanes in parallel: each lane is a git worktree whose tickets run through a headless /chain one at a time, merge into an integration branch behind gates, and close there. Use when several ready tickets can run side by side."
argument-hint: <lane>=<ids>... [--base REF] [--integration BRANCH] [--gate CMD]... [--lanes-dir DIR]
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py:*), Bash(git merge --ff-only:*), Read
---
Arguments: `$ARGUMENTS`

Run from the project root. `fanout.py` makes commits only inside the lanes dir (the lane branches and the integration branch); it never touches main and never pushes. Lane worktrees stay after the run so they can be inspected.

Lanes live in `<toplevel>/.worktrees/fanout/<lane>` by default (`--lanes-dir` overrides). `.worktrees/` must be in `.gitignore`; otherwise preflight refuses with exit 2 and says to add it, and an explicit `--lanes-dir` inside the tree must be ignored too. Caveat: `.gitignore` does not exclude `.worktrees/` from vitest, tsc, or file watchers, so exclude it in the project's own config; Node module resolution also walks up from a lane worktree into the main tree's `node_modules`.

## 1. Dry run
Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run <arguments> --gate "<cmd>"... --dry-run`, adding the project's own check or test commands (for example `scripts/check.sh` or the test command from its README or CLAUDE.md) as `--gate`s unless the arguments already name gates. Show the plan it prints. A refusal (exit 2) stops here: show it and fix the arguments with the user.

## 2. Confirm
Ask with AskUserQuestion which lanes and gates to run. Recommended first: run as planned. Other choices: change the gates, change the lanes, cancel.

## 3. Run
Run the same command without `--dry-run`. A fanout runs full /chain loops per ticket and can take hours. Headless (`claude -p`): run it in the foreground with the Bash tool's `timeout` at 3600000, do not use `run_in_background` there, and never end the turn while it runs, because that ends the session and abandons the lanes. `hooks/block-background.sh` denies Bash `run_in_background` calls and denies any Agent call unless `run_in_background` is explicitly `false` (Agent runs in the background by default, so a missing field counts as background) whenever `SDLC_ROLE` is set or `SDLC_HEADLESS=1`; bench.sh and fanout set `SDLC_HEADLESS=1`, and any other headless launcher (a dogfood script) must set `SDLC_HEADLESS=1` itself. In an interactive session: run it with `run_in_background: true` and wait for the completion notification. Never poll with `sleep`. Ending the turn is safe there because the notification re-invokes the session.

## 4. Report
When notified, print `<lanes-dir>/report.md` verbatim, then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py --lanes --waiting "<one line on what is next>"` verbatim. That is the status output; do not restate it.

## 5. Main
Ask with AskUserQuestion. When every ticket merged, recommended first: fast-forward main with `git merge --ff-only <integration>` in the main worktree. The other choice: leave main as it is. When some ticket did not merge, recommend leaving main and name the lanes to inspect. Run that one `git merge --ff-only` only after the user picks it. Never push, and never merge any other way.
