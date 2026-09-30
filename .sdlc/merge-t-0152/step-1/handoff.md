## Task goal
Lane branch `fanout/night-2026-09-29-fanout` (T-0152) is merged into the integration branch `fanout/night-2026-09-29` with both lanes' intent intact.

## Step 1: Merge fanout/night-2026-09-29-fanout
level: L3
### Do
Run `git merge --no-ff fanout/night-2026-09-29-fanout` on a tree with no uncommitted tracked changes. Resolve every conflict so both lanes' intent survives, run the gates below, and create the merge commit. Never push.
### Acceptance criteria
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`
- `git merge-base --is-ancestor fanout/night-2026-09-29-fanout HEAD`
- (guard) `! git rev-parse -q --verify MERGE_HEAD`
- (guard) `out=$(git diff-tree --cc HEAD) && ! printf "%s\n" "$out" | grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` shows no new findings versus the first parent: run the same command in a `git worktree add --detach <tmp> HEAD^1` copy and compare.
