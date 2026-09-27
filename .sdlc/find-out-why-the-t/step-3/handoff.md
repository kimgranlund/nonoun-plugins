## Task goal
A confirmed root cause for why hooks/block-background.sh (T-0072) did not stop the builder L2 run in T-0103's reported incident, and whether the Agent guard shipped in T-0076 (or anything else) now closes that route.

## Step 3: fanout selftest proves lane drivers get the high Bash timeouts
level: L1
### Do
`plugins/sdlc-lite/scripts/fanout.py` already passes `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` (`TIMEOUT_MS = '3600000'`) to the driver. Nothing checks it yet. Add two lines to the selftest `STUB` driver, next to its `SDLC_HEADLESS` check:
- `[ "${BASH_DEFAULT_TIMEOUT_MS:-}" = 3600000 ] || { echo "BASH_DEFAULT_TIMEOUT_MS not 3600000" >&2; exit 1; }`
- The same line for `BASH_MAX_TIMEOUT_MS`.
### Acceptance criteria
- `grep -qF 'BASH_DEFAULT_TIMEOUT_MS:-' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF 'BASH_MAX_TIMEOUT_MS:-' plugins/sdlc-lite/scripts/fanout.py`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
