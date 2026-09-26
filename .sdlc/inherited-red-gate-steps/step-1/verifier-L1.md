<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF 'gates green' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: exit 0. The diff adds rule 14 at planner.md, right after rule 13.
- `grep -qF 'gates green' CLAUDE.md`: pass. Evidence: exit 0. The diff adds the clause "The planner puts whole-suite gate guards on one final `gates green` step, never on every step (check.py guards the phrase)".
- `grep -qF "'gates green'" plugins/sdlc-lite/scripts/check.py`: pass. Evidence: exit 0. The diff adds `'gates green': ('agents/planner.md',)` to `PLAN_DEFECT_DOCS`.
- Negative control (copy the plugin to a temp dir, strip the phrase from planner.md, run check.py there and grep for `gates green`): pass. Evidence: check.py printed `FAIL agents/planner.md: plan-defect route missing "gates green"`, then `FAIL: 18 role levels, 8 agents checked`, and the grep exited 0. The check can go red: on the stripped copy the check reports a failure, and on the real tree it prints only `ok`, which has no `gates green`, so the grep would fail there.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: printed `ok: 18 role levels, 8 agents checked`, exit 0.
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: exit 0. `git diff` shows no change to handoff-format, and the merge-step block in planner.md is untouched.

## Out of scope changes
None. `git diff` touches only CLAUDE.md, planner.md, and check.py, all named in the step. The untracked `.sdlc` files are task artifacts.

## For the next attempt
None
