<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- greet.sh: resolved the conflict. The `-l` loud branch from main stays, and the name now defaults to `World` as on feature.
- test.sh: resolved the conflict by keeping both the loud check and the default check.
- Merge commit created on main with `git merge --no-ff feature`.

## Checks
- `git merge --no-ff feature`: conflicts in greet.sh and test.sh. Both are resolved and the merge is committed.
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`: pass
- `git merge-base --is-ancestor feature HEAD`: pass
- `! git rev-parse -q --verify MERGE_HEAD`: pass
- Conflict-marker guard (the `git diff ... | xargs ... git grep` command): pass, no markers found.
- `sh test.sh` at HEAD: prints ok, ok-loud, ok-default and exits 0.
- `sh test.sh` in a HEAD^1 worktree: prints ok, ok-loud and exits 0. HEAD has no new findings compared with it.

## Notes
The first parent's test.sh had no default check, so the baseline has no ok-default. The temporary worktree at /tmp/t63p1 has been removed. Nothing was pushed.
