<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -F "run.sh" CLAUDE.md | grep -qF ".nvmrc"`: pass. Evidence: this prints `c1=0` in the working tree. In a throwaway worktree at HEAD it prints `head_c1=1`, so the check does go red without the change. The new sentence is at CLAUDE.md:22 and covers each point the handoff lists: after the git preflight, the toplevel `.nvmrc`, `$NVM_DIR` (else `~/.nvm`) `versions/node`, exact or highest numeric prefix, prepend `bin` or leave PATH unchanged with one stderr line for a missing version or an alias, never sources nvm, and `SDLC_DRY_RUN=1`. I checked each claim against the code in plugins/sdlc-lite/scripts/run.sh. The NVM_DIR default is at :56 and the no-match stderr line is at :85, followed by the alias stderr line. The prepend is at :82-83, and the ordering is covered by the "after the preflight" comment at :17.
- `head -8 plugins/sdlc-lite/scripts/run-selftest.sh | grep -qiF "nvmrc"`: pass. Evidence: this prints `c2=0` in the working tree and `head_c2=1` at HEAD. The nvmrc cases are named in the comment at run-selftest.sh:5-7. That text came from step 1's uncommitted diff, which the builder report also says; it is part of the working tree under review.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: `exit=0`, and the output includes `run selftest: PASS`, `steps selftest: PASS`, `fanout selftest: PASS`, `hook selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`. A guard only has to be green.
- Commands bullet and sdlc-lite-author.md left unchanged: pass. Evidence: the Commands bullet only lists "the ... run selftests" and says nothing about their scope. `.claude/agents/sdlc-lite-author.md` mentions run.sh only at :12, :13 and :31, and none of those lines describe Node or PATH behavior.

## Out of scope changes
None. Only CLAUDE.md changed in this step. The diffs in `plugins/sdlc-lite/scripts/run.sh`, `run-selftest.sh` and `.sdlc/run-honors-nvmrc/handoff.md` come from step 1 and the task's clarify pass.

## For the next attempt
None
