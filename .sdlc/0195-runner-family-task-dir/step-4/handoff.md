## Task goal
Make the verifier model-family rule fire for a verifier launched at the task directory, on Claude and on Codex.

## Step 4: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1, 2, and 3.

1. From the repository root, run every gate the handoff's Done-when names:
   - `bash plugins/sdlc-lite/scripts/check.sh` (259 s at plan time; it runs the codex, lifecycle, run, hook, and other selftests plus `check.py`);
   - `python3 scripts/check-packaging.py`;
   - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`;
   - `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`;
   - `git diff --check "$SDLC_BASE_SHA"`, excluding `.sdlc`.
2. Fix any red that steps 1 to 3 introduced, inside the files those steps changed. A gate already red at the build-start HEAD is reported as Status `inherited red`.
3. If a fix changes `plugins/sdlc-lite/scripts/run.sh`, the step 3 evidence belongs to the earlier blob. Say so under Limits in `docs/validation/runner-family-task-dir-live-run.md`, naming both `git hash-object` values. Never edit the evidence files.
4. Confirm that no em dash (U+2014) was added in any changed tracked file.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `! git diff "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -E "^\+" | grep -qF "$(printf '\342\200\224')"`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/scripts/codex_roles.py -e plugins/sdlc-lite/scripts/codex-selftest.py -e docs/codex-role-execution.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/validation/runner-family-task-dir-live-run(\.md|/)")"`
