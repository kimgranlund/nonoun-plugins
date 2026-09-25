<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/planner.md: replaced the fourth merge-step criterion with the new guard line.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: made the same replacement, so the two blocks are byte-identical.

## Checks
- The first two `grep -qF` criteria and the negated third one all passed.
- `plugins/sdlc-lite/scripts/check.sh` exited 0. Its selftests, shellcheck and plugin validate all passed.
- I did not run the new guard span against a real merge or a real conflict marker. That means the empty-path and marker-hit behaviours described in the handoff are untested here.

## Notes
- None. Nothing was committed.
