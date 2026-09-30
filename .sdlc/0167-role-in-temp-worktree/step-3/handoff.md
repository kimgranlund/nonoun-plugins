## Task goal
A conductor in a repository whose checkout must not be touched, such as a bare-clone layout with a dirty primary worktree, knows how to run a role from a clean temporary worktree and where `.sdlc/` state lives while it does.

## Step 3: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root and fix any red that steps 1 and 2 introduced, in `plugins/sdlc-lite/skills/handoff-format/run-operations.md`, `plugins/sdlc-lite/skills/chain/SKILL.md`, `plugins/sdlc-lite/scripts/run-selftest.sh`, or generated Codex agents via `codex_roles.py generate`. A gate already red at the build-start HEAD is reported as `inherited red`. `check.sh` takes about 90 seconds.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
