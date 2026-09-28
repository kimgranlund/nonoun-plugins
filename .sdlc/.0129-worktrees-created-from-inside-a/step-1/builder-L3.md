<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: added the stray report. It takes a snapshot of worktree paths (porcelain) and `refs/heads` branches after the dry-run exit, next to `wt_tmp`. `detect_strays` runs once per run, is called in an `||` list so errexit is off, and never fails. It skips paths under this run's prefix, comparing by `phys` realpath and by raw path, and keeps each worktree's branch. `json_array` builds the arrays. runs.jsonl gets `stray_worktrees` and `stray_branches` through `jq --argjson`; both are always present and are empty arrays when nothing appeared. `report_strays` prints the stderr lines once, in `on_exit` after `cleanup_worktrees`, so it covers exit 0, 1, 3, INT, TERM and HUP. The header comment now describes the report, names both fields, and says "appeared during this run". I also added one `# shellcheck disable=SC2016` directive on the existing `sed 's|${CLAUDE_PLUGIN_ROOT}|...'` line. Without it, criterion 5 (plain `shellcheck` at the default severity) fails at base with an info-level SC2016.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: extended the header comment. `want_wt` now asserts that no `stray` line is printed. Added a third stub (`$tmp/sbin/claude`) and new cases:
  - stray ok run: a detached worktree outside the prefix, a worktree on branch `stray-wt-br`, branch `stray-br`, and a worktree under the prefix. It checks the exact stderr lines (` [stray-wt-br]` only on the branched one), that nothing under the prefix is reported, and the runs.jsonl arrays.
  - strayfail: exits 1 and still reports.
  - none and prefix-only: no `stray` line and empty arrays.
  - `stray_clean` removes the strays inside the temp repo after each stray case.

## Checks
- Criterion 1 (the inline stub-repo command): rc=0.
- Criterion 2 `grep -qF 'stray branch appeared during this run' ... && bash plugins/sdlc-lite/scripts/run-selftest.sh | grep -qx 'run selftest: PASS'`: rc=0.
- Criterion 3 `sed -n '/^set -euo/q;p' plugins/sdlc-lite/scripts/run.sh | grep -q 'stray_worktrees'`: rc=0.
- Criterion 4 `sed -n '/^set -euo/q;p' plugins/sdlc-lite/scripts/run-selftest.sh | grep -qi 'stray'`: rc=0.
- Criterion 5 `shellcheck plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`: rc=0.
- Base check: `git show HEAD:plugins/sdlc-lite/scripts/run.sh | shellcheck -` gave rc=1 (SC2016 info, line 146), which is why the directive was added.
- `plugins/sdlc-lite/scripts/check.sh`: rc=0 (every selftest PASS, `ok: shellcheck`, `ok: plugin validate`).

## Notes
- The strayfail selftest case caught a real bug in my first version: the last porcelain record was dropped because `$(...)` strips the trailing blank line. It went unnoticed on success runs because the prefix worktree happened to be listed last. The fix passes the input as `<<<"$now_wt"$'\n'`.
- The block-stray-worktree hook fails closed on any Bash text that has a `worktree add` next to a heredoc or a `bash` command word. So I wrote the selftest with the Edit tool, and a verifier has to run criterion 1 as its own Bash call, not in the same command as criterion 2.
- Temp dirs left behind under `/var/folders/.../T/`: `tmp.cV5zUPw2PM` (cleanup was denied by permissions), `tmp.Y1XBUhZfUS` (from a debug copy of the selftest) and the dirs from the two criterion-1 runs (the criterion itself never cleans up). All are mktemp dirs outside the repo. The repo's own worktree list and branches are unchanged.
- I did not touch CLAUDE.md, the author agent, or the hook docs. The ticket asks for them, but this step's Do does not, so I assume a later step (step-2 or step-3) covers them.
