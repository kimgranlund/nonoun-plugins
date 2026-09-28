## Task goal
Builders never touch files or processes outside their own work.

## Step 1: Add the block-pattern-kill hook with selftest fixtures
level: L3
### Do
Add `plugins/sdlc-lite/hooks/block-pattern-kill.sh` (executable, bash, modeled on `hooks/block-publish.sh`). It is a PreToolUse(Bash) hook that reads `.tool_input.command` with jq.
- When `SDLC_ROLE` is unset or empty, it exits 0.
- Inside a role run it exits 2 when the command kills by pattern: `pkill` or `killall` in command position, `kill` fed by `pgrep` (`kill $(pgrep ...)`, backticks, or `pgrep ... | xargs kill`). Command position means the start of the command, or after `;`, `&`, `|`, `(`, `` ` ``, `{`, or `$(`, optionally behind `sudo`, `xargs`, `env`, `command`, `nohup`, or `timeout N`.
- On a block, its stderr names the role, says to stop only the PIDs you started (for example `$!` saved at launch), and says never to kill by name pattern.
- It allows `kill <pid>`, `kill $pid`, `kill %1`, and commands that only mention the words inside a quoted argument (for example `grep -n "pkill" f`). The quote masking can be simple. When it cannot parse, it fails closed and scans the raw text.

Register the hook in `plugins/sdlc-lite/hooks/hooks.json` under the existing `"matcher": "Bash"` hooks list, after block-background.sh.

In `plugins/sdlc-lite/scripts/hook-selftest.sh`:
- Add a `pk=` hook variable.
- Add fixtures: blocked with role (pkill, killall, `kill $(pgrep ...)`, `pgrep ... | xargs kill`, `sudo pkill`, `cd x && pkill -f vite`); allowed with role (`kill 12345`, `kill $pid`, `grep -n "pkill" f`); allowed without role (pkill).
- Build the words with printf where needed, and update the header comment.

Update the `check.sh` header comment so it names the new hook. Do not commit.
### Acceptance criteria
Run these from the repo root:
- `jq -n '{tool_input:{command:"pkill -f vite"}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- `jq -n '{tool_input:{command:"killall node"}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- `jq -n '{tool_input:{command:"kill $(pgrep -f vite)"}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- `jq -n '{tool_input:{command:"pgrep -f vite | xargs kill"}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- `jq -n '{tool_input:{command:"cd x && sudo pkill -f vite"}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- `out=$(jq -n '{tool_input:{command:"pkill -f vite"}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh 2>&1 >/dev/null); printf '%s' "$out" | grep -q PID`
- `jq -n '{tool_input:{command:"kill 12345"}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 0`
- `jq -n '{tool_input:{command:"grep -n \"pkill\" f"}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 0`
- `jq -n '{tool_input:{command:"pkill -f vite"}}' | env -u SDLC_ROLE plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 0`
- `test -x plugins/sdlc-lite/hooks/block-pattern-kill.sh`
- `jq -e '.hooks.PreToolUse[] | select(.matcher=="Bash") | .hooks[].command | select(contains("block-pattern-kill.sh"))' plugins/sdlc-lite/hooks/hooks.json`
- `grep -q 'block-pattern-kill.sh' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh` prints `hook selftest: PASS` and exits 0.
- `shellcheck --severity=warning plugins/sdlc-lite/hooks/block-pattern-kill.sh plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- The verifier observes that the selftest bites. It copies the hook into a throwaway worktree under `$SDLC_TMP_WORKTREES`, makes the copy always `exit 0`, and runs that worktree's `hook-selftest.sh`, which must print FAIL.
