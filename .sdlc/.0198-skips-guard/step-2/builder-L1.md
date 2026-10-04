<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
None. Step 1's tree needed no fixes.

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh`: rc 0. The run, hook and hook live probe selftests passed, and `plugin validate` was ok. `shellcheck` is not installed, so that part was skipped.
- `python3 scripts/check-packaging.py`: PASS.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: "Codex agent definitions verified".
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: "ok: 214 tickets, roadmap current", rc 0.
- `git diff --check "$SDLC_BASE_SHA"` on the three changed files: rc 0.
- The scope `test -z ...` command: rc 0, so no file outside the three allowed ones changed.

## Notes
- These runs show the gates pass. They do not show the gates would reject a defect, and I did not run a negative control.
- `git status` shows only two untracked files, `base-sha` and `builder-L1.attempt.json`. Both are in the step-2 artifacts folder.
