<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
fail

## Criteria
- `grep -n "default" plugins/sdlc-lite/skills/board/SKILL.md CLAUDE.md` shows the new default wording, with no remaining claim that recency is the unconditional default: fail. Evidence: I ran that exact grep on the working tree. It matched only `CLAUDE.md:25`, the unrelated "(default `.sdlc`)" and "plain slugs are the default" text in the tickets bullet, and `CLAUDE.md:55`, "Clean context is the default". It did not match `SKILL.md` at all, and it did not match the new Feed bullet. The new wording is in both files (`SKILL.md:10` "With no flag, order is by ticket id when any rendered task has a ticket (unticketed tasks follow by recency), otherwise by recency", and the `CLAUDE.md` Feed bullet "with no `--sort` it orders by ticket id ... `--sort recent` restores recency"), but it avoids the word "default", so the named check cannot see it. Only the "no remaining claim" half holds. At HEAD the same grep shows `SKILL.md:10` "`recent` by mtime is the default" and `CLAUDE.md:23` "instead of the default recency (`recent`)", and neither appears in the working tree now. The wording also has a defect: `SKILL.md:10` ends with "override.." (a doubled period). The wording itself matches the code: `board.py:460` sets `mode = a.sort or ('auto' if any(ticket_of(t) for t in tasks) else 'recent')`, and `board.py:216` sorts unticketed tasks by mtime in `auto` mode.
- `plugins/sdlc-lite/scripts/check.sh` passes, including the board selftest: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh >/dev/null 2>&1; echo $?` printed `0`. Its output tail: `selftest: PASS`, `tickets selftest: PASS`, `board selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`. The board selftest has an assertion for this default: `board.py:428` "no --sort without tickets equals --sort recent".
- `.claude/agents/sdlc-lite-author.md` edited only if it mentions a sort default: pass. Evidence: `grep -n -i "sort\|recen" .claude/agents/sdlc-lite-author.md` found no matches, and the file is unchanged in `git status`.
- No em dashes: pass. Evidence: `grep -n "—" plugins/sdlc-lite/skills/board/SKILL.md CLAUDE.md` found no matches.

## Out of scope changes
None from this step. `plugins/sdlc-lite/scripts/board.py` and `.sdlc/decide-whether-board-should-default/handoff.md` are modified, but those changes belong to step 1 of the same task. The builder report says so too.

## For the next attempt
- `plugins/sdlc-lite/skills/board/SKILL.md:10`: say "default" in the new sentence so the acceptance grep can find it, for example "With no flag, the default order is by ticket id when...". Also change "override.." to "override.".
- `CLAUDE.md` Feed bullet: use the word "default" the same way, for example "by default (no `--sort`) it orders by ticket id...", so the grep shows the new wording.
- Keep "`--sort recent` restores recency" and use no em dashes.
