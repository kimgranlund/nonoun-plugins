<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: added `.sdlc/roadmap.md` and `.sdlc/_templates/<type>.md` to the Layout block. The "Ticket front matter" section now says `/ticket new` stamps the fields, `/ticket check` validates them, and `tickets.py` is the only parser of front matter. The sentence saying `run.sh` and `board.py` do not parse it is unchanged and still true.
- `CLAUDE.md`: added `/ticket` to the workflow skills list. Added a `scripts/tickets.py` bullet covering its commands, `--root`, and the template lookup order. The check.sh description in Commands now lists the tickets selftest.
- `plugins/sdlc-lite/agents/conductor.md`: added the route line `- New ticket, or roadmap → /sdlc-lite:ticket`.
- `.claude/agents/sdlc-lite-author.md`: its list of what check.sh runs now includes the tickets selftest. It has no skills list, so `/ticket` was not added there.

## Checks
- `grep -n 'roadmap.md'` on handoff-format SKILL.md: lines 21 and 45.
- `grep -n '/ticket'` on handoff-format SKILL.md: lines 22, 45 and 49.
- `grep 'tickets.py' CLAUDE.md`: 1 line. `grep '/ticket' CLAUDE.md`: 3 lines.
- `grep -n 'sdlc-lite:ticket'` on conductor.md: 1 line (line 14).
- The "neither `run.sh` nor `board.py`" sentence is still there and still true. No sentence says nothing parses front matter.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. The coverage_check selftest, the tickets selftest, shellcheck and plugin validate all passed.
- `git diff --stat`: shows the 4 files named in Do, plus `plugins/sdlc-lite/scripts/check.sh`. That check.sh change was already uncommitted before this step started (from an earlier step); this step did not edit it.

## Notes
None
