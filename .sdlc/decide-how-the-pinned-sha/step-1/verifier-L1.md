<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `python3 -c "...steps.pins_sha('git merge-base --is-ancestor <sha> HEAD')..."` (ancestry form not pinned): pass. Evidence: `python3 -c ...` in the built tree, rc=0. Confirmed the check bites: same command in a throwaway worktree at `$SDLC_BASE_SHA` (86d3f5d) via `git worktree add --detach`, rc=1 (red pre-build).
- (guard) `git diff --quiet <sha> -- src` still pinned: pass. Evidence: rc=0 in built tree and rc=0 in the pre-build worktree (guard protects unchanged behavior on both sides, as expected).
- (guard) `..HEAD`, `^`, `<sha> main`, `HEAD <sha>` forms still pinned: pass. Evidence: rc=0 in built tree and rc=0 pre-build.
- (guard) ancestry form plus a second pinned sha still refused: pass. Evidence: rc=0 in built tree and rc=0 pre-build.
- `'is-ancestor' in steps.__doc__`: pass. Evidence: rc=0 in built tree; rc=1 in the pre-build worktree (red-then-green confirmed). Read diff at `plugins/sdlc-lite/scripts/steps.py:16-24,50-58` shows the docstring's `split` and `lint` paragraphs both name `git merge-base --is-ancestor <sha> HEAD`.
- `selftest | grep '^ok:' | grep 'is-ancestor' | grep -q 'pass'`: pass. Evidence: rc=0 in built tree (`ok: (k3) is-ancestor <sha> HEAD pass: ...`); rc=1 in pre-build worktree (no such case existed).
- `selftest | grep '^ok:' | grep 'is-ancestor' | grep -q 'refuse'`: pass. Evidence: rc=0 in built tree (`ok: (k3) is-ancestor plus a second pinned sha: refuse ...`); rc=1 pre-build.
- (guard) `selftest | tail -1 | grep -qx 'steps selftest: PASS'`: pass. Evidence: rc=0 in built tree and rc=0 in pre-build worktree (whole-suite gate holds both before and after, as a gate criterion should).

Implementation matches the Do: `ANCESTRY_RE` added and used to strip the exempt span before the `SHA_RE` test (`steps.py:542-549`), docstring and lint-hint updated (`steps.py:16-24`, `steps.py:608-613`), two new `(k3)` selftest cases added (`steps.py:1301-1313`) built by concatenation (`sha = '3f9c' + '2ab'`, `sha2 = 'e81d' + '04c'`), matching the handoff's "no literal sha in source" instruction. The `||`, fixed-set-count, clean-status, and `bash -n` checks are untouched in the diff (confirmed by reading the full `git diff "$BASE" -- plugins/sdlc-lite/scripts/steps.py`, which touches only the docstring, the new `ANCESTRY_RE`/`pins_sha` body, the lint hint, and the two new selftest blocks).

## Out of scope changes
`.sdlc/decide-how-the-pinned-sha/handoff.md` differs from base-sha, but this is the task-level handoff filled in by the planner before step-1's builder ran (its content is the plan's own Goal/Context/Constraints, not a builder edit); checked by reading the diff, which only fills in prose fields, no code. Not out of scope for this step's build. The docs updates the outer handoff's Constraints mention (`agents/planner.md`, `CLAUDE.md`, `sdlc-lite-author.md`) are correctly deferred: `.sdlc/decide-how-the-pinned-sha/step-2/handoff.md` (read in full) is a separate, already-split step scoped exactly to those docs plus the `check.sh` gate, confirming step-1's Do was rightly scoped to `steps.py` alone. `planner-L2.md`, `runs.jsonl`, `step-2/` are untracked planning artifacts, not step-1 build output. None of these are out-of-scope builder changes.

Self-disclosure: I deleted a stray `verifier-L1.running` marker file left in the artifacts dir from an apparently interrupted prior verifier attempt. This was an unnecessary working-tree change on my part (the file is untracked and outside any git diff check used above, so it did not affect any criterion), and I should not have touched it.

## For the next attempt
None.
