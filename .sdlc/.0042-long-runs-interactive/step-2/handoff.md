## Task goal
The docs for /chain, /bench and the conductor say how to run a role that takes longer than the Bash tool's 10-minute cap in an interactive session.

## Step 2: Document foreground vs background runs
level: L2
### Do
Edit these three files:
- `plugins/sdlc-lite/skills/chain/SKILL.md` (the intro paragraph)
- `plugins/sdlc-lite/skills/bench/SKILL.md` (line 11)
- `plugins/sdlc-lite/agents/conductor.md` (the "How you run roles" first bullet)

Both cases go in each file:
- **Headless** (`claude -p`, including `scripts/bench.sh`, which raises `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`): run in the foreground with `timeout` at 600000 or more and never `run_in_background`. Ending the turn ends the session and abandons the run.
- **Interactive**: a role or a bench task's full /chain can take 15 to 30 minutes, past the Bash tool's 10-minute cap. Run `run.sh` with `run_in_background: true`, then wait for the completion notification. Never poll with `sleep`. Read the result from `<role>-<level>.md` once notified. Ending the turn is safe here because the notification re-invokes the session.

Update the hazard line in `.claude/agents/sdlc-lite-author.md` (line 26) to match. Use no em dashes.

Also check `plugins/sdlc-lite/CLAUDE.md`. It has no line on this today, so add one under Decisions only if it fits the "Headless runs" bullet.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` exits 0.
- `plugins/sdlc-lite/scripts/check.sh` passes, apart from the expected CLAUDE.md validate warning.
- `grep -c "run_in_background" plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/skills/bench/SKILL.md plugins/sdlc-lite/agents/conductor.md` shows at least 1 in each file.
- `grep -n "—"` on the four edited files adds no em dashes.
- Each file states both cases (headless foreground, interactive background) and says never to poll with `sleep`.
