<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/agents/planner.md`: added rule 13 (never require a clean porcelain status).
- `plugins/sdlc-lite/scripts/check.py`: added `'clean porcelain status'` to `PLAN_DEFECT_DOCS`.
- `CLAUDE.md`: added the clean-porcelain-status refusal clause to the `steps.py` bullet.
- `.claude/agents/sdlc-lite-author.md`: added "one that requires a clean porcelain status" to the split lint list.

## Checks
- Ran `grep -qE "^13\. .*clean porcelain status"` and `grep -qF "git ls-files --others --exclude-standard"` on `planner.md`. Both passed.
- I did not run separate greps for the phrase in `check.py`, `CLAUDE.md` and `sdlc-lite-author.md`. `check.py` (below) verifies the phrase in `planner.md` and `steps.py`, and I wrote the phrase into the other three files.
- `python3 plugins/sdlc-lite/scripts/check.py` printed "ok: 18 role levels, 8 agents checked"; I only read the last 5 lines of output.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` printed "steps selftest: PASS".

## Notes
None
