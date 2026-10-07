## Task goal
fanout.py routes every lane ticket path through the configured ticket root (`tickets.ticket_dir`), including the planned-scope overlap check that T-0203 added. Read `.sdlc/0204-fanout-resolver/handoff.md` (Goal, Intent) and the branch verifier's finding in `.sdlc/verify-t0204/step-1/verifier-L3.md` (section For the next attempt).

## Step 2: Route planned_scope through the ticket root and cover it in the selftest
level: L3

### Read first
- plugins/sdlc-lite/scripts/fanout.py (planned_scope, plan_overlap, wait_for_overlap, and the ticket_root lane selftest)
- .sdlc/verify-t0204/step-1/verifier-L3.md (the finding to fix)
- docs/references/sdlc-internals.md (the fanout entry sentence about overlap)

### Do
Make the smallest change that meets the criteria. No refactors, no extra tests or doc edits outside this step. Report blocked instead of looping. main was already merged into this branch (both sides kept).
1. In fanout.py, make `planned_scope` find the ticket folder through `tickets.ticket_dir(root)` (or pass the resolved ticket dir in via ctx), so a repo with `ticket_root: tickets` reads planned step scopes under `.sdlc/tickets/`, not `.sdlc/`.
2. Extend the existing `ticket_root` lane selftest: two lanes whose planned step-1 scopes share a file under `.sdlc/tickets/` must print the planned-scope pair line (the verifier's probe printed `not planned`). It must fail on the pre-change code.
3. Update the fanout sentence in docs/references/sdlc-internals.md so it says the planned-scope overlap check also reads the configured ticket root.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- `grep -q "ticket_dir" plugins/sdlc-lite/scripts/fanout.py`
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 scripts/check-packaging.py`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `git diff --check main -- plugins docs`
