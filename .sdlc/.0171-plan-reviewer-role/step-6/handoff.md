## Task goal
A cross-cutting or risky plan, or any replan, gets an independent semantic review before a builder starts, and a defective plan is rejected before it costs a build.

## Step 6: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on steps 1 to 5. Run every gate below from the repository root and fix any red that the earlier steps introduced, touching only what the fix needs: `bash plugins/sdlc-lite/scripts/check.sh` (123 s at the build-start HEAD, no model call; it includes `check.py`, `codex_roles.py generate --check`, `codex-selftest.py`, `lifecycle-selftest.py`, the steps, order, board, tickets, fanout, onboard, traces selftests, `run-selftest.sh`, the hook selftests, shellcheck when installed, and `claude plugin validate`), `python3 scripts/check-packaging.py`, and `git diff --check` over the changed files. A gate red at the build-start HEAD is `inherited red: <tests>` per the builder contract. If `generate --check` reports drift, rerun `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` rather than editing a profile by hand.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
