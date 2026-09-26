<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-pattern-kill.sh`: new executable PreToolUse(Bash) hook. When SDLC_ROLE is unset it exits 0. Inside a role run it exits 2 for `pkill` or `killall` in command position, and for `kill` fed by `pgrep` (`$(...)`, backticks, or `| xargs kill`). The block message names the role and PIDs and says never to kill by name pattern. Quoted mentions are masked first; parse failures fail closed to a looser raw scan.
- `plugins/sdlc-lite/hooks/hooks.json`: registered the hook in the `"matcher": "Bash"` list, after block-background.sh.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: added the `pk=` variable, the header comment update, and the fixtures the handoff lists. Blocked with role: pkill (also checks stderr for PID and role), killall, `kill $(pgrep ...)`, `pgrep | xargs kill`, `sudo pkill`, `cd x && pkill -f vite`. Allowed with role: `kill 12345`, `kill $pid`, `grep -n "pkill" f`. Allowed without role: pkill. The pattern words are built with printf.
- `plugins/sdlc-lite/scripts/check.sh`: the header comment now names block-pattern-kill.sh.

## Checks
- Criteria 1 to 12 (the 9 hook exit-code and stderr checks, `test -x`, the hooks.json `jq -e` check, the selftest grep): all ran from the repo root and all passed. I also ran criterion 8 exactly as written: passed.
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: printed `hook selftest: PASS`, exit 0.
- `shellcheck --severity=warning` on the hook and hook-selftest.sh: exit 0, no output.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. All selftests passed, plus `ok: shellcheck` and `ok: plugin validate`.
- Bite check (a sanity check of my own; the verifier still runs the worktree version). I copied the hooks and the selftest under `$SDLC_TMP_WORKTREES`, made the hook copy always `exit 0`, and ran the selftest. It printed `hook selftest: FAIL: block-pattern-kill blocks pkill: exit 0, want 2`, exit 1. Copies removed afterwards.
- Extra cases I ran against the hook, all as expected:
  - Blocked: `kill -9 \`pgrep node\``, `kill "$(pgrep x)"`, `'pkill' -f x`, `pk""ill x`, `p\kill x`, `bash -c "pkill x"`, `timeout 5 pkill x`, `env FOO=1 pkill x`, `/usr/bin/pkill x`, `pgrep x | xargs -r kill -9`, `if true; then pkill x; fi`, a heredoc piped to sh, an unterminated quote, `( pkill x )`, `{ pkill x; }`.
  - Allowed: `kill %1`, `man pkill`, `echo pkill`, `ls # pkill x`, `pgrep -f vite`, `pgrep x || kill 12`, and a commit message that quotes the words.
- Fail-closed path: with no python3 on PATH, `pkill x` exits 2 and `kill 12345` exits 0. A quoted mention like `grep -n "pkill" f` also exits 2 in that mode, because the raw scan does no masking.

## Notes
- The hook matches only the forms the handoff names. `ps aux | grep x | awk ... | xargs kill` and a pattern hidden in a variable (`p=pkill; $p x`) are not blocked.
- The command-position wrapper list goes beyond the handoff's six words (sudo, xargs, env, command, nohup, timeout N). It also accepts `VAR=value` assignments and the shell keywords then, do, else, if, while, until, time, exec and `!`, so `if ...; then pkill x; fi` is caught.
- Any command containing a heredoc (`<<`) or a shell or evaluator word (bash, sh, zsh, dash, ksh, fish, eval, ssh, su) falls back to the raw scan. So `cat > f <<EOF` with the words in its body is blocked inside role runs. That is deliberate fail-closed behavior.
- I did not update CLAUDE.md or other docs; step 2 of this task covers documenting the hook.
- Nothing is committed.
