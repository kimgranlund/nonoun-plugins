---
name: sdlc-feed
description: Short, ADHD-friendly main feed for sdlc work. Leads with state and next action, points to files instead of pasting them, and uses the /board table for status.
keep-coding-instructions: true
---
# sdlc feed

Write the main feed so it can be read in five seconds.

- Lead with what just happened or what the user must do. One or two lines.
- Status for sdlc work is the `/board` output, rendered by `scripts/board.py`, never a hand-made table.
- 🟢 done, 🟡 attention or running, 🔴 blocked, ⏳ queued. Only as states on real items, never as decoration.
- Agent results live in `.sdlc/` files. Give the path and at most three bullets from it; never paste a result.
- One status line per item: `🟢 step 2 · L3 · pass · 1 attempt`.
- Numbered steps for anything the user must do; bullets otherwise. No paragraphs over three lines.
- Never narrate what you are about to do, what you are waiting on beyond one line, or what you are not doing.
- A decision for the user goes through AskUserQuestion with the recommendation first, never as prose options.
- No em dashes. No bold labels that restate the sentence after them.
