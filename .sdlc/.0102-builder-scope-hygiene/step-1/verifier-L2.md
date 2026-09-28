<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- pkill blocked with role (exit 2): pass. Evidence: `jq -n '{tool_input:{command:"pkill -f vite"}}' | SDLC_ROLE=builder hooks/block-pattern-kill.sh` gave exit 2 (c1).
- killall blocked with role: pass. Evidence: `killall node` gave exit 2 (c2).
- `kill $(pgrep -f vite)` blocked with role: pass. Evidence: exit 2 (c3).
- `pgrep -f vite | xargs kill` blocked with role: pass. Evidence: exit 2 (c4).
- `cd x && sudo pkill -f vite` blocked with role: pass. Evidence: exit 2 (c5).
- Block stderr names PID: pass. Evidence: the `out=$(...2>&1 >/dev/null); grep -q PID` check exited 0 (c6). The full stderr reads "Blocked for sdlc role 'builder': killing by name pattern ... Stop only the PIDs you started, for example save $! at launch and kill that PID. Never kill by name pattern." It names the role, the PID-only rule and the ban on name patterns.
- `kill 12345` allowed with role: pass. Evidence: exit 0 (c7). `kill $pid`, `kill %1`, `echo hi` and a bare `pgrep -f vite` also exit 0 (extras).
- `grep -n "pkill" f` allowed with role: pass. Evidence: exit 0 (c8).
- pkill allowed without SDLC_ROLE: pass. Evidence: `env -u SDLC_ROLE` run gave exit 0 (c9).
- Hook is executable: pass. Evidence: `test -x` exit 0 (c10).
- Registered in hooks.json under the Bash matcher: pass. Evidence: the `jq -e` check printed `"\"${CLAUDE_PLUGIN_ROOT}/hooks/block-pattern-kill.sh\""` and exited 0. The diff shows it added after block-background.sh in the same list.
- hook-selftest.sh references the hook: pass. Evidence: `grep -q 'block-pattern-kill.sh'` exit 0 (c12). The diff adds `pk=` plus the blocked, allowed and no-role fixtures and the updated header comment.
- `bash hook-selftest.sh` prints `hook selftest: PASS`, exit 0: pass. Evidence: run with `env -u SDLC_ROLE -u SDLC_HEADLESS`, it printed `hook selftest: PASS`, rc=0.
- shellcheck at warning severity on the hook and the selftest: pass. Evidence: exit 0, no output (c14).
- (guard) `check.sh`: pass. Evidence: rc=0. The tail showed `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.
- Selftest bites: pass. Evidence: I made a throwaway worktree under `$SDLC_TMP_WORKTREES`, copied in the builder's `hook-selftest.sh` and replaced the hook with `exit 0`. Its selftest printed `hook selftest: FAIL: block-pattern-kill blocks pkill: exit 0, want 2`, rc=1. The worktree is removed; `git worktree list` shows only the two real worktrees. The biting variable is the exit code of the pkill fixture. The no-role and allow fixtures cannot bite against an always-exit-0 hook.
- Builder claim "hook live in this session": accepted. Evidence: two of my own Bash calls were denied by the registered hook with the message above. Both contained a shell word (`bash`, or a heredoc) plus the kill word, which is the documented fail-closed raw scan. I re-ran the checks without that combination.

Steelman of a possible fail: the raw-scan fallback blocks `bash x` with pkill text in a heredoc. The handoff says "When it cannot parse, it fails closed and scans the raw text", and the builder's Notes document the shell-word and heredoc trigger. The finding would not hold, so I dropped it.

## Out of scope changes
None. `git status` shows only `hooks/hooks.json`, `scripts/check.sh` (header comment only, as the handoff asked), `scripts/hook-selftest.sh` and the new hook. The untracked `.sdlc/0102-builder-scope-hygiene/*` files are task artifacts. No commits were made.

## For the next attempt
None
