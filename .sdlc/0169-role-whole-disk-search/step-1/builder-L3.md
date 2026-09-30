<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-disk-scan.sh`: new executable PreToolUse(Bash) hook. It exits 0 when `SDLC_ROLE` is unset and reads `.tool_input.command` with jq. It uses a python3 masker and analyzer: quoted text that gets dropped is replaced by one placeholder word, `"$HOME"` and `"${HOME}"` are kept, and `${VAR}` is normalized to `$VAR`. It fails closed to a raw ERE scan when there is no python3, an unterminated quote, a heredoc, or a shell or evaluator word. On a match it exits 2 with a stderr message that names the role and the bounded-path advice.
- `plugins/sdlc-lite/adapters/claude/hooks.json`: registered the hook in the Bash matcher's list, after `block-repo-format.sh`.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: added the `ds` variable, a header comment for the new hook, and a fixture block. It has 9 blocked cases (the T-0160 repro plus the 8 cases the handoff lists) and 6 allowed cases (including no role). The search phrases are built with printf, and every failure message starts with `block-disk-scan`.
- `plugins/sdlc-lite/scripts/check.sh`: added `block-disk-scan.sh` to the hook list in the header comment.
- `docs/maintenance/claude-hooks.md`: new `## hooks/block-disk-scan.sh` section before the validation paragraph, covering what it blocks, what passes, when it fails closed, where its fixtures are, and that it is Claude-only (Codex roles are not covered).

## Checks
- AC1 to AC15 (the executable bit, the grep and jq registration checks, the docs grep, and the 11 hook invocations for exit 2, exit 0 and the role in stderr): all PASS, each run exactly as written.
- AC16, the negative control (hook stubbed to `exit 0` in a temp copy): PASS. The selftest prints `hook selftest: FAIL: block-disk-scan blocks the T-0160 repro: exit 0, want 2`.
- AC17 (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: `hook selftest: PASS`.
- AC18 (guard) scope diff against `$SDLC_BASE_SHA`: PASS, only the 5 allowed files changed.
- About 70 more hand cases through the hook: all as expected. Blocked: `${HOME}`, `/Users/<name>`, `grep x / -r`, `xargs -I{} grep -r {} /`, `{ find / ...; }`, `fd --search-path=/`, `eval`, and a heredoc followed by a root find. Allowed: `rg / src`, `grep -r / src`, `rg -g '*.py' /`, `find src -exec grep -r x {} \;`, `bash -c "find . -name x"`.
- No-python3 fallback, with PATH holding only jq, grep and tr: `find / -name x` and `rg -l x /` exit 2, while `find .` and `find ~/.claude/plugins` exit 0. A quoted mention also exits 2 on this path, which is the intended fail-closed behavior.
- `git diff --check`: clean. `bash -n` on the hook and the selftest: ok.
- `python3 scripts/check-packaging.py`: PASS. `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: ok.

## Notes
- The handoff left `-maxdepth` open. I chose to block a root search even when it has `-maxdepth`, and the docs say so.
- For grep, rg, ag and fd, the first positional word is treated as the pattern, not a path, unless an option supplies the pattern (`-e`, `-f`, rg `--files`, ag `-g`). So `rg -g '*.py' /` passes, because rg reads that `/` as the pattern.
- For find, only the starting points before the expression are checked, so `find . -path /` passes.
- The full `check.sh` and shellcheck were not run: shellcheck is not installed on this host. Behavior in a live role session is also unproven; the offline selftest is the evidence, as the handoff states.
