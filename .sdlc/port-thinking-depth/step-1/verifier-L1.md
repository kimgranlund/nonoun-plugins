<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- level-rubric "Bump one level" line contains `recurring finding`: pass. Evidence: the grep exited 0. The `git diff` shows the sentence added on the same line, so the grep would have failed at HEAD.
- chain step 4 item contains `recurring finding`: pass. Evidence: `grep -qE '^4\. .*recurring finding' skills/chain/SKILL.md` exited 0. Item 4 now checks for a recurring finding before "a second fail bumps". Item 2 covers a replanned step whose builder blocks again on the same finding.
- planner has a numbered line containing `recurring finding`: pass. Evidence: the grep exited 0. It matches new rule 6 in `agents/planner.md`. The `merge-step` block is not in the diff.
- conductor `- Levels follow` line contains `recurring finding`: pass. Evidence: the grep exited 0.
- handoff-format contains `recurring finding`: pass. Evidence: the grep exited 0, at the `## Plan review` description.
- repo-root `CLAUDE.md` contains `recurring finding`: pass. Evidence: the grep exited 0. `.claude/agents/sdlc-lite-author.md` also gained its clause.
- The four named files agree: pass. Evidence: I read the diffs.
  - All four send a recurring finding to a planner L3 replan, never a bump, and never count it toward a bump. Level-rubric, chain, and conductor say so; planner rule 6 does not restate it.
  - Level-rubric and chain both say the test fires only on a recurrence (same criterion and same root cause after an addressing rebuild or replan). Conductor and planner rule 6 say the same in shorter form.
  - Planner rule 6 requires a concrete change and rules out commentary-only replans.
  - The existing `plan defect:` sentences are unchanged in the diff.
- (guard) `git diff --quiet HEAD -- scripts/run.sh`: pass. Evidence: exit 0.
- (guard) no table row changes: pass. Evidence: `! git diff HEAD -- skills/level-rubric/SKILL.md ../../CLAUDE.md | grep -qE '^[-+]\|'` exited 0.
- (guard) `scripts/check.sh` exits 0: pass. Evidence: `check=0`. The output ends with the fanout, run, and hook selftests passing, then shellcheck and plugin validate.

## Out of scope changes
None. The modified files are the seven the step named. The untracked `.sdlc/port-thinking-depth/` files are pipeline artifacts.

## For the next attempt
None
