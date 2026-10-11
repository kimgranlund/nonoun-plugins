## Task goal
A ticket can carry a domain `area:`, and its status can say `claimed` and `paused`, with the roadmap, board and tracker mapping showing them.

## Step 3: Loose ends
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
- In `plugins/sdlc-lite/scripts/traces/sources/tickets.py`, the `tickets.problems(ts, tickets.config_numbered(root))` call passes no `areas=`, so trace validation skips the area check that step 1 added. Pass `areas=tickets.config_areas(root)` in that call. Change nothing else.
### Acceptance criteria
- (red) `grep -qF "areas=tickets.config_areas(root)" plugins/sdlc-lite/scripts/traces/sources/tickets.py`
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`
- (guard) Only the named file changed beyond steps 1 and 2: `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/traces/sources/tickets.py -e plugins/sdlc-lite/scripts/tickets.py -e plugins/sdlc-lite/scripts/board.py -e plugins/sdlc-lite/skills/ticket/SKILL.md -e plugins/sdlc-lite/skills/ticket/templates/bug.md -e plugins/sdlc-lite/skills/ticket/templates/chore.md -e plugins/sdlc-lite/skills/ticket/templates/feature.md -e plugins/sdlc-lite/skills/ticket/templates/idea.md -e plugins/sdlc-lite/skills/ticket/templates/spike.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e docs/specs/sdlc-lite/lane-lifecycle.md -e docs/references/sdlc-internals.md); test -z "$out"`
