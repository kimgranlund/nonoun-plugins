## Task goal
A parent host can wait for mail with one blocking command instead of a polling subagent, and the command never claims, moves, or prints a message body.

## Step 5: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1, 2, 3, and 4.

1. Run every project gate from the repository root:
   - `bash plugins/sdlc-lite/scripts/check.sh`. It runs `codex_roles.py generate --check`, `check.py`, the tickets, messages, run, and hook selftests, and `claude plugin validate`. It took 252 s at plan time.
   - `python3 scripts/check-packaging.py`
   - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
   - `git diff --check`
2. Fix any red the earlier steps introduced, inside the files those steps changed. A gate already red at the build-start HEAD is reported as `inherited red`.
3. Confirm that no em dash (U+2014) was added in any changed or new file, including the untracked step 3 and 4 files.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check`
- (guard) `! git diff "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -E "^\+" | grep -qF "$(printf '\342\200\224')"`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/references/sdlc-internals.md -e docs/specs/ticket-stages/design.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/reports/messages-wait-live-run(\.md|/)")"`
