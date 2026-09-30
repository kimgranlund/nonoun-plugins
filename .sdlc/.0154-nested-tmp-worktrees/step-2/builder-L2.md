<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: runs `bash <SCRIPTS>/reap-tmp-worktrees.sh <lane worktree>` right after the driver returns, ignoring its exit code. This happens before `inherited_red` and before any `git add -A` or wip commit. Module docstring step 2 now describes it. Added `REAP_STUB` and selftest case 10, `lane tmp prefix reaped`.
- `docs/maintenance/sdlc-internals.md`: the fanout paragraph gets one clause about the per-driver lane reap.

## Checks
- Red run: I disabled the reaper call by turning it into `if 0: subprocess.run(...)` and ran `python3 plugins/sdlc-lite/scripts/fanout.py selftest`. It exited 1:
  ```
  fanout selftest: FAIL, these did not hold:
    - lane tmp prefix reaped: /private/var/folders/.../rplanes/alpha/.worktrees/tmp/builder-24237 gone and unlisted, got exists=True rc=0 worktrees='... worktree /private/var/folders/.../rplanes/alpha/.worktrees/tmp/builder-24237/w\nHEAD 87f37eb...\ndetached ...'
  ```
- After restoring the call from a backup copy: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` printed `fanout selftest: PASS` (exit 0).
- `grep -qF reap-tmp-worktrees.sh plugins/sdlc-lite/scripts/fanout.py`: exit 0.
- `grep -qF "lane tmp prefix reaped" plugins/sdlc-lite/scripts/fanout.py`: exit 0.
- `git diff --check`: clean.

## Notes
- Case 10 gets its dead pid from a `true` child process that has already been waited on. It passes that pid to the stub as `DEADPID` through the `--driver` string. The stub then adds the nested detached worktree from inside a script, where the hook cannot see it.
- The case also checks that the ticket still merges, so the reap does not break the lane commit.
- During the red run I made a temporary backup of `fanout.py` at `/tmp/fanout.bak.<pid>`. That breaks the rule that throwaway files go only under `$SDLC_TMP_WORKTREES`; the backup was restored and deleted.
- The uncommitted `run.sh`, `run-selftest.sh` and `reap-tmp-worktrees.sh` changes come from step 1 and were not touched here.
