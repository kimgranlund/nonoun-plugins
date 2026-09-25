## Task goal
Which result is newest (builder, verifier, planner) is decided from recorded run order, so a fresh clone or a committed .sdlc/ trail reads the same verdicts as the machine that ran them.

## Step 5: Docs say runs.jsonl order, not mtime
level: L1
### Do
Replace the mtime wording with the rule: "newest = latest runs.jsonl record (run.sh records `file`), else level then rerun index then name; never mtime".
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`:
  - line 27 ("the newest file by mtime is the current one")
  - line 16: the runs.jsonl fields now include `file`
- `CLAUDE.md` (repo root), Layout section:
  - mention `scripts/order.py` as the shared ordering rule, and that check.sh runs its selftest
  - note that runs.jsonl lines carry `file`
- `.claude/agents/sdlc-lite-author.md`: add the invariant that verdict and newest-file decisions go through `order.py` and never use mtime. Keep it in sync with CLAUDE.md.
- `plugins/sdlc-lite/skills/board/SKILL.md`: leave the `recent (mtime)` wording. It is task display order.
### Acceptance criteria
- `grep -rn -i "by mtime" plugins/sdlc-lite/skills plugins/sdlc-lite/agents plugins/sdlc-lite/scripts CLAUDE.md .claude/agents` returns only task-display-order text (board SKILL `--sort recent`, and board.py's `sort_tasks` docstring and selftest).
- `grep -n "order.py" CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/skills/handoff-format/SKILL.md` finds each file.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The only validate warning is the expected one about CLAUDE.md.
