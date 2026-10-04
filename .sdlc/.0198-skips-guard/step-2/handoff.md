## Task goal
Add a skips.md guard to tickets.py check and close, exempting tickets closed before the feature.

## Step 2: gates green
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every project gate named in the handoff's Done-when on the tree that step 1 left, and fix any red that step 1 introduced. Fix only in `plugins/sdlc-lite/scripts/tickets.py`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md` and `docs/maintenance/sdlc-internals.md`. Depends on: step 1.

All four gates were green at the build-start HEAD a5a0e21:
- `check.sh` rc 0 in about 4 minutes;
- `check-packaging.py` PASS;
- `codex_roles.py generate --check` verified;
- `tickets.py --root .sdlc check` printed `ok: 214 tickets, roadmap current`.

A red gate here that is also red at HEAD is reported as Status `inherited red`. handoff-format is not a preloaded role skill (no agent's `skills:` list names it), so no Codex regeneration is expected. If `codex_roles.py generate --check` goes red, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` and report the generated paths as a scope widening rather than editing them by hand.

What is and is not proven red here:
- The `tickets.py check` gate's red shape was observed on a fixture: a done ticket with a stale roadmap exits 1 with `roadmap.md: stale or missing`.
- `check.sh`, `check-packaging.py` and `codex_roles.py generate --check` were not shown red on this host by this plan, so this step proves only that they pass, not that they bite.
- `git diff --check` is scoped to the three changed files.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/tickets.py plugins/sdlc-lite/skills/handoff-format/SKILL.md docs/maintenance/sdlc-internals.md`
- `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/tickets.py -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e docs/maintenance/sdlc-internals.md)"`
