<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/fanout.py: each non-dry run mints its own id, `ctx['run_id'] = 'fanout-' + uuid4().hex[:12]`. It never reads `SDLC_ATTEMPT_ID`.
  - `say(ctx, lane, tid, event)` prints `[<run_id>] [<lane>] <id> <event>` and appends the same line to `logs/fanout.log` under the `PRINT` lock.
  - A new `run_logged` helper (Popen, binary line prefixing, `'wb'` overwrite, stdin DEVNULL) writes the driver and gate logs.
  - `FANOUT_RUN_ID` is exported in the driver env and the gate env (`dict(ENV, FANOUT_RUN_ID=...)`).
  - `report.md` has a new `- Run:` line.
  - The docstring now covers the run id and selftest case 9 (`resume case`), which is added.
- docs/maintenance/sdlc-internals.md: the fanout entry now states the `[<run_id>] ` prefix, the append-only `logs/fanout.log`, `FANOUT_RUN_ID`, and why fanout mints its own id instead of using `SDLC_ATTEMPT_ID`.

## Checks
- Resume probe (the criterion's full command): PROBE=0, pass.
- `grep -qF "resume case"` on fanout.py: 0. `grep -qF "FANOUT_RUN_ID"` on fanout.py: 0.
- `grep -qF "logs/fanout.log"` on sdlc-internals.md: 0. `grep -qF "FANOUT_RUN_ID"` on sdlc-internals.md: 0.
- Negative control: I set the id to the constant `'fanout-000000000000'` and ran `python3 plugins/sdlc-lite/scripts/fanout.py selftest`. It failed with `resume case: the two runs have distinct ids, got 'fanout-000000000000' and 'fanout-000000000000'`. After restoring the uuid line, selftest printed PASS.
- (guard) scope test: 0.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: ok, exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: rc=0. It printed `skip: shellcheck not installed`.
- (guard) `python3 scripts/check-packaging.py`: PASS.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: clean.

## Notes
- `plugins/sdlc-lite/skills/fanout/SKILL.md` is unchanged because it does not describe the printed line or log format, and the handoff only required an edit if it did.
- No existing selftest assertion checked the printed `[<lane>]` line, so none needed fixing.
