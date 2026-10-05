<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
None. Every gate was already green on the tree that steps 1 to 6 left, so nothing needed fixing.

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. It printed results selftest PASS, steps selftest PASS, fanout selftest PASS, traces selftest PASS, messages selftest PASS, run selftest PASS, hook selftest PASS, hook live probe selftest PASS, "Codex agent definitions verified" and "ok: plugin validate". It also printed "skip: shellcheck not installed".
- `python3 scripts/check-packaging.py`: exit 0, printed "PASS: catalog parity, identity, skill routes, hook isolation and context links".
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0, printed "Codex agent definitions verified".
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0, printed "ok: 188 tickets, roadmap current".
- `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: exit 0, no output.
- `! git diff "$SDLC_BASE_SHA" -- plugins docs | grep '^+' | grep -q <em dash>`: exit 0.
- `for f in $(git ls-files --others --exclude-standard -- plugins docs); do ! grep -q <em dash> "$f" || exit 1; done`: exit 0.
- Extra check: a trailing-whitespace grep over the two untracked files (`plugins/sdlc-lite/scripts/results.py`, `docs/reports/role-result-schema-live-run.md`). It found nothing. I ran it because `git diff --check` does not cover untracked files.

## Notes
- shellcheck is not installed on this host, so `check.sh` skipped its shellcheck stage. The shell scripts this ticket changed (`run.sh`, `run-selftest.sh`, `check.sh`) have not been linted by shellcheck.
- No gate was red, so I did not need the pre-build check at the base SHA.
