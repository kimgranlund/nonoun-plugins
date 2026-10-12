<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/evals/01-bare-goal.expected.md`: line 10 rewritten.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/evals/02-wrong-unit.expected.md`: line 10 rewritten.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/evals/03-conflicting-ask.expected.md`: line 10 rewritten.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/evals/04-unattended-gap.expected.md`: line 10 rewritten.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/evals/05-multi-step.expected.md`: line 10 rewritten.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/evals/06-bad-done-when.expected.md`: line 10 rewritten.

## Checks
- The `(red)` loop (grep on the new `Level:` shape plus `plan_check.py clarify --file` per file) ran on all six files and printed no failures.
- The `(guard)` command (`git diff --name-only` filtered by `grep -vE`) printed nothing, so it holds.

## Notes
- The red checkpoint was recorded as retrospective, not red-before-edit. `redck.py` found 21 source paths already differing from base, because the earlier steps' edits are in the tree. I did not take a pre-edit record for this reason.
- Level numbers are unchanged. The old lane word `chain` is now `full` in files 02 and 05.
- Reversibility text is unchanged, apart from the new `yes`/`no` prefix. File 05 was "reversible until a plan names a push", so I wrote `no, a plan may name a push`.
- I set `cost:` to the old low/medium/high word plus the old level reason (for example "low, a few text edits and one guard").
