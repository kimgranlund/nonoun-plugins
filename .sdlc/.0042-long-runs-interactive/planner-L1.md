<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
The docs for /chain, /bench and the conductor say to run roles in the foreground only in headless sessions, and in interactive sessions to run them in the background and wait for the completion notification without polling.

## Step 1: Add a failing doc-consistency check
level: L2
### Do
In `plugins/sdlc-lite/scripts/check.py`, before the final error print, add a check over `skills/chain/SKILL.md`, `skills/bench/SKILL.md` and `agents/conductor.md`. Each file must state that:
- an interactive session runs roles with `run_in_background` and waits for the completion notification;
- it never polls with `sleep`;
- the foreground `timeout` rule applies to headless sessions only.

Test for the words `interactive`, `run_in_background`, `notification` and `sleep` in each file. Also require that no file still says `never run_in_background` unqualified. Add the same requirement to `.claude/agents/sdlc-lite-author.md` (its hazard line, so the mirror stays in sync).

Run the check before Step 2 to see it fail on the three docs. The check lands with or before the doc fix.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` exits 1 and prints a FAIL line naming each of chain, bench and conductor. This run is done before Step 2.
- The check is a plain string test on the file text, not a grep on a possibly missing path. A missing file also fails.
- `shellcheck` and the other selftests are unaffected.

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

## Risks
- Interactive mode is detected only by the model's own knowledge of its session type. The docs must say how to tell: a `claude -p` run or a `bench.sh` run is headless, and anything else is interactive.
- `run_in_background` needs the harness to re-invoke the session on exit. I believe the Bash tool does this, but I did not verify it in a live interactive run. The author's rule 3 (one live run on a throwaway repo) should cover it.
- A string-matching check can pass on wording alone without the docs being right. The live run is the real test.
