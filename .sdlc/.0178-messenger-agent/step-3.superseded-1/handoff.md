## Task goal
`messenger` is a required declared agent for Claude and Codex that polls `messages/new/<harness>` every 10 seconds through `messages.py` and notifies its parent, with `check.py` coverage that fails when the agent file or its Codex mapping is missing.

## Step 3: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 and 2.

1. Run every gate in the handoff's done condition:
   - `codex_roles.py generate --check`
   - `scripts/check-packaging.py`
   - `codex-selftest.py`
   - `check.py`
   - `check.sh`, which also runs `claude plugin validate` and so validates the messenger's `model:` front matter
2. Fix any red that steps 1 and 2 introduced, staying inside the files those steps own. Regenerate the TOMLs with `generate` and never hand-edit them.
3. Keep `run.sh`'s role table and Claude model rows unchanged.
4. A gate already red at the build-start HEAD is reported as Status `inherited red`.
5. The verifier injects at least one defect (for example removing the `messenger` line from `models.json` in a temp copy) and states what failed. Step 1's temp-copy criteria are the reference negative controls.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh`
