<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `docs/references/sdlc-internals.md`: I took HEAD's `fanout.py` paragraph, which covers run ids, the integration-dirty refusal and per-run log prefixes. I added the runner lane's sentence on the reap step, placed after the driver and before the lane commit.
- `plugins/sdlc-lite/scripts/fanout.py`: `run_ticket` keeps HEAD's `say(ctx, ...)` and `run_logged` driver call, followed by the runner lane's `reap-tmp-worktrees.sh` call. The selftest keeps HEAD's cases 9 (resume) and 10 (gate retry) and adds the runner lane's reap case, renumbered to 11.
- Merge commit created on `fanout/night-2026-09-29` (parents `6139f73` and `fanout/night-2026-09-29-runner`). Nothing was pushed.

## Checks
- `git merge --no-ff fanout/night-2026-09-29-runner`: conflicts in the two files above. I resolved both, and a grep found no conflict markers left.
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS
- `git diff --check --cached`: clean
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`: OK
- `git merge-base --is-ancestor fanout/night-2026-09-29-runner HEAD`: OK
- `! git rev-parse -q --verify MERGE_HEAD`: OK
- diff-tree `--cc` conflict-marker guard: OK
- `bash plugins/sdlc-lite/scripts/check.sh` at HEAD: rc=0, with 34 lines matching `fail|error`.
- The same command in a detached worktree at `HEAD^1` (`$SDLC_TMP_WORKTREES/base`): rc=0, also 34 matching lines. I found no new findings. The worktree has been removed.

## Notes
- `check.sh` skips shellcheck in both runs because it is not installed.
- The merge commit message still contains git's default `# Conflicts:` comment lines.
- I saved the gate outputs to `/tmp/claude-head-check.txt` and `/tmp/claude-base-check.txt`. I compared them by exit code and the count of `fail|error` lines, not with a full diff.
