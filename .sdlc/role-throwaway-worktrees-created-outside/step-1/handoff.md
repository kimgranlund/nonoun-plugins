## Task goal
Inside a role run, a throwaway git worktree created outside `$SDLC_TMP_WORKTREES` (for example under `/tmp`) or created with a new branch (`git worktree add -b`/`-B`) can no longer leave a worktree or branch behind unnoticed: it is blocked before it is created, or detected and reported when the run ends.

Done when: an automated selftest (wired into `scripts/check.sh`) proves that, with `SDLC_ROLE` set, `git worktree add /tmp/x HEAD` and `git worktree add -b tmpbr <path under $SDLC_TMP_WORKTREES> HEAD` are caught (denied or reported), that `git worktree add --detach "$SDLC_TMP_WORKTREES/x" HEAD` still passes, and that nothing changes when `SDLC_ROLE` is unset.

## Step 1: Add the block-stray-worktree hook, wire it, and prove it in hook-selftest.sh
level: L3
### Do
Create `plugins/sdlc-lite/hooks/block-stray-worktree.sh` (executable, `#!/usr/bin/env bash`). Model it on `hooks/block-pattern-kill.sh`: same header-comment style, `[[ -n "${SDLC_ROLE:-}" ]] || exit 0`, read `.tool_input.command` with `jq`, a cheap exit when the text holds no `worktree`, the python3 masker for quoted strings, heredocs and comments, and the same fail-closed raw scan. The raw scan runs when python3 is missing, when a quote is unterminated, when the command holds a heredoc, or when a shell or evaluator (bash, sh, zsh, dash, ksh, fish, eval, ssh, su) is a command word. In the raw scan, any `git ... worktree add` is denied.

Find `git worktree add` in command position. Allow global git options between `git` and `worktree`, such as `git -C <dir> worktree add`. For each hit, deny (exit 2) when any of these holds:
- `-b`, `-B`, or `--orphan` is present, because they create a branch that run.sh's cleanup never deletes.
- `SDLC_TMP_WORKTREES` is empty or unset. A conductor has `SDLC_ROLE` but no prefix.
- The path argument is not under the prefix. Before comparing, expand a literal `$SDLC_TMP_WORKTREES` or `${SDLC_TMP_WORKTREES}` in the path token to the env value and strip surrounding quotes. Resolve a relative path against the hook JSON's `.cwd`, else `$PWD`. Deny a path with a `..` segment. Allowed means equal to `$SDLC_TMP_WORKTREES/<something>` or below it.
- Neither `--detach`/`-d` nor a commit-ish positional follows the path, because `git worktree add <path>` alone creates a branch named after the path.

The stderr message names the role and gives the allowed form: `git worktree add --detach "$SDLC_TMP_WORKTREES/<name>" <commit>`. Allow every other command, including `git worktree list`, `git worktree remove ...`, and a mention inside a quoted argument (`grep -n "git worktree add" f`).

Add it to `plugins/sdlc-lite/hooks/hooks.json` as a fourth command in the `"matcher": "Bash"` group.

In `plugins/sdlc-lite/scripts/hook-selftest.sh`, add a `block-stray-worktree` section. It follows the existing `run`/`pj` pattern with `SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1`.

Denied, exit 2:
- `git worktree add /tmp/x HEAD`
- `git worktree add -b tmpbr "$SDLC_TMP_WORKTREES/x" HEAD`
- `-B` and `--orphan` variants
- `git -C . worktree add /tmp/x HEAD`
- `git worktree add "$SDLC_TMP_WORKTREES/x"` with no commit-ish
- `git worktree add "$SDLC_TMP_WORKTREES/../x" HEAD`
- a `bash -c` wrapper around a stray add
- any add with `SDLC_TMP_WORKTREES` unset

Allowed, exit 0:
- `git worktree add --detach "$SDLC_TMP_WORKTREES/x" HEAD`
- `git worktree add "${SDLC_TMP_WORKTREES}/base" HEAD`
- the literal absolute prefix path
- `git worktree remove --force "$SDLC_TMP_WORKTREES/x"`
- a quoted mention
- `git worktree add /tmp/x HEAD` with `SDLC_ROLE` unset

Also check that the deny stderr names the role. Update the file's header comment to list the new hook. Update the header comment in `plugins/sdlc-lite/scripts/check.sh` (the line listing the hooks the hook selftest covers) to name `block-stray-worktree.sh`. Do not touch `run.sh` cleanup or `fanout.py`.
### Acceptance criteria
- `test -x plugins/sdlc-lite/hooks/block-stray-worktree.sh`
- `printf '%s' '{"tool_input":{"command":"git worktree add /tmp/x HEAD"}}' | env SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 bash plugins/sdlc-lite/hooks/block-stray-worktree.sh; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"git worktree add -b tmpbr \"$SDLC_TMP_WORKTREES/x\" HEAD"}}' | env SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 bash plugins/sdlc-lite/hooks/block-stray-worktree.sh; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"git worktree add --detach \"$SDLC_TMP_WORKTREES/x\" HEAD"}}' | env SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 bash plugins/sdlc-lite/hooks/block-stray-worktree.sh; test $? -eq 0`
- `printf '%s' '{"tool_input":{"command":"git worktree add /tmp/x HEAD"}}' | env -u SDLC_ROLE -u SDLC_TMP_WORKTREES bash plugins/sdlc-lite/hooks/block-stray-worktree.sh; test $? -eq 0`
- `printf '%s' '{"tool_input":{"command":"bash -c \"git worktree add /tmp/x HEAD\""}}' | env SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 bash plugins/sdlc-lite/hooks/block-stray-worktree.sh; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"git worktree add --detach /r/x HEAD"}}' | env -u SDLC_TMP_WORKTREES SDLC_ROLE=conductor bash plugins/sdlc-lite/hooks/block-stray-worktree.sh; test $? -eq 2`
- `jq -e '[.hooks.PreToolUse[] | select(.matcher == "Bash") | .hooks[].command] | any(test("block-stray-worktree"))' plugins/sdlc-lite/hooks/hooks.json`
- `grep -q block-stray-worktree plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -q block-stray-worktree plugins/sdlc-lite/scripts/check.sh`
- `shellcheck --severity=warning plugins/sdlc-lite/hooks/block-stray-worktree.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- A negative control shows the selftest bites. In a throwaway worktree under `$SDLC_TMP_WORKTREES`, make the new hook `exit 0` right after its `SDLC_ROLE` line. `hook-selftest.sh` must then print `hook selftest: FAIL` naming a block-stray-worktree case. Remove the worktree afterwards.
