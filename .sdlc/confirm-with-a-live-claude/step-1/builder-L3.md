<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/hook-live-probe.sh`: new executable opt-in probe (live mode plus an offline `--selftest` covering cases a to d, and a temp dir leak check).
- `plugins/sdlc-lite/scripts/check.sh`: runs `hook-live-probe.sh --selftest` after hook-selftest. The header comment now says the selftest runs offline and the live probe never runs here.
- `CLAUDE.md`: new Commands bullet for the live probe; the probe is added to the check.sh list and to the `hooks/block-background.sh` Layout bullet.
- `.claude/agents/sdlc-lite-author.md`: probe (and hook selftest) added to the check.sh list on line 24; the probe is mentioned where block-background.sh is described.

## Checks
- `test -x plugins/sdlc-lite/scripts/hook-live-probe.sh`: exit 0
- `out=$(bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest) && grep -q "hook live probe selftest: PASS" <<<"$out"`: exit 0
- `SDLC_PROBE_CLAUDE=/usr/bin/true bash plugins/sdlc-lite/scripts/hook-live-probe.sh --timeout 20; test $? -eq 1`: exit 0 (printed `verdict: FAIL: no Bash call captured`)
- `grep -q "hook-live-probe.sh\" --selftest" plugins/sdlc-lite/scripts/check.sh`: exit 0
- `! grep hook-live-probe plugins/sdlc-lite/scripts/check.sh | grep -v "^#" | grep -qv -- --selftest`: exit 0
- `grep -q hook-live-probe CLAUDE.md`: exit 0
- `grep -q hook-live-probe .claude/agents/sdlc-lite-author.md`: exit 0
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/hook-live-probe.sh`: exit 0
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (every selftest PASS, including `hook live probe selftest: PASS`; shellcheck ok; plugin validate ok)
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: `hook selftest: PASS`, exit 0

## Notes
- I did not run the live probe here. That is step 2, which spends the model call.
- Live mode runs claude with the temp dir as its working directory, so the repo's project settings and CLAUDE.md do not load into the probe session. User settings still apply. The hook is registered only through `--settings <tmp>/settings.json`, with no `--plugin-dir`.
- The capture wrapper records only the first Bash call to `payload.json` and `rc`. A model that retries in the foreground after the deny therefore cannot overwrite the call under test. Every call still goes through the real hook.
- The timeout uses a `python3` subprocess started with `start_new_session`. It kills the whole process group on timeout, on SIGTERM, and after claude exits. Case (d) also checks with `pgrep` that the stub's `sleep 47` child is gone.
- Case (d) accepts up to 20s, not "a few seconds". The host load average was about 95 during this build (hook-selftest alone took 28s). Case (d) measured 4s, and 20s is still well under the stub's 47s sleep.
- `python3` is a setup requirement: exit 2 if missing, the same as `jq`.
