<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `test -z "$(grep -L 'red guard' CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/skills/chain/SKILL.md)"`: pass. Evidence: exit 0 in the current tree. At HEAD, `grep -c 'red guard'` returned 0 for all three files, so the check goes red before the change.
- `grep 'A plan defect goes to a replan' CLAUDE.md | grep -q 'red guard'`: pass. Evidence: exit 0. The diff adds "A red guard in `steps.py split --only N` ... is a plan defect too" to that paragraph. The phrase was absent at HEAD.
- `grep '^2\. builder Status blocked' plugins/sdlc-lite/skills/chain/SKILL.md | grep -q 'red guard'`: pass. Evidence: exit 0. The diff adds the `--only N` guard run and the red guard refusal, handled like the section 3 split refusal, to that line.
- `grep -q "'red guard'" plugins/sdlc-lite/scripts/check.py`: pass. Evidence: exit 0. The diff adds `'red guard': ('skills/chain/SKILL.md', 'scripts/steps.py')` to `PLAN_DEFECT_DOCS`. The phrase was absent at HEAD.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: exit 0, last line "steps selftest: PASS".
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: exit 0. The tail shows the order, fanout, run and hook selftests, shellcheck and plugin validate all passing.

The step's "Do" items are also covered:
- The CLAUDE.md Layout bullet and Systems line are updated.
- The sdlc-lite-author.md plan-defect route bullet names the red guard.
- The chain section 3 text notes that the full split executes nothing.
- The existing `plan defect`, `Plan review` and `no new findings` phrases are intact.

## Out of scope changes
- `plugins/sdlc-lite/scripts/steps.py` (+165/-19) is step 1 work, not part of step 2. `check.py` guards `'red guard'` in `steps.py`, and the phrase is present there (7 occurrences).
- `.sdlc/criteria-that-contradict-each-other/handoff.md` is modified and `planner-L2.md`, `runs.jsonl` and `step-1/` are untracked. These are task bookkeeping.

## For the next attempt
None
