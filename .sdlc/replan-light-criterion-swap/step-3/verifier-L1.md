<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -q "can go red" plugins/sdlc-lite/agents/planner.md`: pass. Evidence: ran it, exit 0.
- `grep -q "membership or structure" plugins/sdlc-lite/agents/planner.md`: pass. Evidence: ran it, exit 0.
- `grep -q "membership or structure" CLAUDE.md`: pass. Evidence: ran it, exit 0. The diff shows the extended plan-defect Decisions sentence: "sees each `(guard)` red first (un-negated, or on a fixture) so it is a check that can go red, checks files other lanes change by membership or structure".
- `grep -q "can go red" plugins/sdlc-lite/scripts/check.py`: pass. Evidence: ran it, exit 0. The diff shows the `PLAN_DEFECT_DOCS` entry and the docstring item 5 naming it.
- `grep -q "membership or structure" plugins/sdlc-lite/scripts/check.py`: pass. Evidence: ran it, exit 0. Same diff hunks as the previous criterion.
- Negative control (mktemp copy with "can go red" replaced by `xx`, check.py must report the missing phrase): pass. Evidence: the grep exited 0, and check.py on the mutated copy printed `FAIL agents/planner.md: plan-defect route missing "can go red"`. The guard therefore goes red when the phrase is absent, and the unmutated tree is green (see the `check.py` guard below).
- Rules 11 and 12 exist (`grep -cE "^1[12]\. "` equals 2): pass. Evidence: `test` exit 0.
- (guard) Rule 10 keeps its number: pass. Evidence: grep exit 0. The section lists rules 1 to 12 in order, with no gaps.
- Observable (rules numbered 1 to 12, rules 9 and 10 unchanged): pass. Evidence: `git diff` on planner.md shows only two added lines after rule 10, and no `-` lines. The numbering listing runs 1 to 12.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: printed `ok: 18 role levels, 8 agents checked`, exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0. The tail shows the order, fanout, run, hook, and hook live probe selftests all PASS, plus shellcheck and plugin validate ok.

Steelman: I drafted a fail on the grounds that the check.py, CLAUDE.md and other diffs also hold swap-related hunks. The builder's rebuttal would hold. Those hunks belong to earlier steps of this task (the builder's Notes say so, and the swap lines are outside step 3's scope), so I dropped the finding.

## Out of scope changes
None from this step. The tree also holds other modified files from earlier steps: steps.py, verifier.md, conductor.md, the chain, handoff-format and level-rubric skills, sdlc-lite-author.md, and the swap-related hunks in check.py and CLAUDE.md. `git status` lists them, and they match earlier plan steps (the swap route), not step 3's Do.

## For the next attempt
None
