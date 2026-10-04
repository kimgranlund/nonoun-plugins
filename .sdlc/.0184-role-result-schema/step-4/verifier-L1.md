<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- AC1 (builder body with `## Changes` and `## Checks` swapped must be flagged): pass. Evidence: I ran the criterion on a copy of the plugin. rc=1, and the output had `FAIL agents/builder.md: result schema: ## Checks before ## Changes`. The check bites because the swap itself produces the red.
- AC2 (run.sh with `# allowed='x'` appended must be flagged): pass. Evidence: I ran the criterion on a copy of the plugin. rc=1, and the output had `FAIL scripts/run.sh: holds a copy of the result schema`.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: output `ok: 19 role levels, 9 agents checked`, rc=0.
- (guard) Scope diff against `$SDLC_BASE_SHA`: pass. Evidence: I ran the command and it exited 0.

## Out of scope changes
None. `git diff` of `check.py` shows two edits beyond the two new guards.
- **Docstring item 13:** the Do asked for it.
- **Rewritten plan-reviewer guard:** it now reads `results.SCHEMA` instead of the old `PR_SECT` line in `run.sh`. I judge this needed, not stray. The `run.sh` line it matched no longer exists, and the new copy guard forbids `sect=[A-Z]` there. The 19-role-levels run is green with it, and it carries three negative controls of its own.

The other modified files (`check.sh`, `fanout.py`, `run.sh`, `run-selftest.sh`, `steps.py`, `traces/selftest.py`) are all on the guard's allowed list. They belong to earlier steps.

## For the next attempt
None
