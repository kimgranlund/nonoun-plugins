<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
None. Every gate was already green, so there was nothing to fix and I did not need to run `codex_roles.py generate`.

## Checks
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0 ("ok: 18 role levels, 8 agents checked")
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0 ("steps selftest: PASS")
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0 ("Codex agent definitions verified")
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: exit 0
- `python3 scripts/check-packaging.py`: exit 0 ("PASS: catalog parity, identity, skill routes, hook isolation and context links")
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (ends with "ok: plugin validate"; it printed "skip: shellcheck not installed")
- `git diff --check`: exit 0

## Notes
- The working tree already had uncommitted changes this step did not make: `docs/README.md`, four `plugin.json` manifests, and an untracked `docs/reports/release-0.19.0.md`. They look like concurrent release work, so I left them alone.
- `check.sh` skipped shellcheck because shellcheck is not installed here.
