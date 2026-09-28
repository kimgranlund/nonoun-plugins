<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/agents/verifier.md`: pass. Evidence: exit 0. At HEAD the file has 0 matches, so the check can go red. The diff adds it to rule 3 and to the "throwaway worktree at HEAD" paragraph.
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/agents/builder.md`: pass. Evidence: exit 0. HEAD has 0 matches. The diff adds rule 5, which limits throwaway worktrees to `$SDLC_TMP_WORKTREES` and says never `/tmp` or a sibling dir.
- `! grep -q 'git worktree add <tmp dir> HEAD' plugins/sdlc-lite/agents/verifier.md`: pass. Evidence: I ran it as `test -f <file> && ! grep ...`, exit 0. HEAD has 1 match of the old phrase, so the check can go red.
- `grep -q SDLC_TMP_WORKTREES CLAUDE.md`: pass. Evidence: exit 0. HEAD has 0 matches. The diff adds the sentence to the `scripts/run.sh` Layout bullet, and it matches the required wording.
- `grep -q SDLC_TMP_WORKTREES .claude/agents/sdlc-lite-author.md`: pass. Evidence: exit 0. HEAD has 0 matches. The diff adds the line right after the "throwaway worktrees" invariant.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: rc=0. The tail shows the order, fanout, run, hook and hook live probe selftests PASS, plus `ok: shellcheck` and `ok: plugin validate`. My grep for "fail" only matched "ok:" lines that describe failure cases.

## Out of scope changes
`plugins/sdlc-lite/scripts/run.sh` and `plugins/sdlc-lite/scripts/run-selftest.sh` also show as modified. These are not step 2 files. The step's Do list names only the two agent files, `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`. They match step 1's work, which exports `SDLC_TMP_WORKTREES` and cleans up. Step 2's text describes that behavior, and `check.sh` passes with them, so I am treating them as step 1's uncommitted work and not a step 2 defect.

The `merge-step` template is unchanged, as the step required. `check.sh` passes.

## For the next attempt
None
