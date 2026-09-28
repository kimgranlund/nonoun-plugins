<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -q 'hooks/block-stray-worktree.sh' CLAUDE.md`: pass. Evidence: the command gives rc=0. It bites: `git show HEAD:CLAUDE.md | grep -c -e block-stray-worktree -e '--orphan'` finds 0 matches at HEAD. The new Layout bullet sits right after the block-pattern-kill bullet. It states what the hook denies and allows, that it fails closed, that fanout.py's worktrees are untouched, and that run.sh's EXIT cleanup stays. The Commands "Check everything" hook-selftest list now names block-stray-worktree.sh (`git diff` of CLAUDE.md).
- `grep -q block-stray-worktree .claude/agents/sdlc-lite-author.md`: pass. Evidence: rc=0, and 0 matches at HEAD. The diff adds the hook to the check.sh hook-selftest list and adds a hazard bullet directly after the pattern-kill entry.
- `grep -q -- '--orphan' plugins/sdlc-lite/agents/builder.md`: pass. Evidence: rc=0, and 0 matches at HEAD. Rule 5 gains one sentence, "A hook denies `-b`, `-B`, `--orphan`, and any path outside the prefix." The rest of the rule's wording is unchanged (`git diff`).
- `grep -q -- '--orphan' plugins/sdlc-lite/agents/verifier.md`: pass. Evidence: rc=0, and 0 matches at HEAD. Rule 3 gains the same single sentence and nothing else changes.
- `! git diff HEAD -- <4 files> | grep -q '^+.*—'`: pass. Evidence: rc=0. It bites: `printf '+foo — bar\n' | grep -q '^+.*—'` gives rc=0, so a planted added em-dash line matches and would make the negated check go red. The diff contains no such line.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I captured the exit code: rc=0. The tail of the output reads "run selftest: PASS", "hook selftest: PASS", "hook live probe selftest: PASS", "ok: shellcheck", "ok: plugin validate", and I found no FAIL lines. This confirms the builder's claim, which had no captured exit code.

## Out of scope changes
Other modified files are `plugins/sdlc-lite/hooks/block-stray-worktree.sh` (new), `hooks/hooks.json`, `scripts/check.sh`, `scripts/hook-selftest.sh`, and the task `handoff.md`. None of them belongs to step 2, and none needs action here:
- The four plugin files are all named in `step-1/handoff.md`, which I checked with grep. `step-1/verifier-L2.md` has the Verdict `pass`. So these are step 1's uncommitted work, not this builder's.
- The task `handoff.md` change is conductor or planner bookkeeping, 11 lines added and 2 removed (`git diff --stat`).

This builder's own diff touches only the four files the step names.

## For the next attempt
None
