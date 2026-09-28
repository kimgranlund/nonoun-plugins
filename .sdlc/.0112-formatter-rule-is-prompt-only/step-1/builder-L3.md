<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-repo-format.sh` (new, executable): a PreToolUse(Bash) hook that runs only when `SDLC_ROLE` is builder. It has a header comment and uses `jq` to read the command. It exits early when no formatter word appears. A python3 step masks quoted text and splits the command into segments at command positions. It strips wrapper words, then checks each segment against script rules (npm, pnpm, yarn, bun, make) and tool rules (prettier, eslint, black, ruff, gofmt, go fmt, cargo fmt, rustfmt, biome, dprint, stylelint, clang-format). When it cannot analyze the command it falls back to a loose regex scan of the raw text. The stderr message names the role, says "builder rule 6", and shows `prettier --write <paths>` and `npm run format -- <paths>`.
- `plugins/sdlc-lite/hooks/hooks.json`: added a fifth entry for `block-repo-format.sh` under the `Bash` matcher. The other entries are unchanged.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: added a header-comment sentence and `rf="$hooks/block-repo-format.sh"`. Fixtures cover the 11 blocked forms (exit 2, stderr names `builder` and `rule 6`), the 6 allowed forms with builder, and the blocked forms with no role and with `SDLC_ROLE=verifier` (exit 0).

## Checks
All commands were run from the worktree root.
- `test -x plugins/sdlc-lite/hooks/block-repo-format.sh`: exit 0
- `grep -qF block-repo-format.sh plugins/sdlc-lite/hooks/hooks.json`: exit 0
- `jq -e '[... select(test("block-repo-format.sh"))] | length == 1' plugins/sdlc-lite/hooks/hooks.json`: `true`, exit 0
- Loop over the 11 blocked forms with builder: every one exits 2, `test $bad -eq 0` exit 0
- Loop over the 6 allowed forms with builder: every one exits 0, `test $bad -eq 0` exit 0
- Loop over no role, verifier, and conductor with the 3 blocked forms: every one exits 0, `test $bad -eq 0` exit 0
- `... npm run format | SDLC_ROLE=builder bash ...block-repo-format.sh 2>&1 >/dev/null | grep -q "rule 6"`: exit 0
- `grep -qF block-repo-format.sh plugins/sdlc-lite/scripts/hook-selftest.sh`: exit 0
- Bite check (the hook copy outside the tree replaced by `exit 0`, then `! bash "$d/scripts/hook-selftest.sh"`): exit 0. The copy failed with `hook selftest: FAIL: block-repo-format blocks npm run format: exit 0, want 2`.
- `shellcheck --severity=warning plugins/sdlc-lite/hooks/block-repo-format.sh plugins/sdlc-lite/scripts/hook-selftest.sh`: exit 0. A plain `shellcheck` of the new hook also exits 0.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: `hook selftest: PASS`, exit 0
- (guard) `git diff --quiet HEAD -- block-publish.sh block-background.sh block-pattern-kill.sh block-stray-worktree.sh`: exit 0
- Extra manual probes: about 35 more blocked forms, such as `black .`, `ruff check --fix .`, `biome check --write .`, a quoted stylelint glob, `timeout 60 npx prettier --write src`, `sudo pnpm exec eslint --fix .`, `python3 -m black .`, `$(prettier --write .)`, backslash-newline continuation, and a heredoc, all exit 2. About 25 more allowed forms, such as `prettier --check .`, `cargo fmt --check`, `eslint --fix-dry-run .`, a quoted commit message, redirections, and `--config .prettierrc --write a.ts`, all exit 0. With python3 left off PATH, the loose fallback blocks the 10 required forms and allows `npm test`, `ls`, `npm run build`, `prettier --check .`, and `gofmt -l .`.

## Notes
- How file paths are recognized: a target passes when it is an existing file, or when it is not an existing directory and its last path part has an extension (the check never reads package.json or a Makefile). As a result, an extensionless name that does not exist (such as `src`), a `$VAR` or `$(...)` target, a quoted path with spaces, and an unknown option value given as `--opt value` all count as not-a-file and get blocked. Common value-taking options are listed per tool to limit this; the `--opt=value` form always works.
- The fallback scan only runs on a heredoc, a shell or evaluator word, an unterminated quote, or missing python3. It ignores targets, so in those cases explicit file paths are blocked too, and so is prose inside a heredoc that mentions something like `go fmt` or `black`, as the handoff asks.
- `format:check` and other names starting with `format` or `fmt` are blocked as scripts, per the handoff's name rule, even when they only check.
- Beyond the handoff's list, the checks also cover `python -m <tool>`, `npm/yarn exec|dlx`, `bun x`, and `nice`/`exec`/`time` as wrappers. `--check` and `--diff` are treated as check-only modes and pass.
- The session's live hooks load from the main repo's plugin copy, not this worktree, so the new hook did not affect this run's own commands.
- Records (CLAUDE.md, the author agent, builder.md) and the full `scripts/check.sh` belong to step 2 and were not touched or run.
