<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/run-selftest.sh: added a `# heading rule:` case to the result-pick tests. The log holds two result events and neither is a task notification: first `## Verdict\npass`, then a later `done, see above` with no heading. `verifier L1` must exit 0, and the saved result must hold `## Verdict` and must not hold `done, see above`.

## Checks
- `grep -q '^# heading rule:' plugins/sdlc-lite/scripts/run-selftest.sh && grep -qF 'done, see above' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`, exit 0. I ran it after the edit and again after restoring run.sh.
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0, no findings.
- Mutation check: I replaced run.sh line `  (map(select(has_head)) | last)` with `  null` using a temporary sed edit. The selftest then went red: `run selftest: FAIL: result pick verifier L1: exit 3, want 0 (run.sh: verifier result lacks ## Verdict ...)`, exit 1. I restored run.sh afterwards (see Notes). After the restore, `git diff --stat` on run.sh shows 43 insertions and 18 deletions, the same as before the mutation; line 246 holds the heading rule again, and the selftest passes.

## Notes
- run.sh ended up exactly as it was before this step, but the restore took an extra step. After the mutation I ran `git checkout` on run.sh, which reset it to HEAD and threw away the uncommitted run.sh changes from earlier steps. I restored it from the full copy I had taken before the sed edit (the copy went to /tmp because `$SDLC_TMP_WORKTREES` did not exist yet). The copy is now deleted. The diff stat and the selftest both confirm the restore. Only run-selftest.sh has changed in this step.
