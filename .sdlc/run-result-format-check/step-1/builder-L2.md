<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: once the result file and its `runs.jsonl` line are written, it checks the result for the role's required section. A builder must have `## Status` followed by done or blocked, and a verifier `## Verdict` followed by pass or fail, in any case. The other roles need their `## <Name>` heading. If the check fails, run.sh prints one stderr line naming the role, the section and the path, then exits 3. Both files stay on disk. The header comment now documents the check and exit codes 0 to 3.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: when `STUB_RESULT` is set, the stub `claude` prints that JSON file. Otherwise it gives the old `## Goal` output. The `.nvmrc` real run now gets a `## Status done` result. New cases expect exit 3 for: a builder with no `## Status` (also checks the stderr names it and that the result file and `runs.jsonl` line are kept), builder `maybe`, verifier `maybe`, and a planner with no `## Goal`. They expect exit 0 for builder `Done ` (blank line before it, trailing space after) and for verifier `pass`.

## Checks
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`.
- `shellcheck --severity=warning` on both scripts: clean.
- All four acceptance commands that start with `t=$(mktemp -d)`, run from the repo toplevel: all PASS (the three exit 3 cases and the builder `done` guard).
- `git diff --stat`: only the two scripts changed. The diff has the new exit 3 cases for a builder with no `## Status` and a verifier verdict of `maybe`.
- Not run: the new cases against the old run.sh to watch them fail first.
- Not run: `scripts/check.sh`.

## Notes
None
