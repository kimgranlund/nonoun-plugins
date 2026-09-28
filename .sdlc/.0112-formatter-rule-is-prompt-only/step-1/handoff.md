## Task goal
Inside a builder run, a repo-wide formatter, `--fix` linter, or format script (including one reached through a project script such as `npm run format`) is stopped by code before it runs, so builder rule 6 no longer rests on the prompt alone.

## Step 1: Add the block-repo-format hook, register it, and add selftest fixtures
level: L3
### Do
All paths below are relative to `plugins/sdlc-lite/`.

1. Create `hooks/block-repo-format.sh` and make it executable. Model it on `hooks/block-pattern-kill.sh`:
   - A header comment lists what is blocked and what is allowed.
   - `[[ "${SDLC_ROLE:-}" == builder ]] || exit 0`, so every other role, and any session with no role, passes unchanged.
   - Read the command with `jq -r '.tool_input.command // ""'`.
   - A cheap early exit when no formatter or format-script word appears.
   - A python3 masker that drops quoted mentions, so `grep -n 'npm run format' f` passes.
   - Command-position matching after `^ ; & | ( { \` $(`, optionally behind the wrapper words `sudo`, `env`, `npx`, `pnpm exec`, `yarn`, `bunx`, `command`, `nohup`, `timeout N`, or `VAR=value`.
   - Fail closed, scanning the raw text with a looser word match, when there is a heredoc (`<<`), when a shell or evaluator word (`bash`, `sh`, `zsh`, `dash`, `ksh`, `fish`, `eval`, `ssh`, `su`) is a command word, when a quote is unterminated, or when python3 is missing or errors.
2. Block (exit 2) these forms:
   - (a) A project format script: `npm|pnpm|yarn|bun run <name>`, bare `pnpm|yarn|bun <name>`, or `make <name>`, where the name is `format`, `fmt`, `prettier`, `lint:fix`, `lint-fix`, or `fix`, or starts with `format` or `fmt`. It passes only when the script is followed by explicit file-path arguments (`npm run format -- a.ts`).
   - (b) A known formatter or fixer in write or fix mode whose targets are missing, or are a directory, `.`, or a glob (`**`, `*`, a trailing `/`, `./...`). The tools: prettier `--write`/`-w`, eslint `--fix`, black, ruff `format` and `ruff check --fix`, gofmt `-w`, `go fmt`, `cargo fmt`, rustfmt with no files, biome `format --write`/`check --write`, `dprint fmt`, stylelint `--fix`, `clang-format -i` with a glob.
   - Explicit file paths pass, for example `prettier --write a.ts` and `eslint --fix src/a.ts src/b.ts`.
3. Do not try to work out what a project script actually runs: no reading of package.json or a Makefile.
4. The stderr block message must:
   - name the role;
   - say "builder rule 6";
   - say to run the formatter only on the files this step changed and to pass those paths explicitly (for example `prettier --write <paths>` or `npm run format -- <paths>`).
5. Register the hook in `hooks/hooks.json` as a fifth entry under the existing `Bash` matcher. Leave the other entries as they are.
6. Add fixtures to `scripts/hook-selftest.sh`:
   - a `rf="$hooks/block-repo-format.sh"` variable and a header-comment sentence;
   - blocked with `SDLC_ROLE=builder` (exit 2, stderr names `builder` and `rule 6`): `npm run format`, `pnpm run format`, `yarn run lint:fix`, `make fmt`, `prettier --write .`, `eslint --fix src`, `cargo fmt`, `go fmt ./...`, `npx prettier -w src/`, `cd x && npm run format`, and `bash -c 'npm run format'`;
   - allowed with `SDLC_ROLE=builder` (exit 0): `prettier --write a.ts`, `npm run format -- a.ts`, `npm test`, `eslint --fix src/a.ts src/b.ts`, a quoted mention (`grep -n 'npm run format' f`), and `ls`;
   - allowed with no role and with `SDLC_ROLE=verifier`, for the blocked forms.
7. Do not change `block-publish.sh`, `block-background.sh`, `block-pattern-kill.sh`, `block-stray-worktree.sh`, or their existing fixtures.

Records and the full `check.sh` belong to step 2.

### Acceptance criteria
- `test -x plugins/sdlc-lite/hooks/block-repo-format.sh`
- `grep -qF block-repo-format.sh plugins/sdlc-lite/hooks/hooks.json`
- `jq -e '[.hooks.PreToolUse[] | select(.matcher=="Bash") | .hooks[].command | select(test("block-repo-format.sh"))] | length == 1' plugins/sdlc-lite/hooks/hooks.json`
- `bad=0; for c in "npm run format" "pnpm run format" "yarn run lint:fix" "make fmt" "prettier --write ." "eslint --fix src" "cargo fmt" "go fmt ./..." "npx prettier -w src/" "cd x && npm run format" "bash -c 'npm run format'"; do jq -n --arg c "$c" '{tool_input:{command:$c}}' | env -u SDLC_HEADLESS SDLC_ROLE=builder bash plugins/sdlc-lite/hooks/block-repo-format.sh 2>/dev/null; rc=$?; if [ $rc -ne 2 ]; then bad=1; fi; done; test $bad -eq 0`
- `bad=0; for c in "prettier --write a.ts" "npm run format -- a.ts" "npm test" "eslint --fix src/a.ts src/b.ts" "grep -n 'npm run format' f" "ls"; do jq -n --arg c "$c" '{tool_input:{command:$c}}' | env -u SDLC_HEADLESS SDLC_ROLE=builder bash plugins/sdlc-lite/hooks/block-repo-format.sh 2>/dev/null; rc=$?; if [ $rc -ne 0 ]; then bad=1; fi; done; test $bad -eq 0`
- `bad=0; for r in "" verifier conductor; do for c in "npm run format" "prettier --write ." "cargo fmt"; do jq -n --arg c "$c" '{tool_input:{command:$c}}' | env -u SDLC_HEADLESS -u SDLC_ROLE ${r:+SDLC_ROLE=$r} bash plugins/sdlc-lite/hooks/block-repo-format.sh 2>/dev/null; rc=$?; if [ $rc -ne 0 ]; then bad=1; fi; done; done; test $bad -eq 0`
- `jq -n '{tool_input:{command:"npm run format"}}' | SDLC_ROLE=builder bash plugins/sdlc-lite/hooks/block-repo-format.sh 2>&1 >/dev/null | grep -q "rule 6"`
- `grep -qF block-repo-format.sh plugins/sdlc-lite/scripts/hook-selftest.sh`
- The selftest bites. With the new hook's body replaced by `exit 0` in a copy outside the tree, the selftest fails: `d=$(mktemp -d) && cp -R plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts "$d"/ && printf '#!/usr/bin/env bash\nexit 0\n' > "$d/hooks/block-repo-format.sh" && chmod +x "$d/hooks/block-repo-format.sh" && ! bash "$d/scripts/hook-selftest.sh" >/dev/null 2>&1`
- `shellcheck --severity=warning plugins/sdlc-lite/hooks/block-repo-format.sh plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/hooks/block-publish.sh plugins/sdlc-lite/hooks/block-background.sh plugins/sdlc-lite/hooks/block-pattern-kill.sh plugins/sdlc-lite/hooks/block-stray-worktree.sh`
