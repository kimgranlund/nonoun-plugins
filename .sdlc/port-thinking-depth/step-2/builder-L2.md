<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/check.py: added a `'recurring finding'` key to `PLAN_DEFECT_DOCS` covering planner.md, conductor.md, chain, level-rubric, and handoff-format; docstring item 5 now names the recurring-finding rule.
- CLAUDE.md (repo root): the Decisions line now says check.py guards both the `plan defect` tag and the `recurring finding` rule.

## Checks
All of these ran from `plugins/sdlc-lite`:
- Negative control (conductor.md copy with "recurring finding" replaced by "recurring-xx"): check.py fails on the copy, so the criterion passes (exit 0).
- `grep -q "'recurring finding'" scripts/check.py`: exit 0.
- `scripts/check.sh`: exit 0. The selftests, shellcheck, and plugin validate all passed.
- `git diff --quiet HEAD -- scripts/run.sh`: exit 0.

## Notes
The Commands section's `check.sh` line in CLAUDE.md does not list the plan-defect guards, so I left it as is and updated the Decisions line that does name check.py's guard. The author agent file (`.claude/agents/sdlc-lite-author.md`) already covers the recurring finding and check.py; I made no change to it this step. The other files in the diff were changed before this step, not by me.
