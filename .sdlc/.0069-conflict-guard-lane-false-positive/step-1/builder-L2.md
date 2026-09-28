<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/planner.md: in the merge-step block, the conflict-marker guard span is now `out=$(git diff-tree --cc HEAD) && ! printf ... | grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"`
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: the same line, so both blocks stay byte-identical
- plugins/sdlc-lite/scripts/check.py: the behavior probe now runs five cases: empty, marker added by the merge commit, legit lane line, real conflict kept, and clean. Its comment and docstring item 6 are updated to match.

## Checks
- `grep -q 'git diff-tree --cc HEAD'` in planner.md: exit 0
- `grep -q 'git diff-tree --cc HEAD'` in handoff-format/SKILL.md: exit 0
- `! grep -q 'xargs -0 sh -c'` in planner.md: exit 0
- Old-guard negative control (7e51f1b archive): check.py printed `legit lane line flagged`, grep exit 0
- Kept-conflict negative control (span replaced with `true "<<<<<<<"` in a temp copy): check.py printed `FAIL merge-step conflict-marker guard: kept conflict markers not flagged`, and also the marker FAIL
- `python3 plugins/sdlc-lite/scripts/check.py`: ok, exit 0
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0, with the hook selftest, shellcheck, and plugin validate all passing
- `git diff --quiet HEAD -- steps.py builder.md`: exit 0

## Notes
In the marker case, the lane branch adds a separate file (`m.txt`) so the merge has something to bring in. The merge commit itself then appends `>>>>>>> evil` to `sp ace.txt`.
