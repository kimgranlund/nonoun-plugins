<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/verifier.md: rule 3 now creates the throwaway worktree only under `$SDLC_TMP_WORKTREES` (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`). It says run.sh removes that prefix on exit, tells the verifier to still remove its own worktree, and resolves the merge-step `<tmp>` to a path under the prefix. The later "throwaway worktree at HEAD" now points to the same place.
- plugins/sdlc-lite/agents/builder.md: new rule 5 says throwaway worktrees go only under `$SDLC_TMP_WORKTREES`, never `/tmp` or a sibling dir.
- CLAUDE.md: added the `SDLC_TMP_WORKTREES` export, cleanup, and prune sentence to the `scripts/run.sh` Layout bullet.
- .claude/agents/sdlc-lite-author.md: added the matching invariant line right after the "throwaway worktrees" line.

## Checks
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/agents/verifier.md`: OK
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/agents/builder.md`: OK
- `! grep -q 'git worktree add <tmp dir> HEAD' plugins/sdlc-lite/agents/verifier.md`: OK
- `grep -q SDLC_TMP_WORKTREES CLAUDE.md`: OK
- `grep -q SDLC_TMP_WORKTREES .claude/agents/sdlc-lite-author.md`: OK
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (selftests, hook selftests, shellcheck, and plugin validate all passed)

## Notes
I left the merge-step template's `<tmp>` placeholder and `skills/checks-that-bite` unchanged, as the handoff said to.
