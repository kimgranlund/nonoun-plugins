<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/board/SKILL.md`: step 2 now states the new default (ticket id when any rendered task has a ticket, unticketed tasks after by recency, otherwise recency). `recent`, `id` and `name` override.
- `CLAUDE.md`: Feed bullet states the new default and says `--sort recent` restores recency.

## Checks
- `scripts/check.sh` (run from the repo root as `plugins/sdlc-lite/scripts/check.sh`): all checks passed, including tickets selftest, board selftest, shellcheck and plugin validate. I only looked at the last 8 lines of its output.
- `grep -n "default" plugins/sdlc-lite/skills/board/SKILL.md`: no matches. The new text says "With no flag", so the word "default" no longer appears there. I did not run the grep on `CLAUDE.md`.
- `grep -n -i "sort\|recen" .claude/agents/sdlc-lite-author.md`: no matches, so I left that file unchanged.
- `sed` on `board.py` lines 455-463: `sort_tasks` is called only at the render path (line 461), with mode `auto` when tickets exist, else `recent`. I did not open `summary()`, so the statusline risk is not confirmed.

## Notes
- I left `argument-hint` unchanged.
- I did not check whether any doc or script assumes newest-last order.
- The diff also shows changes to `board.py` and `decide-whether-board-should-default/handoff.md`. Those came from an earlier step, not this one.
