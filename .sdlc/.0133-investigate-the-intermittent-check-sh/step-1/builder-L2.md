<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/hook-selftest.sh: `run()` now feeds the hook's stdin by process substitution (`< <(printf '%s' "$json")`) instead of a pipe. It keeps the `3>&1 1>/dev/null 2>&3` fd juggling, and a comment explains the SIGPIPE/pipefail race.

## Checks
- Race repro before the fix: a throwaway hook that exits 0 without reading stdin, fed a 200000-byte payload through the old `printf | env ... "$hook"` pipe under `set -uo pipefail`, 20 runs: 20 of 20 reported non-zero (race confirmed).
- The same 20-run loop through the fixed form (`env ... "$hook" ... < <(printf ...)`): 0 wrong.
- `! grep -qF 'json" | env' plugins/sdlc-lite/scripts/hook-selftest.sh`: exit 0 (pass)
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/hook-selftest.sh`: exit 0
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: exit 0, printed `hook selftest: PASS`
- `plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: exit 0, printed `hook live probe selftest: PASS`
- `git diff --quiet HEAD -- plugins/sdlc-lite/hooks/`: exit 0

## Notes
- I left `hook-live-probe.sh` unchanged, as the handoff asked. Its `write_capture` wrapper and its stub `run_hook` also pipe into the hook, but that script never sets `pipefail` around those pipes, so `$?` there is already the hook's own exit status. I did not add `pipefail`.
- Nothing under `plugins/sdlc-lite/hooks/` changed.
