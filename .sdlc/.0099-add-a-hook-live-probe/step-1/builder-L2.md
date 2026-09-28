<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/hook-live-probe.sh`: the stub claude gains a `nodeny` mode, which runs the registered hook with `SDLC_HEADLESS` and `SDLC_ROLE` unset. The header comment for `STUB_MODE` and the section comment now name case (e). New case (e) runs `probe nodeny "$good"` and asserts exit 1 and the line `^verdict: FAIL: hook exit code 0, not 2`.

## Checks
- `plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: exit 0, printed `hook live probe selftest: PASS`.
- `grep -q "(e)" plugins/sdlc-lite/scripts/hook-live-probe.sh`: exit 0.
- Mutation check, the handoff's command run as given under `bash -c`: exit 0. With the `hook_rc != 2` check deleted, the selftest goes red.
- Temp dir check: ran the selftest with `TMPDIR` set to a fresh dir. It printed 0 `temp dir left behind` lines and left the dir empty.
- Live-mode guard (`git diff -U0 ... | awk ...`): exit 0. Every hunk is above the `# Live mode.` banner.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. The tail showed the probe selftest PASS, shellcheck ok and plugin validate ok.

## Notes
None
