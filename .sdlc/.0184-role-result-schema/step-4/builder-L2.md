<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/check.py: added docstring item 13 and two guards. The first checks that each agent body holds its result-schema sections in the declared order. The second fails if run.sh or steps.py holds a copy of the schema. Each guard has an inline negative control.

## Checks
- AC1 (builder body with `## Changes` and `## Checks` swapped): rc 1, and the output had `FAIL agents/builder.md: result schema`. Passed.
- AC2 (run.sh with `# allowed='x'` appended): rc 1, and the output had `FAIL scripts/run.sh: holds a copy of the result schema`. Passed.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: `ok: 19 role levels, 9 agents checked`, exit 0.
- (guard) Scope diff against `$SDLC_BASE_SHA`: no files outside the allowed list, exit 0.

## Notes
None
