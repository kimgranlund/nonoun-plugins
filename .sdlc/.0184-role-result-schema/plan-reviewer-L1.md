<!-- role=plan-reviewer level=L1 model=fable effort=high -->
## Verdict
replan

## Findings
- step 3: interfaces: `plugins/sdlc-lite/scripts/traces/selftest.py` is an unnamed contract dependent of `steps.next_action`, and the step's change turns its fixtures into `invalid result`. The case `results: on the same fixtures as step dirs, steps.next_action agrees` expects `verify`, `replan`, `inherited`, `rebuild`, `done` and `reverify`. Its builder fixture header has no `level=` token, so it fails the step 1 header regex, and its verifier fixture has no header at all. The step 3 scope guard does not allow that file, no step 3 criterion runs `traces.py selftest`, and step 7 limits fixes to files the earlier steps changed, so `check.sh` goes red with no step allowed to repair it. Evidence: `plugins/sdlc-lite/scripts/traces/selftest.py:340` (`head = '<!-- role=builder model=opus effort=high -->\n'`), `:345-347` (`_verifier_text` writes no header), `:385-409` (`got = steps.next_action(d)[0]; assert got == act`); `plugins/sdlc-lite/scripts/check.sh:23` (`traces.py selftest`); plan lines 36 (regex requires `level=(L[1-5])`), 153, 183 (allow-list has no `traces/` path), 277.
- step 1: acceptance criteria: the order criterion is impossible with the step's Do. Reason 8 is `## <B> comes before ## <A>` where declared-earlier A appears after B. For a verifier file with `## Criteria` then `## Verdict`, A is Verdict and B is Criteria, so the Do yields `## Criteria comes before ## Verdict`. The criterion greps for the exact line `## Verdict comes before ## Criteria`. The selftest also requires "their exact reason", so a builder cannot satisfy both. Step 4's example (`## Checks before ## Changes` for a body with those two swapped) follows the Do's direction, not the criterion's. Evidence: plan line 57 against plan line 84; plan line 196.

## Missing decisions
None
