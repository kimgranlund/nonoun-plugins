## Task goal
A role cannot stall its run on a search of the whole filesystem, and a test that failed before the fix passes after it.

## Step 1: Add block-disk-scan.sh hook with fixtures, registration, and docs
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add a new PreToolUse(Bash) hook at `plugins/sdlc-lite/hooks/block-disk-scan.sh` and make it executable. Model it on `plugins/sdlc-lite/hooks/block-pattern-kill.sh`:
- It exits 0 at once when `SDLC_ROLE` is unset or empty.
- It reads `.tool_input.command` with `jq`.
- It masks quoted contents, heredoc bodies, and comments through the same small python3 masker. A command that only mentions the phrase, such as `grep -n "find /" f`, passes.
- It fails closed and scans the raw text when python3 is missing, a quote is unterminated, a heredoc is present, or a shell or evaluator word (`bash`, `sh`, `zsh`, `eval`, `ssh`, `su`, ...) appears as a command word.
- On a match it exits 2. Its stderr names the role (`$SDLC_ROLE`), says that searching the whole filesystem or home folder can run for many minutes with no output (`| head` does not stop it when nothing matches), and tells the role to search a bounded path instead: the repository, a named subfolder such as `~/.claude/plugins`, or `$CLAUDE_PLUGIN_ROOT`.

What to block (a search command in command position, optionally behind `sudo`, `command`, `env`, `nohup`, `timeout N`, `xargs`, or a `VAR=value` assignment):
- The commands are `find`, `bfs`, `fd`, `fdfind`, `rg`, `ag`, `grep` or `egrep` with `-r`/`-R`/`--recursive`, `du`, `ls -R`, and `tree`.
- A match is one of those commands with a path operand that is exactly one of: `/`, `/*`, `~`, `~/`, `$HOME`, `${HOME}`, `$HOME/`, `/Users`, `/home`, `/Volumes`, `/System`, `/Library`, `/private`, or `/Users/<one name>` / `/home/<one name>` (a home folder itself).
- After masking, `"$HOME"` must still read as `$HOME`, so keep double-quoted strings that hold only `$VAR`/`${VAR}`, as block-pattern-kill does.

Must pass:
- A path below those roots, such as `/tmp/x`, `~/.claude/plugins`, `"$HOME/.claude/plugins"`, or `/Users/me/Projects/x`.
- `find .` and relative paths.
- `ls /` without `-R`.
- Quoted mentions.
- Anything with no role.

Allowing a root search that has `-maxdepth` is the builder's choice; no criterion pins it.

Register the hook in `plugins/sdlc-lite/adapters/claude/hooks.json`, in the `Bash` matcher's hook list, after `block-repo-format.sh`. Never create a shared `hooks/hooks.json`.

In `plugins/sdlc-lite/scripts/hook-selftest.sh`, add a variable for the new hook and a fixture block with these cases:
- Blocked with exit 2, with stderr naming the role: the T-0160 repro `find / -name quick_validate.py -path "*skill*" 2>/dev/null | head -3`, plus `bfs / -name x`, `find ~ -name x`, `find "$HOME" -name x`, `find /Users -name x`, `rg -l x /`, `grep -r x ~`, `sudo find / -name x`, and a `bash -c` wrapper around a root find.
- Allowed with exit 0: `find . -name x`, `find /tmp/x -name y`, `find ~/.claude/plugins -name x`, `ls /`, a quoted mention, and a root find with no `SDLC_ROLE`.
- Every failure message starts with `block-disk-scan` (for example `fail "block-disk-scan blocks ...: exit $rc, want 2"`).
- Build the search phrases with `printf`, so the selftest file never holds a root search as a command, as it already does for publish and kill words.
- Extend the header comment to describe the new hook.

Update the hook list in the header comment of `plugins/sdlc-lite/scripts/check.sh`.

Add a `## hooks/block-disk-scan.sh` section to `docs/references/claude-hooks.md`, before the closing validation paragraph. Use the same shape as the other hook sections: what it blocks, what passes, when it fails closed, and where its fixtures are. State that it is Claude-only and that Codex roles are not covered by it.

