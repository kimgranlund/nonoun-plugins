## Task goal
Independently verify T-0219: the skips guard in tickets.py now covers a done ticket whose last lane is solo or full, and still exempts tickets with no lane record or no skips.md.

## Step 1: Verify the skips guard extension
level: L2

### Do
Read-only, in this worktree. Read the diff of plugins/sdlc-lite/scripts/tickets.py and skills/handoff-format/SKILL.md against 244d0af. Confirm lanes lean and fix behave as before, solo needs Skipped entries for planner and filer, full needs the results or entries, an open ticket is not checked, and the old lean-then-full selftest case was changed on purpose (a full lane now needs the full chain's results). Then run the criteria.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite $d/p && sed -i.bak "s/not in ('solo', 'lean', 'fix', 'full'):/not in ('lean', 'fix'):/" $d/p/scripts/tickets.py && ! python3 $d/p/scripts/tickets.py selftest`
- `bash plugins/sdlc-lite/scripts/check.sh`
