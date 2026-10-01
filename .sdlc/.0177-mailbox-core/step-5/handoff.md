## Task goal
`plugins/sdlc-lite/scripts/messages.py` runs a git-ignored `.sdlc/messages/` mailbox with a validated schema, an explicit new, read, done lifecycle, and a tested transition table, and `run.sh` prints a count notice before it launches a role.

## Step 5: gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 to 4. Run every gate below from the repository root, and fix any red that steps 1 to 4 introduced, staying within the files those steps changed. Report a gate that was already red at the build-start HEAD as `inherited red`.
- `check.sh` now includes the messages selftest (step 3).
- Shellcheck is skipped on this host when it is not installed (`check.sh` prints `skip:`). That is not a failure.
- The em-dash guards cover the lines added to tracked files and the whole of any new untracked file.
- Every guard here was green at HEAD c6d39d0 (`check.sh` exit 0 in about 2.5 minutes). Each went red in a detached worktree copy with injected defects: a corrupted `plugin.json`, a trailing-space line, an em-dash line, and a stray untracked file.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `! git diff "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep "^+" | grep -q "$(printf "\xe2\x80\x94")"`
- (guard) `git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | while read -r f; do ! grep -q "$(printf "\xe2\x80\x94")" "$f" || exit 1; done`
- (guard) `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.sh -e .gitignore -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/scripts/onboard.py -e docs/repo-onboarding/design.md -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md ); test -z "$out"`
