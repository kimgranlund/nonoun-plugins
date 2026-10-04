<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
None. Every gate was already green, so nothing needed fixing.

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. The run, hook and hook live probe selftests all passed, and plugin validate is ok. It skipped shellcheck because shellcheck is not installed.
- `python3 scripts/check-packaging.py`: exit 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0
- `python3 plugins/sdlc-lite/scripts/evals.py check`: exit 0, "ok (1 evals, lock cites .sdlc/evals/0000-baseline.md)"
- `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: exit 0
- Em dash check on added lines in plugins, docs and .sdlc/AGENTS.md: passed
- Em dash check on untracked files in plugins, docs and .sdlc/evals: passed
- Trailing whitespace check on the same untracked files: passed
- `git diff --quiet "$SDLC_BASE_SHA" -- run.sh models.json`: exit 0, so neither file changed

## Notes
check.sh skipped shellcheck because it is not installed on this host, so shell lint was not run.
