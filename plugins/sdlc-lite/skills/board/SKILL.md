---
name: board
description: The status board for sdlc work: one table (Task, Step, Status, %) rendered from .sdlc/ by scripts/board.py, never written by hand; gains optional ID and Ticket columns when a rendered task's handoff.md has ticket front matter. Use for any status ask ("status?", "where are we", "show the board", "what is running") and at every natural pause in /chain or /bench.
argument-hint: [task] [--root DIR] [--sort {recent,id,name}] [--lanes]
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py:*)
---
Arguments: `$ARGUMENTS`

1. Write one waiting line: `Waiting on: builder L3, step 2` or `Waiting on you: approve publishing`. If nothing is running or pending, `Waiting on: nothing`.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py --waiting "<line>"`, adding `--task <slug>` if a task was named, `--root <dir>` if given (`<bench dir>/results` for benchmark runs, see `scripts/bench-dir.sh`), and `--sort <mode>` if given. With no flag, the default order is by ticket id when any rendered task has a ticket (unticketed tasks follow by recency), otherwise by recency. `recent` (mtime), `id` (ticket id as in the roadmap) and `name` (folder name) override. For a "lanes" or "worktrees" ask, pass `--lanes` instead of `--task` and `--sort`.
3. Print stdout verbatim as the whole reply. No text before or after it.
4. Exit 1 means nothing to render: report stderr in one sentence.

Rules:
- Render, never compose. Never hand-write or edit a board table.
- Glyphs are states: 🟢 verifier pass, 🟡 running or awaiting verify, 🔴 blocked or failed, ⏳ queued.
- % comes only from the script's ladder (0 queued, 10 building, 50 built, 70 verifying, 100 verifier pass).
- ID and Ticket columns appear only when at least one rendered task's `handoff.md` has ticket front matter; a task without front matter gets empty cells in those columns, and a task dir with no front matter anywhere still renders the plain 4-column table.
- The board lists the live set only: a ticketed task is left off entirely when it is `dropped`, or `done` with no recorded step work (no planner file, step dir, or running marker); proposed, ready, and blocked tickets stay visible even without steps.
- If the render ends with a legacy `.board-state.json` hint line, print it verbatim like the rest. The file is safe to delete; board.py never touches it.
- `--lanes` lists every `git worktree list` entry with its branch and that worktree's `--summary` line (`no tasks` when it has none), one row per lane; it leaves the default board unchanged and exits 1 outside a git work tree.
- Decisions never go in the board; they go through AskUserQuestion.
