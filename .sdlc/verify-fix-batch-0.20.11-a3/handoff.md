## Task goal
Re-verify only the criterion that failed in .sdlc/verify-fix-batch-0.20.11-a2/verifier-L3.md (T-0294 dependents of the changed `review_required` contract). Fix commit 2cd5342 on this branch (earlier 832bb36). User decision: plan review runs only for a plan with an L4 or L5 step. The fix chose the "strict" option: lean stays strict in both lane and lint (`lean_only_reasons` in plugins/sdlc-lite/scripts/steps.py is read by `lane_action` and `lean_warnings`), the merge, replan, and `## Plan review` quiet cases are back in the lint selftest, agents/planner.md lists the lean plan conditions again, a Merge-title case was added to the lane selftest, and docs/references/sdlc-internals.md (review and lane sentences) now states the rule.

## Step 1: Re-verify the failed criterion
level: L3

### Do
- Lint-clean three-step planner-L2 fixtures (plain, Merge title, replan, `## Plan review` line, planner L3 file, an L4 step): `steps.py lint` warnings must match what `lane` calls lean-eligible (only the plain plan warns); `steps.py review` prints `split` for all but the L4 plan; `lane` prints `full` with the matching reason for Merge, replan, `## Plan review`, and planner L3. Then check every dependent text agrees with that code and with itself: steps.py usage text (lint, review, lane docstring sections and the `--help` epilog), skills/chain/SKILL.md, docs/lean-sdlc/design.md, skills/level-rubric/SKILL.md, skills/handoff-format/SKILL.md, agents/planner.md, agents/conductor.md, docs/references/sdlc-internals.md. Cite file:line for each.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- Fixtures behave as above; no dependent text contradicts the code.
