## Task goal
With no `--sort` flag, `board.py` orders by ticket id when any rendered task has ticket front matter, with unticketed tasks after it in mtime order. Otherwise it keeps recency order, and an explicit `--sort` behaves exactly as before.

## Step 2: Update the records that describe the default
level: L1
### Do
- `plugins/sdlc-lite/skills/board/SKILL.md`, line 10: replace "`recent` by mtime is the default" with the new default. With no flag, order is by ticket id when any rendered task has a ticket, unticketed tasks follow by recency, and otherwise recency. `recent`, `id` and `name` override.
- Keep `argument-hint` as is, or note the default there if it fits.
- Repo `CLAUDE.md` Feed bullet: replace "instead of the default recency (`recent`)" with the new default, and say `--sort recent` restores recency.
- `.claude/agents/sdlc-lite-author.md`: grep for a sort default. Edit it only if it mentions one.
- Use no em dashes.
### Acceptance criteria
- `grep -n "default" plugins/sdlc-lite/skills/board/SKILL.md CLAUDE.md` shows the new default wording, with no remaining claim that recency is the unconditional default.
- `plugins/sdlc-lite/scripts/check.sh` passes, including the board selftest.

## Risks
- A `/chain` render without `--task` may now show tasks in a different order when tickets exist. This is intended, but verify no doc or script assumes newest-last.
- `statusline.sh` uses `--summary`, which is not affected, but confirm `summary()` does not call `sort_tasks` with the default.
- The selftest expected order depends on the fixture mtimes. The builder must derive it from the `os.utime` values.

## Previous attempt
- `plugins/sdlc-lite/skills/board/SKILL.md:10`: say "default" in the new sentence so the acceptance grep can find it, for example "With no flag, the default order is by ticket id when...". Also change "override.." to "override.".
- `CLAUDE.md` Feed bullet: use the word "default" the same way, for example "by default (no `--sort`) it orders by ticket id...", so the grep shows the new wording.
- Keep "`--sort recent` restores recency" and use no em dashes.