Do not run formatters repo-wide. shellcheck is not installed on this host, so check.sh skips it; the runtime behavior in a live role session is not proven by this step (the offline selftest is the evidence).
### Acceptance criteria
- `test -x plugins/sdlc-lite/hooks/block-disk-scan.sh`
- `grep -qF block-disk-scan.sh plugins/sdlc-lite/adapters/claude/hooks.json`
- `jq -e '.hooks.PreToolUse[] | select(.matcher=="Bash") | .hooks[] | select(.command | contains("block-disk-scan.sh"))' plugins/sdlc-lite/adapters/claude/hooks.json`
- `grep -qF "block-disk-scan.sh" docs/references/claude-hooks.md`
- `jq -n --arg c 'find / -name quick_validate.py -path "*skill*" 2>/dev/null | head -3' '{tool_input:{command:$c}}' | SDLC_ROLE=planner plugins/sdlc-lite/hooks/block-disk-scan.sh 2>/dev/null; test $? -eq 2`
- `jq -n --arg c 'bfs / -name x' '{tool_input:{command:$c}}' | SDLC_ROLE=planner plugins/sdlc-lite/hooks/block-disk-scan.sh 2>/dev/null; test $? -eq 2`
- `jq -n --arg c 'find ~ -name x' '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-disk-scan.sh 2>/dev/null; test $? -eq 2`
- `jq -n --arg c 'find "$HOME" -name x' '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-disk-scan.sh 2>/dev/null; test $? -eq 2`
- `jq -n --arg c 'rg -l x /' '{tool_input:{command:$c}}' | SDLC_ROLE=scout plugins/sdlc-lite/hooks/block-disk-scan.sh 2>/dev/null; test $? -eq 2`
- `out=$(jq -n --arg c 'find / -name x' '{tool_input:{command:$c}}' | SDLC_ROLE=planner plugins/sdlc-lite/hooks/block-disk-scan.sh 2>&1 >/dev/null); printf '%s\n' "$out" | grep -q planner`
- `jq -n --arg c 'find . -name x' '{tool_input:{command:$c}}' | SDLC_ROLE=planner plugins/sdlc-lite/hooks/block-disk-scan.sh; test $? -eq 0`
- `jq -n --arg c 'find ~/.claude/plugins -name x' '{tool_input:{command:$c}}' | SDLC_ROLE=planner plugins/sdlc-lite/hooks/block-disk-scan.sh; test $? -eq 0`
- `jq -n --arg c 'find /tmp/x -name y' '{tool_input:{command:$c}}' | SDLC_ROLE=planner plugins/sdlc-lite/hooks/block-disk-scan.sh; test $? -eq 0`
- `jq -n --arg c 'grep -n "find / -name x" notes.md' '{tool_input:{command:$c}}' | SDLC_ROLE=planner plugins/sdlc-lite/hooks/block-disk-scan.sh; test $? -eq 0`
- `jq -n --arg c 'find / -name x' '{tool_input:{command:$c}}' | env -u SDLC_ROLE plugins/sdlc-lite/hooks/block-disk-scan.sh; test $? -eq 0`
- The selftest fails without the hook. This negative control copies the hooks and scripts to a temp dir, stubs the new hook to `exit 0`, and expects a `block-disk-scan` failure: `t=$(mktemp -d) && cp -R plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts "$t"/ && printf "#!/usr/bin/env bash\nexit 0\n" > "$t/hooks/block-disk-scan.sh" && chmod +x "$t/hooks/block-disk-scan.sh" && out=$(bash "$t/scripts/hook-selftest.sh"); rm -rf "$t"; printf "%s\n" "$out" | grep -q "FAIL: block-disk-scan"`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/hooks/block-disk-scan.sh|plugins/sdlc-lite/adapters/claude/hooks.json|plugins/sdlc-lite/scripts/hook-selftest.sh|plugins/sdlc-lite/scripts/check.sh|docs/references/claude-hooks.md" | { ! grep -q .; }`
