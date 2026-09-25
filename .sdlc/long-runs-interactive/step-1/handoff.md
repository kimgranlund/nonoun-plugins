## Task goal
The docs for /chain, /bench and the conductor say how to run a role that takes longer than the Bash tool's 10-minute cap in an interactive session.

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
