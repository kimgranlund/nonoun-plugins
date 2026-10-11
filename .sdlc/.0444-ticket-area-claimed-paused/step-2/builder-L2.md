<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/b/plugins/sdlc-lite/skills/ticket/templates/{bug,chore,feature,idea,spike}.md: the status comment now lists all seven statuses, including claimed and paused.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/b/plugins/sdlc-lite/skills/handoff-format/SKILL.md: new status line, plus the `paused_reason:` and `area:` lines; the `claimed_by:` comment now says it is required for claimed; the status paragraph names claimed and paused.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/b/plugins/sdlc-lite/skills/ticket/SKILL.md: one new rule bullet covering area and `areas:`, claimed with `claimed_by:`, paused with `paused_reason:`, and that existing tickets need no migration.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/b/docs/specs/sdlc-lite/lane-lifecycle.md: new section 8.2 with the mapping table, a note that it is mapping text only, the L5 note and the no-migration statement.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/b/docs/references/sdlc-internals.md: the Feed board sentence now gives the Ticket cell as `<status> · <area>`; the tickets.py section now covers the statuses, `claimed_by:`/`paused_reason:`, `areas:` with `config_areas`, the Area column, the router paused text, and no migration.

## Checks
- c1 to c5 (red criteria, run after the edits): all exit 0.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0
- `git diff --check 222f817e -- plugins docs`: exit 0
- `python3 scripts/check-packaging.py`: exit 0
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0
- Scope guard (only the named files changed outside .sdlc): exit 0, no extra paths.
- `redck.py record` (run before the first edit): it recorded 5 controls, red at base. It marked them retrospective because step 1's source changes were already in the tree.

## Notes
The red checkpoint is marked retrospective only because step 1's uncommitted changes to tickets.py and board.py were in the tree before this step. It ran before any edit from this step. `docs/specs/ticket-stages/design.md` was left untouched, as the handoff says.
