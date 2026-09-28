## Task goal
A headless session (claude -p: bench, dogfood, fanout lanes, every role run) can never background a role run or a gate and then end its turn.

## Step 1: Hook that denies background Bash in headless sessions, with its selftest
level: L2
### Do
- Add `plugins/sdlc-lite/hooks/block-background.sh` (executable, `#!/usr/bin/env bash`). It reads the hook JSON from stdin with `jq`. It exits 0 unless both of these hold: `SDLC_ROLE` is non-empty or `SDLC_HEADLESS` is `1`, and `.tool_input.run_in_background == true`. When both hold, it prints this message to stderr and exits 2: "headless session (sdlc role '<role>' or SDLC_HEADLESS=1): run this in the foreground with the Bash timeout at 600000 or more; do not use run_in_background, and never end the turn while it runs, because that ends the session and abandons the work". The words `foreground` and `600000` must appear. `run_in_background` false, absent, or null must pass (exit 0), whatever the command is.
- Register it in `plugins/sdlc-lite/hooks/hooks.json` as a second command hook under the existing `"matcher": "Bash"` PreToolUse entry. Use the same `"${CLAUDE_PLUGIN_ROOT}/hooks/..."` quoting style. Keep `block-publish.sh` unchanged.
- Add `plugins/sdlc-lite/scripts/hook-selftest.sh`. It runs both hooks with fixture JSON on stdin and a controlled env, and never inherits the caller's `SDLC_ROLE`/`SDLC_HEADLESS`: use `env -u SDLC_ROLE -u SDLC_HEADLESS ...` as the base, because builders and verifiers run check.sh with `SDLC_ROLE` set. Cases:
  - SDLC_ROLE set + background true → 2, and stderr names foreground and 600000.
  - SDLC_HEADLESS=1 + background true → 2.
  - Neither set + background true → 0 (negative control).
  - SDLC_ROLE set + background false → 0.
  - SDLC_ROLE set + background absent → 0.
  - SDLC_HEADLESS=0 + background true → 0.
  - block-publish.sh still exits 2 on a push command with SDLC_ROLE set, and 0 on `ls`. Build the push string at runtime, for example `printf 'git %s' push`, so the live hook does not block the selftest's own Bash call.

  It prints `hook selftest: PASS` or `hook selftest: FAIL: <case>` and exits non-zero on failure, in the style of `scripts/run-selftest.sh`.
- Wire it into `plugins/sdlc-lite/scripts/check.sh` next to `run-selftest.sh` (`bash "$root/scripts/hook-selftest.sh" || fail=1`). Update the check.sh header comment.
### Acceptance criteria
- `test -x plugins/sdlc-lite/hooks/block-background.sh`
- `out=$(printf '%s' '{"tool_input":{"command":"sleep 1","run_in_background":true}}' | env -u SDLC_HEADLESS SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-background.sh 2>&1); test $? -eq 2 && grep -q 600000 <<<"$out" && grep -qi foreground <<<"$out"`
- `printf '%s' '{"tool_input":{"command":"sleep 1","run_in_background":true}}' | env -u SDLC_ROLE SDLC_HEADLESS=1 plugins/sdlc-lite/hooks/block-background.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"sleep 1","run_in_background":true}}' | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-background.sh` exits 0 (negative control; red now only because the file is missing)
- `printf '%s' '{"tool_input":{"command":"sleep 1"}}' | env -u SDLC_HEADLESS SDLC_ROLE=verifier plugins/sdlc-lite/hooks/block-background.sh` exits 0
- `grep -q 'hooks/block-background.sh' plugins/sdlc-lite/hooks/hooks.json && jq -e '.hooks.PreToolUse[] | select(.matcher=="Bash") | .hooks | length == 2' plugins/sdlc-lite/hooks/hooks.json`
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh | grep -q 'hook selftest: PASS'`
- `grep -q 'hook-selftest.sh' plugins/sdlc-lite/scripts/check.sh`
- (guard) `printf '{"tool_input":{"command":"git %s"}}' push | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/hooks/*.sh plugins/sdlc-lite/scripts/*.sh`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (green on the base commit today)
