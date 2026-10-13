<!-- role=solo level=L1 model=sonnet effort=high -->
## Output
🟢 T-0538 is done: verifier briefs and the verifier role now state the header rule, and a new hook makes `rm` under the tmp prefix agree with the brief. I did not commit.

**Header rule.** `results.py validate` has a new `--headerless` flag that needs `--role`. The verifier brief's Report file line (in `dispatch.py`) now says to write no header, that `dispatch.py record` adds it, and to validate with `--role verifier --headerless`. `agents/verifier.md` and the generated `verifier-L1`/`L2`/`L3` agents and Codex toml files carry the same single statement.

**Tmp cleanup.** Reproduced: no existing hook refuses `rm` under the tmp prefix. Every hook exits 0 on those commands, so the denial in maison T-0546 observation 40 came from the host permission layer. I added `hooks/block-role-rm.sh` and registered it in `adapters/claude/hooks.json`:
- It applies to read-only roles only.
- `rm`, `rmdir` and `unlink` of a path under the prefix pass. When the command is only `rm` and `cd`, the hook also prints an explicit `allow` decision, which is meant to settle the host prompt.
- Any path outside the prefix, the prefix itself, `..`, `~`, an unreadable variable, or a relative path after an unreadable `cd` is denied.
- The prefix line in the dispatch brief now says rm is allowed there and refused elsewhere.
- I did not run it live. Whether the allow decision actually overrides the host prompt is untested.

**Docs.** `docs/references/claude-hooks.md` has a new `block-role-rm.sh` section, and the hook lists in the `_role.sh` and `check.sh` comments name it.

**Checks:**
- `results.py selftest`: PASS. New cases cover headerless pass, headerless still failing the key and value rules, a missing `--role`, a mismatched header, the no-flag negative control, and the CLI flag.
- `hook-selftest.sh`: PASS. The new cases cover rm under the prefix allowed and outside refused, both for `SDLC_TMP_WORKTREES` and for the sub-agent toplevel prefix, plus the allow decision, no-prefix denial, and other roles untouched. A copy of the plugin with the hook stubbed to `exit 0` failed with `denies 'rm /etc/passwd': exit 0, want 2`, so the new cases do catch a hook that allows everything.
- `dispatch.py selftest`: PASS, including new brief assertions.
- `check.py`, `claude_roles.py generate --check`, `codex_roles.py generate --check`, `codex-selftest.py`, `check-packaging.py` and `git diff --check`: pass. `prompt_lint.py` reports 0 errors and 9 warnings.

The ticket has no `(red)` criteria and its level is L1, so there was no `specgate.py red` run and no verifier. Nothing is left open. One thing to know: the hook now refuses a read-only role's `rm` of anything outside its prefix, such as `/tmp` scratch, which no hook refused before.

Files changed:
- `plugins/sdlc-lite/scripts/results.py`
- `plugins/sdlc-lite/scripts/dispatch.py`
- `plugins/sdlc-lite/scripts/hook-selftest.sh`
- `plugins/sdlc-lite/scripts/check.sh`
- `plugins/sdlc-lite/hooks/block-role-rm.sh` (new)
- `plugins/sdlc-lite/hooks/_role.sh`
- `plugins/sdlc-lite/adapters/claude/hooks.json`
- `plugins/sdlc-lite/agents/verifier.md`
- `plugins/sdlc-lite/agents/verifier-L1.md`, `verifier-L2.md`, `verifier-L3.md`
- 6 `plugins/sdlc-lite/adapters/codex/agents/sdlc-verifier-*.toml` files
- `docs/references/claude-hooks.md`
