<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/planner.md: added rules 11 ("can go red": see each guard red first) and 12 ("membership or structure" for files other lanes also change) after rule 10. Rules 1 to 10 are unchanged.
- plugins/sdlc-lite/scripts/check.py: added `'can go red'` and `'membership or structure'` to `PLAN_DEFECT_DOCS` for agents/planner.md, and named both in item 5 of the docstring.
- CLAUDE.md: extended the plan-defect Decisions sentence. It now says the planner sees each `(guard)` red first (un-negated, or on a fixture) and checks files other lanes change by membership or structure.

## Checks
- `grep -q "can go red" plugins/sdlc-lite/agents/planner.md`: exit 0
- `grep -q "membership or structure" plugins/sdlc-lite/agents/planner.md`: exit 0
- `grep -q "membership or structure" CLAUDE.md`: exit 0
- `grep -q "can go red" plugins/sdlc-lite/scripts/check.py`: exit 0
- `grep -q "membership or structure" plugins/sdlc-lite/scripts/check.py`: exit 0
- Negative control (mktemp copy with "can go red" replaced by `xx`, then check.py grepped for the missing-phrase error): exit 0, so the guard bites.
- `test ... grep -cE "^1[12]\. " ... -eq 2`: exit 0
- (guard) rule 10 still numbered 10: exit 0
- Observable: the section's rules are numbered 1 to 12 with no gaps, and the diff only adds lines to planner.md, so rules 9 and 10 read as they do at HEAD.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 0, every section PASS/ok.

## Notes
`git diff --stat` also shows changes in steps.py, verifier.md, conductor.md, the chain, handoff-format and level-rubric skills, and sdlc-lite-author.md. Those came from earlier steps of this task and were already in the tree; this step did not touch them. I did not mirror the CLAUDE.md sentence into `.claude/agents/sdlc-lite-author.md` because the handoff did not ask for it. The planner may want to do that in a later step.
