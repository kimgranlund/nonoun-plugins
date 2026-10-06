## Task goal
Re-verify only the one criterion that failed in .sdlc/verify-fix-batch-0.20.11-a/verifier-L3.md: dependents of the changed `review_required` contract (T-0294). Fix commit 832bb36 on this branch (base before it 0e85edb). The user decision is that plan review runs only for a plan with an L4 or L5 step; the fix keeps the lean lane strict (a new `lean_only_reasons` in plugins/sdlc-lite/scripts/steps.py, so `steps.py lane` still refuses planner L3, a Merge step, a replan, and a `## Plan review` line for lean), drops the false claim that a merge step is L4 or higher, and updates skills/handoff-format/SKILL.md.

## Step 1: Re-verify the failed criterion
level: L3

### Do
- Rerun the earlier fixture (size M, planner-L3.md plus planner-L3-2.md, a `Merge x` step at L2, a `## Plan review` line): `steps.py lane` must print `full`, as at 3482207, and `steps.py review` must print `split`. Check that skills/chain/SKILL.md line about lean conditions, docs/lean-sdlc/design.md, the steps.py usage text (`--help` epilog and the lint and review docstring sections), skills/level-rubric/SKILL.md, and skills/handoff-format/SKILL.md agree with that behavior and none claims a merge step is L4 or higher.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- The fixture above gives lane `full` and review `split`; no dependent text contradicts the code (cite file:line for each).
