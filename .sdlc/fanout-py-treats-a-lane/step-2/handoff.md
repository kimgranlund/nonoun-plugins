## Task goal
When a fanout lane's task stops on an `inherited red` builder, `fanout.py` reports that cause and the inherited tests, and does not merge or close the half-done ticket, so the operator sees "main was already red" instead of a misleading merge or close refusal.

## Step 2: Document the outcome and guard it in check.py
level: L2
### Do
Make each of these edits:

- `CLAUDE.md` (repo root), in the `scripts/fanout.py` bullet: after the driver step, say that a driver run leaving a `step-<n>/` whose `steps.py next` action is `inherited` gives the outcome `inherited red: step-<n>: <tests>`. That outcome means no lane commit, no merge, no close, the lane stops, and the work stays in the lane worktree.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`, section 4 Report or 5 Main: one line saying an `inherited red: step-<n>: <tests>` outcome means those gate tests were already red on the base. Fix main first. Nothing from that ticket was merged.
- `.claude/agents/sdlc-lite-author.md`, the `Inherited-red route:` line: add `fanout.py` (outcome `inherited red: step-<n>: <tests>`) to what it maps to, and add `fanout.py` and the /fanout skill to its keep-in-sync list.
- `plugins/sdlc-lite/scripts/check.py`: add `'scripts/fanout.py'` and `'skills/fanout/SKILL.md'` to `INHERITED_RED_DOCS`, and update docstring item 8 to name both.
### Acceptance criteria
- `grep -q "inherited red" plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -n "scripts/fanout.py" CLAUDE.md | grep -q "inherited red"`
- `sed -n '/Inherited-red route/p' .claude/agents/sdlc-lite-author.md | grep -q fanout.py`
- `grep -A1 'INHERITED_RED_DOCS = ' plugins/sdlc-lite/scripts/check.py | grep -q fanout`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- Observable: no doc says that fanout ignores inherited red or treats it like any other non-merged outcome. The chain SKILL and conductor.md unattended rule ("stop the task and report the inherited tests") stays unchanged.
