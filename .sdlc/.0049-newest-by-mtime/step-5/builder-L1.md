<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the runs.jsonl field list now includes `file`. The line that said "the newest file by mtime is the current one" now gives the `order.py` rule. The `planner-L3-2.md` comment now says "the latest runs.jsonl record is current".
- `CLAUDE.md`: added a `scripts/order.py` bullet to the Layout section. It states the ordering rule, that runs.jsonl lines carry `file`, and that `check.sh` runs its selftest.
- `.claude/agents/sdlc-lite-author.md`: added an invariant that verdict and newest-file decisions go through `order.py` and never use mtime.
- `plugins/sdlc-lite/scripts/tickets.py` and `plugins/sdlc-lite/scripts/steps.py`: reworded one comment each from "never by mtime" to "never by file time". This is a comment-only change.

## Checks
- The `grep -rn -i "by mtime"` command from the acceptance criteria now returns only `board.py` lines 253, 256, 453, 482 and 487. These are task-display-order text.
- `grep -n "order.py"` finds a match in all three files: `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md` and `handoff-format/SKILL.md`.
- `plugins/sdlc-lite/scripts/check.sh` passed; the last lines were "order selftest: PASS", "run selftest: PASS", "ok: shellcheck" and "ok: plugin validate". I piped its output through `tail -15`, so the reported `rc=0` is `tail`'s exit code, not `check.sh`'s. I did not see the CLAUDE.md validate warning in that output; it may be earlier than the last 15 lines.

## Notes
- The two comment rewrites in `tickets.py` and `steps.py` go beyond the handoff's file list. Without them, the first grep matched "never by mtime" in those comments and failed the criterion.
- I left the board SKILL's `recent (mtime)` wording alone, as the handoff said.
