<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0085: Recurring-finding rule: a repeated finding goes to a planner L3 replan, not a level bump

## PR body
### Summary
This adds a recurring-finding rule to sdlc-lite's escalation doctrine. A recurring finding is a verifier fail, or a builder block, that repeats an earlier attempt's finding on the same step: same criterion, same root cause, even after a rebuild or replan addressed it. When that happens, the chain treats it as a sign that the plan or a rule is wrong, not the last attempt. It sends the step to a planner L3 replan, the same path a `plan defect:` takes. It never bumps the level and never counts toward a bump. The replan must produce a real change: a rewritten criterion or step, or a changed Do that states why the rule holds. A replan that only adds commentary is not allowed. Ordinary fails are unaffected, because the test fires only on a recurrence.

No level, model, or effort table changed, and the `plan defect:` tag works as before.

### Changes
Step 1: state the rule in the docs
- `skills/level-rubric/SKILL.md`: the "Bump one level" line now routes a recurring finding to a planner L3 replan. It adds no bump, does not count toward one, and fires only on a recurrence.
- `skills/chain/SKILL.md`, step 4:
  - Item 4 now checks whether a second fail is a recurring finding before bumping.
  - If it is, /chain adds a `recurring finding:` entry to the task handoff's `## Plan review` and takes the 4.2 replan path.
  - Item 2 treats a replanned step whose builder blocks again on the same finding as a recurring finding.
- `agents/planner.md`: new rule 6 under "Criteria that can pass". When `## Plan review` holds a `recurring finding:` entry, the planner first asks whether the criterion, the step, or a rule is wrong, and must land a concrete change.
- `agents/conductor.md`: the `- Levels follow` escalation line says a recurring finding means a planner L3 replan that questions the plan or rule, never a level bump.
- Other records updated in the same change so they don't go stale: `skills/handoff-format/SKILL.md` (`## Plan review` description), repo-root `CLAUDE.md` (plan-defect decision bullet), `.claude/agents/sdlc-lite-author.md` (plan-defect route bullet).

Step 2: guard the rule in check.py
- `scripts/check.py`: new `'recurring finding'` key in `PLAN_DEFECT_DOCS`. It covers planner.md, conductor.md, chain, level-rubric, and handoff-format. Docstring item 5 now names the rule.
- Repo-root `CLAUDE.md`: the Decisions line now says check.py guards both the `plan defect` tag and the `recurring finding` rule.

### Verification
Step 1 (verifier L1: pass)
- Six greps confirm the phrase sits on the right lines in level-rubric, chain item 4, planner (a numbered rule), conductor, handoff-format, and `CLAUDE.md`. The diff shows the level-rubric grep would have failed at HEAD.
- The verifier read the four named files and found they agree on:
  - the route (planner L3 replan, no bump)
  - the trigger (recurrence only)
  - the concrete-change requirement
- The existing `plan defect:` sentences are unchanged.
- Guards passed:
  - `run.sh` unchanged
  - no table rows changed in level-rubric or `CLAUDE.md`
  - `scripts/check.sh` exits 0

Step 2 (verifier L1: pass)
- Negative control: the verifier renamed "recurring finding" in a temp copy of conductor.md. check.py then failed with `plan-defect route missing "recurring finding"`. The unmutated copy passed.
- `grep` finds the new key in check.py.
- `scripts/check.sh` exits 0, and `run.sh` is unchanged.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Escalation: a recurring finding now goes to a planner L3 replan, not a level bump, and does not count toward a bump. A recurring finding is a fail or block that repeats an earlier attempt's criterion and root cause after that finding was addressed. The replan must change a criterion, a step, or a rule. `check.py` checks that the rule appears in the planner, conductor, chain, level-rubric, and handoff-format docs. (T-0085)

## Follow-ups
None
