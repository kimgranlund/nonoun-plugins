<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `CLAUDE.md`: in the `scripts/fanout.py` bullet, the driver step now says that an `inherited` step gives the outcome `inherited red: step-<n>: <tests>`. That outcome means no lane commit, no merge, no close, the lane stops, and the work stays in the lane worktree.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: section 4 Report has one new line. It says the outcome means those gate tests were already red on the base, main should be fixed first, and nothing from that ticket was merged.
- `.claude/agents/sdlc-lite-author.md`: the `Inherited-red route:` line now names the fanout.py lane outcome. fanout.py and the /fanout skill are added to its keep-in-sync list.
- `plugins/sdlc-lite/scripts/check.py`: `'scripts/fanout.py'` and `'skills/fanout/SKILL.md'` are added to `INHERITED_RED_DOCS`, and docstring item 8 now names both.

## Checks
- `grep -q "inherited red" plugins/sdlc-lite/skills/fanout/SKILL.md`: pass
- `grep -n "scripts/fanout.py" CLAUDE.md | grep -q "inherited red"`: pass
- `sed -n '/Inherited-red route/p' .claude/agents/sdlc-lite-author.md | grep -q fanout.py`: pass
- `grep -A1 'INHERITED_RED_DOCS = ' plugins/sdlc-lite/scripts/check.py | grep -q fanout`: failed on the first layout, where the new entries were on the tuple's third line. I reordered the tuple so they sit on its second line, and it now passes.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0, run twice (once after each layout).
- Observable criterion: I made no edits to the chain SKILL or `conductor.md`. No doc was changed to say that fanout ignores inherited red.

## Notes
The `INHERITED_RED_DOCS` entries are not in their old order: the two fanout paths sit on the tuple's second line because the `grep -A1` criterion only reads one line past the assignment. The step 1 changes to `fanout.py` were already uncommitted in the tree when this step started. I left them untouched.
