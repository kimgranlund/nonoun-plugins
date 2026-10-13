<!-- role=solo level=L2 model=sonnet effort=high -->
## Output
T-0508 is delivered: the verifier (opus, L2) passed all six criteria and found nothing out of scope. Nothing is committed.

The fix has two parts. Before it, `/ask` grepped a hard-coded `.sdlc/tickets`, so on a flat layout it exited 2 and missed the blocked ticket.
- **New `tickets.py blockers [--scope PATH]`:** it lists open tickets that are `blocked` or have a `## Deferred` heading. It reads the ticket directory through the existing `layout_paths`, so flat, `ticket_root: tickets` and `layout: topics` give the same inventory. Done and dropped tickets and closed `.NNNN-*` folders never count. `--scope` only narrows the results; it doesn't change where the root is found. A missing ticket directory or scope is an error naming the path, never `none`.
- **`skills/ask/SKILL.md`:** it now runs that command from the repo root. A supplied task dir only narrows the report. The verdict and gap greps skip closed folders. I added the `tickets.py` command to `allowed-tools`.

I also updated `check.py` item 29 to require the new command text. I added the dated evidence report `docs/reports/2026-10-12-ask-layout-sweep.md` and left the Astra review untouched.

Files changed:
- `plugins/sdlc-lite/scripts/tickets.py`
- `plugins/sdlc-lite/scripts/check.py`
- `plugins/sdlc-lite/skills/ask/SKILL.md`
- `docs/reports/2026-10-12-ask-layout-sweep.md` (new)

Checks (outcome; exit code where I ran the command):
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes. It covers flat, ticket-root and topics fixtures with one inventory, scoped runs, closed-ticket exclusion, and a missing scope and ticket dir. It also asserts the old baseline grep exits 2 on the flat fixture.
- Mutation controls: removing the active-status/closed-folder exclusion, or the scope filter, made the selftest fail. The verifier repeated these and also broke the layout resolution, which failed too.
- `python3 plugins/sdlc-lite/scripts/check.py` passes (exit 0).
- `python3 scripts/check-packaging.py` passes.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `claude_roles.py generate --check` pass, and `prompt_lint.py` reports 0 errors.
- `git diff --check` exits 0.
- Throwaway flat project, using the commands the revised skill prescribes (observed output is in the report):
  - Baseline: the old grep exits 2.
  - Fixed: `blockers` lists the blocked and the deferred tickets and excludes the done one.
  - Scoped to one ticket dir: only that ticket.
  - Missing directories: each is an error that names the path.

Still open:
- I did not run a live `/sdlc-lite:ask` session with a model. I ran the skill's commands directly, and the report says so.
- I did not run the full `check.sh` suite, which the Astra review recorded as incomplete.
- The ticket has no `(red)` criteria, so no `red` controls ran.
- `verify_scope.py` printed `tests-gate: criteria: no acceptance criterion` and exited 1, so I took the `verify: needed` path and the verifier ran. It wrote `.sdlc/0508-ask-ticket-layout-sweep/verifier-L2.md`.
