## Task goal
When a step edits a shared contract (a catalog entry, a type, an exported API), the planner or verifier finds its dependents (tests, fixtures, lint fixtures) and puts them in scope before a later step trips on them.

## Step 2: Gates green
level: L1
### Do
Run every gate below from the repository root and fix any red that step 1 introduced. Keep all edits inside the files step 1 changed. If a generated TOML is stale, rerun `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` rather than editing the TOML. A gate that is already red at the build-start HEAD is reported as Status `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins`
