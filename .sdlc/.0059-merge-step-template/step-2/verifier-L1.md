<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Blocks differ, so check.py fails: pass. I ran the criterion's setup in a temp copy with the `merge-base --is-ancestor` substitution in `handoff-format/SKILL.md`. check.py printed `FAIL merge-step block differs between agents/planner.md and skills/handoff-format/SKILL.md` and exited 1. The `!` therefore exits 0.
- Identical blocks that no longer parse: pass. I applied the `wc -w)` to `wc -w` substitution to both files in a temp copy. check.py printed `FAIL merge-step block fails steps.py lint: ... acceptance criterion command does not parse ...` with the lint's stderr included, and exited 1. The blocks were identical, so only the lint check fired.
- `git merge --no-ff` removed from `builder.md`: pass. In a temp copy, check.py printed `FAIL agents/builder.md: missing "git merge --no-ff"` and exited 1.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` exits 0 on the real tree: pass. It printed `ok: 18 role levels, 8 agents checked` and `rc=0`.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (guard): pass. It exited 0, and the tail shows the order and run selftests passing plus `ok: shellcheck` and `ok: plugin validate`.
- Spec items (code inspection, `git diff` of `check.py`): pass.
  - The module docstring has a line 6.
  - The check extracts the block between the exact line ```` ```merge-step ```` and the next exact line ```` ``` ````.
  - It fails on a missing, empty or differing block.
  - It replaces `<n>` with `1`, writes `planner-L2.md` in a temp dir, and runs `steps.py lint`, including stderr in the error.
  - It removes the temp dir in a `finally`.
  - All errors go into `errors` and use the existing `FAIL` output.

## Out of scope changes
- `agents/builder.md`, `agents/planner.md` and `skills/handoff-format/SKILL.md` show as modified, along with `.sdlc/0059-merge-step-template/handoff.md`. These are most likely step 1's work (the template) and are not part of step 2's edit to `check.py`. The `.sdlc` artifacts are untracked task files.

## For the next attempt
None
