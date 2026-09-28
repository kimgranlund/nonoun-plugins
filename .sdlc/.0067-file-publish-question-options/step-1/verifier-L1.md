<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -q "at most 4 options" skills/file/SKILL.md`: pass. Evidence: exits 0 in the working tree. The phrase is on the step 4 line of the diff, and HEAD's SKILL.md lacks it (the guard reports it missing there).
- `grep -q "at most 4 options" scripts/check.py`: pass. Evidence: exits 0. The phrase appears in the new guard at check.py:168.
- `python3 scripts/check.py` exits 0, and exits 1 on the pre-fix SKILL.md: pass. Evidence: with the fix it prints `ok: 18 role levels, 8 agents checked` and exits 0. In a throwaway worktree at HEAD with the new check.py copied in, it prints two FAIL lines and exits 1: `FAIL skills/file/SKILL.md: publish question missing "at most 4 options"` and `FAIL skills/file/SKILL.md: step 4 lists GitHub issues among the publish options`. Both conjuncts of the guard fire on the old text.
- (guard) `block-publish.sh` and "Never publish on your own" are still in SKILL.md: pass. Evidence: the combined grep exits 0. The diff to step 4 leaves both, and the numbered-mode folder note, intact.
- (guard) `scripts/check.sh` shows no new findings versus HEAD: pass. Evidence: the working tree gives exit 0, and all selftests, shellcheck and plugin validate report ok. The HEAD worktree run (with the new guard applied) exits 1 with only the two new FAIL lines. Diffing the two outputs shows those lines as the only difference.

The SKILL text meets the step's wording. It says one multiSelect question with "at most 4 options" (commit, push, PR, changelog edit). The issues item is dropped from that list. Issues are offered in a separate second AskUserQuestion with at least 2 options.

## Out of scope changes
None. The diff touches only `plugins/sdlc-lite/scripts/check.py` and `plugins/sdlc-lite/skills/file/SKILL.md`. The untracked `.sdlc` files are task artifacts.

## For the next attempt
None
