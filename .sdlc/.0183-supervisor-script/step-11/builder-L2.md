<!-- role=builder level=L2 model=opus effort=low -->
## Status
inherited red: traces selftest (corpus: attempts in no row: .sdlc/0183-supervisor-script/step-7.superseded-1/step-7/builder-L3.attempt.json)

## Changes
- docs/maintenance/sdlc-internals.md: added a `## scripts/supervisor.py` entry (one paragraph) just before `## scripts/traces.py`.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: added a `.sdlc/supervisor/` line to the layout block, and added `.sdlc/supervisor/{hosts.local.json,status.json,state.json,lock,STOP,wakes/}` to the ignore list.
- plugins/sdlc-lite/AGENTS.md: added a Behavioral invariants bullet saying the supervisor never claims, moves, or reads a message body, and that a wake follows unattended-run rules.

## Checks
- `grep -q 'scripts/supervisor.py' docs/maintenance/sdlc-internals.md`: pass
- `grep -q '.sdlc/supervisor/' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass
- `grep -q 'supervisor' plugins/sdlc-lite/AGENTS.md`: pass
- (guard) em dash grep on sdlc-internals.md: pass. The other two files have no em dash either.
- (guard) scope diff with SDLC_BASE_SHA taken from step-11/base-sha: pass. Only the 3 allowed files changed.
- `git diff --check`: clean
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: rc=1. The only failure is `traces selftest: FAIL` on the corpus case. The supervisor selftest passes, and so does everything else.
- Pre-build check: ran the same `check.sh` in a detached worktree at base 0e55731 (`$SDLC_TMP_WORKTREES/base`). It also gave rc=1, with the identical `traces selftest: FAIL` on the same corpus line. I removed that worktree afterwards.

## Notes
- The traces corpus case reads this repo's `.sdlc` trail. The file `.sdlc/0183-supervisor-script/step-7.superseded-1/step-7/builder-L3.attempt.json` sits in a nested `step-7/` inside a superseded dir, and it was already present before this step. My edits only touch docs, so they cannot cause this failure.
- The handoff says the supervisor docstring names entries to ignore. The docstring names no repo ignore list. What it has is the `.gitignore` that `init` writes (`hosts.local.json`, `status.json`, `state.json`, `lock`, `STOP`, `wakes/`), so I used those 6 entries, prefixed with `.sdlc/supervisor/`.
