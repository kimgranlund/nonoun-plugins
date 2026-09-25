<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0063: Prove the merge-step template with a live run on a throwaway repo

## PR body
### Summary
T-0059 added the `merge-step` template, but only static checks covered it. For this ticket, a real merge step ran through `run.sh` on a throwaway repo (`/tmp/t0063-merge`). The builder made exactly one two-parent merge commit, and the verifier's merge-step criteria all passed. The plugin is unchanged. The run's artifacts are copied into `.sdlc/run-a-live-merge-step/step-1/`.

### Changes
- `step-1/handoff.md`: the merge step, written directly as a step handoff. There is no planner file in the task folder.
- `step-1/builder-L2.md` (Opus low): the builder ran `git merge --no-ff feature` on main and got conflicts in `greet.sh` and `test.sh`.
  - In `greet.sh` it kept the `-l` loud branch from main and the `World` default from feature.
  - In `test.sh` it kept both the loud check and the default check.
  - It committed the merge and pushed nothing.
- `step-1/verifier-L1.md` (Sonnet medium): verdict pass.
- `step-1/throwaway-graph.txt` and `step-1/runs.jsonl`: the commit graph and run records from the live run.

### Verification
Every item below passed in the verifier's report:
- **Two parents:** `rev-list --parents` word count is 3. Merge commit 528e6ed has parents 655daaf (main) and 7fcd8a8 (feature).
- **Branch is an ancestor:** `git merge-base --is-ancestor feature HEAD` exited 0.
- **No MERGE_HEAD:** the guard exited 0.
- **No conflict markers:** the guard exited 0. It was not vacuous, because the merge diff listed `greet.sh` and `test.sh`, so it scanned real files.
- **No new findings versus HEAD^1:** in a HEAD^1 worktree, `sh test.sh` printed ok and ok-loud. HEAD printed ok, ok-loud and ok-default, and both exited 0.
- **The new check can fail:** the default check asserts the exact string `Hello, World`, and the first parent's `greet.sh` has no `World` default.
- **Behavior:** `sh greet.sh` printed `Hello, World`, `sh greet.sh Ann` printed `Hello, Ann`, and `sh greet.sh -l Bo` printed `HELLO, Bo!`.
- **No out-of-scope changes:** `git status` showed only the untracked `.sdlc/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Verified the `merge-step` template live: a builder run through `run.sh` on a throwaway repo resolved conflicts and made exactly one two-parent merge commit, and the verifier's merge-step criteria all passed (T-0063).

## Follow-ups
None
