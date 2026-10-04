---
name: fanout
description: "Run ticket lanes in parallel: each lane is a git worktree whose tickets run one at a time through the lane `steps.py lane` picks (the `solo` agent for size S and M, the headless /chain for the rest), merge into an integration branch behind gates, and close there. Use when several ready tickets can run side by side."
argument-hint: "<lane>=<ids>... <lane>@<branch>=<ids>... [--base REF] [--integration BRANCH] [--gate CMD]... [--lanes-dir DIR] [--rewrite-refs] [--lane auto|solo|full] [--max-lanes N] [--stagger SECS]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py:*), Bash(git merge --ff-only:*), Read
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

For every role launch, set `SDLC_ROUTING_REASON` to the selected role/level rationale, including the recorded cause of any escalation or replan. Read [shared run operations](../handoff-format/run-operations.md) for readiness, attempt records, and safe recovery.

Arguments: `$ARGUMENTS`

Run from the project root. `fanout.py` makes commits only inside the lanes dir (the lane branches and the integration branch); it never touches main and never pushes. Lane worktrees stay after the run so they can be inspected. When a lane stops on a driver failure or any outcome other than `merged`, a dirty lane tree is committed as `wip(<id>): <outcome>` on the lane branch only (never merged). A tree already dirty before a ticket's sync is WIP-committed as `wip(<id>): dirty before sync` and that ticket stops with the outcome `dirty before sync`, never merged. An integration worktree with uncommitted tracked changes is refused before the merge with the outcome `integration dirty: <path>`; nothing is merged or reset, so the edit survives. Inspect a stopped lane's `wip(` commit on its lane branch.

Solo first: for each ticket `fanout.py` runs `steps.py lane` in the lane worktree and follows it. `solo` (size S and M by default) starts the `solo` agent from a typed brief at the tier's model and effort, in a headless session (Claude: `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo`; Codex: `sdlc-solo-l1` to `l3` through `codex_exec.py`). A size M ticket then needs one independent batched verifier with Verdict pass, from the solo or else one fanout runs, before any merge. Anything else keeps the headless conductor running /chain. `--lane solo` or `--lane full` forces the choice, and the report lists each ticket's lane. One run holds at most `--max-lanes` lanes (default 4; above 16 it also needs `--yes-many`), starts them `--stagger` seconds apart (default 20; your plan limit and merge conflicts are the real limits, not the machine), and refuses two tickets in different lanes whose planned scope overlaps unless `--allow-overlap`. A good first run is 4 to 6 lanes of tickets that touch different files.

Lanes live in `<toplevel>/.worktrees/fanout/<lane>` by default (`--lanes-dir` overrides). `.worktrees/` must be in `.gitignore`; otherwise preflight refuses with exit 2 and says to add it, and an explicit `--lanes-dir` inside the tree must be ignored too. Caveat: `.gitignore` does not exclude `.worktrees/` from vitest, tsc, or file watchers, so exclude it in the project's own config; Node module resolution also walks up from a lane worktree into the main tree's `node_modules`.

An external lane (`<lane>@<branch>=<ids>`) names a branch an outside agent (for example Codex) owns, registered with an `external_branch: <branch>` line in `.sdlc/config`. Fanout runs no driver on it, creates no worktree and no `<integration>-<lane>` branch, and never writes that branch. It is merged `--no-ff` into the integration branch under the lock, gated, and its tickets are closed there; a second ticket on the same branch merges nothing new and skips the gates. A `merge conflict` outcome means the outside agent merges the integration branch on their side before the run is repeated. The lane shows in `report.md` but not in `board.py --lanes`, which lists worktrees.

## 1. Dry run
Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run <arguments> --gate "<cmd>"... --dry-run`, adding the project's own check or test commands (for example `scripts/check.sh` or the test command from its README, AGENTS.md, or CLAUDE.md) as `--gate`s unless the arguments already name gates. Show the plan it prints; its `close:` line shows whether the repo is in numbered mode. A refusal (exit 2) stops here: show it and fix the arguments with the user.

## 2. Confirm
Ask with AskUserQuestion which lanes and gates to run. Recommended first: run as planned. Other choices: change the gates, change the lanes, cancel.

When the plan's `close:` line says `numbered folders`, also ask, as a separate AskUserQuestion choice, whether to add `--rewrite-refs`: it rewrites files that cite a closed ticket's folder to its `.NNNN-<slug>` path. Never add it unless the user picks it; step 3 runs with the flag only if they did. A `merged, close refused` outcome naming `--rewrite-refs` means a citing file blocked the close.

## 3. Run
Run the same command without `--dry-run`. A solo ticket takes minutes; a fanout that sends tickets through the full /chain can take hours. Headless (`claude -p`): run it in the foreground with the Bash tool's `timeout` at 3600000, do not use `run_in_background` there, and never end the turn while it runs, because that ends the session and abandons the lanes. `hooks/block-background.sh` denies Bash `run_in_background` calls and denies any Agent call unless `run_in_background` is explicitly `false` (Agent runs in the background by default, so a missing field counts as background) whenever `SDLC_ROLE` is set or `SDLC_HEADLESS=1`; bench.sh and fanout set `SDLC_HEADLESS=1`, and any other headless launcher (a dogfood script) must set `SDLC_HEADLESS=1` itself. In an interactive session: run it with `run_in_background: true` and wait for the completion notification. Never poll with `sleep`. Ending the turn is safe there because the notification re-invokes the session.

## 4. Report
When notified, print `<lanes-dir>/report.md` verbatim, then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py --lanes --waiting "<one line on what is next>"` verbatim. That is the status output; do not restate it. An `inherited red: step-<n>: <tests>` outcome means those gate tests were already red on the base: fix main first; nothing from that ticket was merged. Fanout's close is the plain form (no `--ticket`), so a lane files no follow-up ticket and every follow-up item lands in `notes.md` on the integration branch.

## 5. Main
Ask with AskUserQuestion. When every ticket merged, recommended first: fast-forward main with `git merge --ff-only <integration>` in the main worktree. The other choice: leave main as it is. When some ticket did not merge, recommend leaving main and name the lanes to inspect. Run that one `git merge --ff-only` only after the user picks it. Never push, and never merge any other way.
