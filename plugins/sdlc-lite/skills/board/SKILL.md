---
name: board
description: The status board for sdlc work: one table (Task, Step, Status, %) rendered from .sdlc/ by scripts/board.py, never written by hand; gains optional ID and Ticket columns when a rendered task's handoff.md has ticket front matter. Use for any status ask ("status?", "where are we", "show the board", "what is running") and at every natural pause in /chain or /bench.
argument-hint: [task] [--root DIR]
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py:*)
---
Arguments: `$ARGUMENTS`

1. Write one waiting line: `Waiting on: builder L3, step 2` or `Waiting on you: approve publishing`. If nothing is running or pending, `Waiting on: nothing`.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py --waiting "<line>"`, adding `--task <slug>` if a task was named and `--root <dir>` if given (`bench/results` for benchmark runs).
3. Print stdout verbatim as the whole reply. No text before or after it.
4. Exit 1 means nothing to render: report stderr in one sentence.

Rules:
- Render, never compose. Never hand-write or edit a board table.
- Glyphs are states: 🟢 verifier pass, 🟡 running or awaiting verify, 🔴 blocked or failed, ⏳ queued.
- % comes only from the script's ladder (0 queued, 10 building, 50 built, 70 verifying, 100 verifier pass).
- ID and Ticket columns appear only when at least one rendered task's `handoff.md` has ticket front matter; a task without front matter gets empty cells in those columns, and a task dir with no front matter anywhere still renders the plain 4-column table.
- Decisions never go in the board; they go through AskUserQuestion.
