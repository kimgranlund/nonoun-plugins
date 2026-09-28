## Task goal
A repeatable live probe proves, against the installed Claude Code version, that the subagent tool reaches PreToolUse as `tool_name` `Agent` (so the `"matcher": "Agent"` entry in plugins/sdlc-lite/hooks/hooks.json fires), that `hooks/block-background.sh` denies an Agent call with `run_in_background` missing or `true` under `SDLC_HEADLESS=1`, and that an Agent call with `run_in_background: false` is accepted by the tool schema and passes the hook. The probe is run once live and its result recorded in the task dir.

## Step 3: Gates green
level: L1
### Do
Run `bash plugins/sdlc-lite/scripts/check.sh` from the repo root in the foreground with the Bash timeout at 1800000. It took more than 15 minutes on this host, so do not background it. Fix any red that steps 1 and 2 introduced, for example shellcheck warnings, the probe selftest, or check.py doc guards. Keep the Bash probe behavior and the docs accurate. If a gate was already red at the build-start HEAD, report Status `inherited red: <tests>`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
