## Task goal
Branches owned by an outside agent can join fanout without hand-made lane/<x> refs, and ticket ids created on such a branch cannot collide with tickets.py ids (register the owner or branch, or reserve id ranges).

## Step 4: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root and fix any red that steps 1 to 3 introduced (their files only, plus a generated Codex agent file if `codex_roles.py generate --check` reports drift). `check.sh` runs `codex_roles.py generate --check`, the codex, lifecycle, tickets, board, steps, order, fanout and onboard selftests, `check.py`, the run and hook selftests, and `claude plugin validate`; shellcheck is skipped on this host. Do not commit.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
