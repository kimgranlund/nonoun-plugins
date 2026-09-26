<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Builders format only the files their step changed and stop only the PIDs they started, with a PreToolUse hook that blocks pattern kills inside role runs (T-0102).

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

## Step 2: Builder scope rules, check.py guard, and docs
level: L2
### Do
Add two numbered rules to `plugins/sdlc-lite/agents/builder.md` after rule 5:
- Run formatters, `--fix` linters, and code generators only on the files this step changed, and pass those paths explicitly (for example `prettier --write <paths>`). Never run a repo-wide `--write` or `--fix`. If the tool writes a file the step did not ask for, restore it.
- Stop only the PIDs you started (save `$!` when you launch a server, then `kill <pid>`). Never run `pkill`, `killall`, or `kill $(pgrep ...)`, because they hit other sessions' processes. `hooks/block-pattern-kill.sh` blocks these in role runs.

The rules must contain the exact phrases `files this step changed` and `PIDs you started`.

In `plugins/sdlc-lite/scripts/check.py`, add a guard that fails when `agents/builder.md` lacks either phrase. Add a negative control, the way the step 3.3 guard does: the guard function run on the text with the phrase removed must flag it, or check.py reports `check.py: builder scope guard negative control not flagged`.

Document the hook:
- Repo-root `CLAUDE.md` Layout gets a `hooks/block-pattern-kill.sh` bullet next to the other hooks, and the `check.sh` command line mentions it.
- `.claude/agents/sdlc-lite-author.md` gets the same.

Do not commit.
### Acceptance criteria
Run these from the repo root:
- `grep -q 'files this step changed' plugins/sdlc-lite/agents/builder.md`
- `grep -q 'PIDs you started' plugins/sdlc-lite/agents/builder.md`
- `grep -q 'files this step changed' plugins/sdlc-lite/scripts/check.py`
- `grep -q 'PIDs you started' plugins/sdlc-lite/scripts/check.py`
- `grep -q 'builder scope guard negative control' plugins/sdlc-lite/scripts/check.py`
- `grep -q 'block-pattern-kill.sh' CLAUDE.md`
- `grep -q 'block-pattern-kill.sh' .claude/agents/sdlc-lite-author.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py "$PWD/plugins/sdlc-lite"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- The verifier observes that the guard bites. In a throwaway worktree under `$SDLC_TMP_WORKTREES` holding the built tree, it deletes the `PIDs you started` phrase from `agents/builder.md` and runs that copy's check.py, which must exit 1 and name `agents/builder.md`.

## Risks
- A command-position regex can miss shapes like `bash -c "pkill ..."` or an alias, or block harmless text. Step 1 fails closed on parse errors, and its fixtures cover the common shapes, but it is a guard, not a sandbox.
- The formatter rule is enforced by prompt only, and check.py only proves the text is present. A builder can still run a repo-wide formatter through a project script such as `npm run format`.
- In fanout, `SDLC_ROLE=conductor` means lane conductors are also blocked from pattern kills. That is intended, but it could surprise a lane that relied on `pkill`.
