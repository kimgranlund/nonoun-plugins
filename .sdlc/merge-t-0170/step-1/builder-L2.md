<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run-selftest.sh`: resolved the merge conflict by keeping both lanes' additions. That is the integration branch's "temporary worktree recipe" test (header comment and body) and the runner lane's "self-edit" test (header comment and body).
- Merge commit a7783bb "Merge fanout/2026-09-29-runner (T-0170)". Git merged these without conflict: `docs/references/sdlc-internals.md`, `lifecycle-selftest.py`, `run.sh`, `run_lifecycle.py`, and the `.sdlc/0170-*` artifacts.

## Checks
- `bash -n run-selftest.sh` on the resolved file: ok.
- `bash plugins/sdlc-lite/scripts/check.sh` on the merged tree before committing: rc=0. It includes "run selftest: PASS", "hook selftest: PASS", "hook live probe selftest: PASS" and "ok: plugin validate". It printed "skip: shellcheck not installed".
- `bash plugins/sdlc-lite/scripts/check.sh` in a detached worktree at HEAD^1 (926f8d0): rc=0. Both runs are green, so the merge adds no findings.
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`: 3 words, pass.
- `git merge-base --is-ancestor fanout/2026-09-29-runner HEAD`: pass.
- `! git rev-parse -q --verify MERGE_HEAD`: pass.
- The `diff-tree --cc` conflict-marker guard: pass.

## Notes
- I compared the two `check.sh` runs by exit code only (both 0), not by diffing their logs.
- The throwaway base worktree was removed and pruned.
- `.sdlc/merge-t-0170/` is still untracked, as it was before the merge.
