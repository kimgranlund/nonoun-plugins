## Task goal
A confirmed root cause for why hooks/block-background.sh (T-0072) did not stop the builder L2 run in T-0103's reported incident, and whether the Agent guard shipped in T-0076 (or anything else) now closes that route.

## Step 1: run.sh raises the Bash timeouts for every role run
level: L2
### Do
In `plugins/sdlc-lite/scripts/run.sh`, before the real `claude` launch (the `SDLC_ROLE=... "${cmd[@]}"` line), set `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` to `3600000`, the value bench.sh uses.
- Keep an inherited value only when it is a plain integer and at least 3600000. Replace anything else (unset, lower, or not numeric) with 3600000.
- Export both, or pass them on the launch line like `SDLC_ROLE`.
- Add a comment in the header saying why: Claude Code moves a foreground Bash call to the background once it passes its timeout, and no PreToolUse hook sees that (T-0105).

In `plugins/sdlc-lite/scripts/run-selftest.sh`, make a stub `claude` record the `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` it sees. Assert three cases:
- Unset: the stub sees `3600000` for both.
- Inherited `120000`: the stub sees `3600000`.
- Inherited `7200000`: the stub sees `7200000`.

Also update the selftest's header comment.
### Acceptance criteria
- `grep -q 'BASH_DEFAULT_TIMEOUT_MS' plugins/sdlc-lite/scripts/run.sh`
- `grep -q 'BASH_MAX_TIMEOUT_MS' plugins/sdlc-lite/scripts/run.sh`
- `grep -q '7200000' plugins/sdlc-lite/scripts/run-selftest.sh && grep -q 'BASH_DEFAULT_TIMEOUT_MS' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`
