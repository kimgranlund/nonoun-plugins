## Task goal
A harness that reads `.sdlc/*` learns the ticket and message folder systems from the entry files alone, and a fresh Claude role and a fresh Codex role, given only a path to a message file and no skill, ack it and reply correctly.

## Step 5: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `.sdlc/AGENTS.md`
### Do
Depends on: steps 1 to 4.
- Run every gate below.
- Fix any red that steps 1 to 4 introduced, in the files those steps own.
- If a main sync left `.sdlc/AGENTS.md` stale, regenerate it with `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap`.
- A gate already red at this step's build-start HEAD comes back as builder Status `inherited red`.
- `tickets.py --root .sdlc check` was red at plan time only because the tracked router was stale. Step 2 regenerates the router and requires check to pass, so it is green from step 2 on.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA"`
