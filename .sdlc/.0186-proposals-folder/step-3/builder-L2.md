<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
None. Every gate was already green, so nothing needed fixing.

## Checks
All commands were run from the worktree root with base SHA 66586153cc4a3c4fe5979f1aac181af633bc646e:
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. The log includes `proposals selftest: PASS`. shellcheck is not installed, so the script skipped that check.
- `python3 scripts/check-packaging.py`: exit 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0
- `python3 plugins/sdlc-lite/scripts/proposals.py selftest`: exit 0
- `git diff --check` against the base, in both forms the criterion names: exit 0
- Em dash guard on added diff lines: passed
- Em dash guard on untracked files under plugins, docs and .sdlc/proposals: passed
- Trailing whitespace guard on those untracked files: passed
- `git diff --quiet` on `run.sh` and `models.json`: exit 0
- Changed-file allowlist guard: no files outside the allowlist

## Notes
shellcheck is not installed on this machine, so `check.sh` skipped its shellcheck stage.
