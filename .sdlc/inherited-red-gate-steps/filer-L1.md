<!-- role=filer level=L1 model=sonnet effort=medium -->
Both steps passed verification with no plan defects. Ready to file.

## Warnings
None

## PR title
T-0124: Planner puts whole-suite gate guards on a final "gates green" step, not every step

## PR body
Summary: Fixes T-0124 so inherited red (from an earlier step or a main sync) never blocks a step whose own work is green. Previously the planner put whole-suite gate guards (full test suite, lint, typecheck, repo check) on every step, so red introduced upstream failed every later step even when that step's own work was fine.

Changes:
- `plugins/sdlc-lite/agents/planner.md`: added rule 14 under "Criteria that can pass" — whole-suite gate guards go on one final "gates green" step, never on every step. Earlier steps use file- or test-scoped checks; the final step's Do runs every gate and fixes any red the earlier steps introduced. A gate already red at build-start HEAD reports builder Status `inherited red: <tests>`. A one-step plan makes that step the gates-green step; a merge step keeps its own gate guards (merge-step block untouched).
- `plugins/sdlc-lite/scripts/check.py`: added `'gates green': ('agents/planner.md',)` to `PLAN_DEFECT_DOCS`, and extended docstring item 5 to name the rule, so check.py flags a planner.md missing the phrase.
- `CLAUDE.md`: added a clause to the "A plan defect goes to a replan" decision naming the gates-green rule and that check.py guards it.

Verified:
- Step 1 (builder L2 opus low, verifier L1 sonnet medium, pass): all three grep criteria pass; the negative-control fixture (plugin copied to a temp dir, phrase stripped from planner.md) makes check.py fail with `FAIL agents/planner.md: plan-defect route missing "gates green"`, proving the guard actually discriminates; `check.py` and the handoff-format diff guard both green on the real tree.
- Step 2 (builder L1 sonnet low, verifier L1 opus medium, pass): full `check.sh` and `check.py` both green on the built tree; verifier reran the negative-control fixture independently and got the same fail-then-pass result. No inherited red was present at build-start HEAD, so no fix-forward was needed.
- No out-of-scope changes: diff touches only `CLAUDE.md`, `agents/planner.md`, `scripts/check.py`, matching step 1's Do exactly.

## Changelog entry
Planner now places whole-suite gate guards (tests, lint, typecheck, repo check) on one final "gates green" step instead of on every step, so red inherited from an earlier step or a main sync no longer blocks a step whose own work is green.

## Follow-ups
- No code gate detects a full-suite guard placed on a non-final step; the planner-L2 handoff notes rule 14 lives only in the prompt and check.py only proves the phrase's presence, not that planners follow it — worth deciding whether a heuristic check (e.g. flag a non-final step whose guard command matches the project's declared whole-gate command) is worth building.
- The check.py negative-control fixture used by both steps relies on macOS `sed -i ''`; the planner-L2 handoff flags this as non-portable to GNU sed, which would make the criterion fail to run rather than fail correctly on other hosts.
