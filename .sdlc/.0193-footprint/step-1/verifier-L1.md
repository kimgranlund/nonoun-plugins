<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `footprint.py selftest`: pass. Evidence: ran it. It printed 11 `ok:` lines and `footprint selftest: PASS`, exit 0.
- Selftest output has a line starting `ok: negative control`: pass. Evidence: grep exit 0. The line is `ok: negative control: extra file fails check --max-files`.
- `.0181-messages-wait` measure lines: pass. Evidence: all 8 expected lines matched exactly.
- `.0175-ticket-root-router` measure lines: pass. Evidence: all 8 expected lines matched.
- `.0188-tighten-idle-note` measure lines: pass. Evidence: all 7 expected lines matched.
- `.0164-fix-skill-lints-task-folder` measure lines: pass. Evidence: all 7 expected lines matched.
- `check` at `--max-files 8 --max-bytes 8010` passes: pass. Evidence: printed `ok`, rc=0.
- `check --max-files 7` exits 1 and names the flag: pass. Evidence: rc=1, stderr `footprint: files 8 exceeds --max-files 7`.
- `check --max-bytes 8009` exits 1 and names the flag: pass. Evidence: rc=1, stderr `footprint: bytes 8010 exceeds --max-bytes 8009`.
- Scope guard (only `footprint.py` changed outside `.sdlc`): pass. Evidence: the command exited 0. `git status` shows only `footprint.py` untracked outside `.sdlc`.
- The four closed ticket folders are unchanged against `$SDLC_BASE_SHA`: pass. Evidence: `git diff --quiet` exited 0.
- Behavior spec points the criteria don't cover: pass. Evidence: I checked each directly.
  - `check` with no limit exits 2.
  - `check` on a missing dir exits 2.
  - Output order and the `planner_bytes` line match the spec.
  - The shebang is `#!/usr/bin/env python3`.
  - The script opens files for writing only inside selftest fixtures (script lines 119-122, in the selftest fixture writer). Measuring opens files read-only (line 43).
- The checks can go red: pass. Evidence: the `--max-files 7` and `--max-bytes 8009` runs on the real folder exited 1, so the limit comparison fails when exceeded. The exact-value greps on four real folders would go red on any count drift.

## Out of scope changes
None. The only changed file outside `.sdlc` is `plugins/sdlc-lite/scripts/footprint.py`. The other untracked paths are task artifacts under `.sdlc/0193-footprint`.

## For the next attempt
None
