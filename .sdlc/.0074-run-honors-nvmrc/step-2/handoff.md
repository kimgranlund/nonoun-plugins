## Task goal
Headless builders run the Node version the repo pins in .nvmrc.

## Step 2: Document the .nvmrc behavior
level: L1
### Do
In the repo-root `CLAUDE.md`, extend the `scripts/run.sh` bullet under Layout with one sentence covering:
- after the git preflight it reads the target repo's toplevel `.nvmrc`
- it matches it against `$NVM_DIR` (else `~/.nvm`) `versions/node`, exact or highest numeric prefix
- it prepends that `bin` to PATH, or leaves PATH unchanged with one stderr line for a missing version or an alias
- it never sources nvm
- `SDLC_DRY_RUN=1` shows the resolution

Also update the `run.sh` selftest description in the Commands bullet if it names the selftest's scope, and the comment at the top of `plugins/sdlc-lite/scripts/run-selftest.sh` so it names the nvmrc cases. `.claude/agents/sdlc-lite-author.md` does not describe this behavior, so leave it unchanged.
### Acceptance criteria
- `grep -F "run.sh" CLAUDE.md | grep -qF ".nvmrc"`
- `head -8 plugins/sdlc-lite/scripts/run-selftest.sh | grep -qiF "nvmrc"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
