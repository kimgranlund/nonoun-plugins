## Task goal
`plugins/sdlc-lite/scripts/hook-selftest.sh` never fails from a race between feeding a hook its JSON and the hook exiting early: every hook fixture reports the hook's own exit code, so the selftest is deterministic.

Diagnosis (conductor, from reading the code): hook-selftest.sh runs under `set -uo pipefail`, and its `run()` helper feeds the payload with `printf '%s' "$json" | env ... "$hook"`. Every hook exits 0 before reading stdin when its role gate does not match (`[[ -n "${SDLC_ROLE:-}" ]] || exit 0`; block-repo-format.sh when the role is not builder), and block-pattern-kill.sh never reads stdin on its early-exit paths. When the hook exits before printf writes, printf gets SIGPIPE (exit 141), and pipefail makes the pipeline status 141 instead of the hook's 0. Confirm this (for example by making the race likely, such as a hook fixture that exits at once while the feeder sleeps briefly), then fix the harness so a hook that ignores stdin cannot change the reported exit code.

## Step 1: Fix hook-selftest.sh's run() helper to stop piping into the hook
level: L2
### Do
In `plugins/sdlc-lite/scripts/hook-selftest.sh`, the `run()` helper currently does `printf '%s' "$json" | env -u SDLC_ROLE -u SDLC_HEADLESS -u SDLC_TMP_WORKTREES "$@" "$hook" 3>&1 1>/dev/null 2>&3`. Under this file's `set -uo pipefail`, if the hook exits before reading stdin (every early-exit path in `block-repo-format.sh`, `block-pattern-kill.sh`, and the role gate in the others), `printf`'s write can get SIGPIPE (exit 141), and pipefail reports 141 instead of the hook's real exit code — the intermittent `check.sh` failure this ticket traces.

Confirm the race first: write a throwaway hook (`printf '#!/usr/bin/env bash\nexit 0\n' >tmp; chmod +x tmp`) that exits immediately without reading stdin, feed it a ~200000-byte string through the exact current `printf | env ... "$hook"` pipe in a loop of 20 runs, and note how many report a non-zero exit under `set -uo pipefail` (this reliably reproduces the race on this host — 30/30 wrong in a manual check). Then fix `run()` so the hook's stdin comes from something that is not a shell pipe stage counted by `pipefail` — write `$json` to a temp file and redirect the hook's stdin from it (`rm` the temp file after), or use process substitution (`< <(printf '%s' "$json")`) — either removes the race by construction rather than by luck. Keep the `3>&1 1>/dev/null 2>&3` fd juggling so `run()` still returns exactly the hook's exit code and still yields its stderr as the captured output. Rerun the same 20-iteration large-payload loop through the fixed helper and confirm 0 wrong.

Keep every existing fixture's expected exit code and stderr `grep` unchanged — this is a harness-only change, `plugins/sdlc-lite/hooks/*.sh` is untouched (a hook exiting without reading stdin is valid in production).

Also check `plugins/sdlc-lite/scripts/hook-live-probe.sh`'s own hook-feeding code (the `write_capture` wrapper and the offline-selftest stub's `run_hook`, both of which also do `printf ... | ... "$hook"`): neither of those scripts sets `set -o pipefail` around that pipe, so `$?` there already reflects the hook's own exit status, not the feeder's. Leave them as is and say so in the builder notes; do not add `pipefail` there.

### Acceptance criteria
- `! grep -qF 'json" | env' plugins/sdlc-lite/scripts/hook-selftest.sh` (the vulnerable pipe-into-hook pattern in `run()` is gone; currently false — the pattern is present at line 40)
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `plugins/sdlc-lite/scripts/hook-selftest.sh` (exits 0, prints `hook selftest: PASS`)
- (guard) `plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest` (exits 0, prints `hook live probe selftest: PASS`)
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/hooks/` (no change under `hooks/`)
