<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Inside a role run (`SDLC_ROLE` set), a new PreToolUse(Bash) hook `hooks/block-stray-worktree.sh` stops any `git worktree add` that would create a branch or place the worktree outside `$SDLC_TMP_WORKTREES`. The hook has selftest fixtures and is wired into `hooks.json` and `scripts/check.sh`. Interactive sessions and fanout.py's own worktree creation are unaffected.

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

## Step 2: Update the records that describe the hooks
level: L1
### Do
Make the records name the new hook and state its rule the way `block-pattern-kill.sh` is described:
- In the repo-root `CLAUDE.md`, add a `hooks/block-stray-worktree.sh` bullet in Layout after the `hooks/block-pattern-kill.sh` bullet. State what it denies and allows and that it fails closed. Note that fanout.py's own worktrees are untouched because they are not Bash tool calls, and that run.sh's EXIT cleanup stays. Add the hook to the hook-selftest list in the Commands "Check everything" line.
- In `.claude/agents/sdlc-lite-author.md`, add it to the check.sh hook-selftest list and to the learned hazards next to the pattern-kill entry.
- Add one clause to `plugins/sdlc-lite/agents/builder.md` rule 5 and `plugins/sdlc-lite/agents/verifier.md` rule 3: a hook denies `-b`/`-B`/`--orphan` and any path outside the prefix.

Keep each file's existing wording otherwise. No em dashes.
### Acceptance criteria
- `grep -q 'hooks/block-stray-worktree.sh' CLAUDE.md`
- `grep -q block-stray-worktree .claude/agents/sdlc-lite-author.md`
- `grep -q -- '--orphan' plugins/sdlc-lite/agents/builder.md`
- `grep -q -- '--orphan' plugins/sdlc-lite/agents/verifier.md`
- `! git diff HEAD -- CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md | grep -q '^+.*—'`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- The hook only sees Bash tool text. A worktree created from inside a script or program the role runs (python, make) gets past it. The ticket allows "blocked or reported", and a run-end report was left out. Attributing worktrees and branches per run is unreliable while lanes share `git worktree list` concurrently, and the constraints forbid touching anything the run did not create.
- Resolving relative paths against `.cwd` misses a `cd x && git worktree add rel HEAD`. Such a path is judged against the hook's cwd, so it may be wrongly allowed or denied. Absolute and `$SDLC_TMP_WORKTREES` forms are the documented ones.
- `check.sh` takes about 3 minutes (fanout selftest), so the Step 2 guard is slow but green at HEAD. Planner and verifier docs still say `git worktree add <tmp> HEAD`. A role that fills `<tmp>` with `/tmp/...` will now be denied, which is the intended behavior and costs one retry.
