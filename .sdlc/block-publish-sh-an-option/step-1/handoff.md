## Task goal
hooks/block-publish.sh scans the raw command whenever an interpreter runs inline code, even when options that take a separate value word (for example `python3 -X dev -c '...'`, `python3 -W ignore -c`, `node --require x -e`, `perl -I lib -e`, `ruby -I lib -e`) come before the inline-code flag, so a publish call inside that code is blocked inside a role run.

## Step 1: Match inline-code flags after value-taking options, with fixtures and docs (gates green)
level: L2
### Do
1. In `plugins/sdlc-lite/hooks/block-publish.sh`, change the masker's `INTERP` regex. Today `OPTS = r'(?:\s+-\S+)*?\s+'` allows only dash words before the inline-code flag, so a separate value word (`dev` in `-X dev`) stops the match. Let each interpreter's option run also take the separate value word of the options that need one:
   - python: `-X`, `-W`, `--check-hash-based-pycs`
   - node: `-r`/`--require`, `--import`, `--loader`/`--experimental-loader`, `-C`/`--conditions`, `--input-type`, `--title`, and other `--flag value` options you find in `node --help`
   - perl: `-I`, `-M`, `-m`, `-x` where a separate value is accepted
   - ruby: `-I`, `-r`, `-C`, `-E`, `-x`, `-W` where a separate value is accepted
   
   Use a per-interpreter list of value-taking options. Do not allow any word between the interpreter and the flag. A non-option word (a script path such as `scripts/check.py`) must still end the option run, so `python3 scripts/check.py -c "..."` keeps the masked scan. The attached forms (`-Xdev`, `--require=x`) keep working. Keep the rest unchanged: the short-option cluster rule (`perl -ne`, `python3 -Sc`), path-qualified interpreters, ruby `-E` not being code, and interpreter words inside quotes being masked away.
2. Update the header comment of the same file (lines 14 to 19) to say that options taking a separate value word (for example `python3 -X dev -c`, `node --require x -e`, `perl -I lib -e`) may come before the inline-code flag. The literal text `-X dev` must appear.
3. In `plugins/sdlc-lite/scripts/hook-selftest.sh`, next to the existing "Interpreter inline code is scanned raw" block, add these fixtures in the same `c=$(printf ...)` / `run "$pub" "$(pj "$c")"` style:
   - Blocked (exit 2): `python3 -X dev -c`, `python3 -W ignore -c`, `node --require x -e`, `perl -I lib -e`, `ruby -I lib -e`, each holding a publish call built with `%s` so the fixture text never holds the literal phrase.
   - Allowed (exit 0): `python3 -X dev scripts/check.py "git <push>"` and `python3 scripts/check.py -c "git <push>"`.
4. In the root `CLAUDE.md` `hooks/block-publish.sh` bullet, extend the interpreter sentence to say that value-taking options before the flag still count, citing `python3 -X dev -c` (the literal `-X dev` must appear on that line). `.claude/agents/sdlc-lite-author.md` does not describe the interpreter rule, so leave it alone unless you add such a description.
5. This is the gates green step. Run `plugins/sdlc-lite/scripts/check.sh` and fix any red this step introduced.
### Acceptance criteria
- `c=$(printf "python3 -X dev -c 'import os; os.system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "python3 -W ignore -c 'import os; os.system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "node --require x -e 'require(\"child_process\").execSync(\"gh %s create\")'" pr); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "perl -I lib -e 'system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "ruby -I lib -e 'system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- (guard) `c=$(printf 'python3 -X dev scripts/check.py "git %s"' push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 0`
- (guard) `c=$(printf 'python3 scripts/check.py -c "git %s"' push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 0`
- `grep -qF -- '-X dev' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF -- '--require' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF -- '-X dev' plugins/sdlc-lite/hooks/block-publish.sh`
- `grep -F 'hooks/block-publish.sh' CLAUDE.md | grep -qF -- '-X dev'`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
