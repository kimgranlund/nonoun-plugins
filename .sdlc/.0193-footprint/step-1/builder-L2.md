<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/footprint.py`: new file (stdlib only, executable). It provides measure, `check` and `selftest`.

## Checks
All commands were run from the repo root with `SDLC_BASE_SHA=99d29b8c`.
- `python3 plugins/sdlc-lite/scripts/footprint.py selftest`: PASS with 11 `ok:` lines, exit 0.
- `... selftest | grep -q '^ok: negative control'`: exit 0.
- Measure criteria for `.0181-messages-wait`, `.0175-ticket-root-router`, `.0188-tighten-idle-note` and `.0164-fix-skill-lints-task-folder`: all expected lines matched, exit 0 for each.
- `check .0188 --max-files 8 --max-bytes 8010`: printed `ok`, exit 0.
- `check .0188 --max-files 7`: exit 1, and stderr names `--max-files`.
- `check .0188 --max-bytes 8009`: exit 1, and stderr names `--max-bytes`.
- Scope criterion (only `footprint.py` changed outside `.sdlc`): exit 0.
- `git diff --quiet` on the four closed folders: exit 0.
- `git diff --check`: clean.

## Notes
- I set the executable bit on `footprint.py` (`chmod +x`). The handoff did not ask for this.
- In `check`, a negative limit or a repeated flag counts as bad args and exits 2.
