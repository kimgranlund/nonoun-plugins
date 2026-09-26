## Task goal
Inside a role run, `hooks/block-publish.sh` blocks a publish command run through an interpreter's inline-code flag (for example `python3 -c 'import os; os.system("git push")'`, `node -e '...gh pr create...'`, `perl -e`, `ruby -e`), as it did before T-0077, while a plain interpreter run of a script (`python3 scripts/check.py`) and quoted mentions of a publish phrase in non-interpreter commands still pass.

Done when: the hook raw-scans a command in which an interpreter word (at least python, python3, node, perl, ruby, including a path-qualified form like /usr/bin/python3) appears as a command word with an inline-code flag (`-c` for python, `-e`/`-E` for perl/ruby/node, `-p`/`--eval`/`--print` for node); `scripts/hook-selftest.sh` has blocking fixtures for each interpreter and pass fixtures (script run, interpreter with no publish phrase, a quoted mention that is not interpreter code); the hook header comment, CLAUDE.md's block-publish.sh bullet, and `.claude/agents/sdlc-lite-author.md` (if it describes the evaluator list) name the new rule; `scripts/check.sh` is green.

Decision (conductor, unattended, from existing doctrine): extend the fail-closed raw-scan rule, which already covers shell and evaluator words, to interpreter inline code. Scope it to the inline-code flag so ordinary `python3 script.py` runs keep the masked scan and do not gain false positives.

## Step 1: Raw-scan interpreter inline code in block-publish.sh
level: L2
### Do
1. **Hook** (`plugins/sdlc-lite/hooks/block-publish.sh`, masker Python block). After `parse(...)` has built `masked`, check the masked text (not the raw text) for an interpreter command word that has an inline-code flag. If it finds one, `sys.exit(1)` so the hook scans the raw command.
   - Why the masked text: interpreter words inside quotes are already masked away there. So `git commit -m "doc: python3 -c must never git <push>"` still passes.
   - Interpreter words: `python`, `python3`, and versioned forms like `python3.12`; also `node`, `perl`, `ruby`.
   - Command-word boundary: reuse the SHELL_WORD left boundary (`^` or `[\s;&|(`{/]`), so `/usr/bin/python3` counts. Allow `env`/`sudo`-style prefixes naturally.
   - After the word, allow any run of other options (for example `python3 -u -c`). The flag also counts inside a short-option cluster (`perl -ne`, `perl -pe`, `python3 -Sc`).
   - Flags per interpreter: python `-c`; node `-e`, `-p`, `--eval`, `--print`; perl `-e`, `-E`; ruby `-e`. Ruby `-E` is the encoding flag, not code, so do not treat it as inline code.
   - A plain `python3 script.py ...` keeps the masked scan.
   - Rewrite the header comment so it names the new rule, using the phrase "interpreter inline code" and listing the words and flags.
2. **Selftest** (`plugins/sdlc-lite/scripts/hook-selftest.sh`). Build every publish phrase with `printf`, as the file already does.
   - Add one blocking fixture per interpreter, each with its own fail label:
     - `block-publish blocks python3 -c`
     - `block-publish blocks /usr/bin/python3 -c`
     - `block-publish blocks node -e`
     - `block-publish blocks node --eval`
     - `block-publish blocks perl -e`
     - `block-publish blocks ruby -e`
   - Add pass fixtures:
     - `block-publish allows python3 script run`: `python3 scripts/check.py "<phrase>"`
     - `block-publish allows interpreter without publish`: `python3 -c 'print(1)'`
     - `block-publish allows interpreter word in quoted mention`: the commit-message form above
   - Replace the existing fixture `block-publish allows python3 -c string` (`python3 -c 'print("gh pr create")'`, expected exit 0). Under the ticket's decision that is interpreter inline code, and no static check can tell `print(...)` from `os.system(...)`. It becomes the `python3 -c` blocking fixture. This is the one deliberate exception to "existing fixtures keep their outcomes"; every other fixture keeps its outcome.
   - Extend the file's header comment to mention interpreter inline code.
3. **Docs** (repo-root `CLAUDE.md`, the `hooks/block-publish.sh` bullet). Add that the hook also scans raw text when an interpreter (python, python3, node, perl, ruby, path-qualified too) appears as a command word with an inline-code flag, while `python3 script.py` keeps the masked scan. `.claude/agents/sdlc-lite-author.md` does not describe block-publish's evaluator list, so leave it unchanged.
4. **Constraints.** No em dashes anywhere. Run `plugins/sdlc-lite/scripts/check.sh` before finishing.
### Acceptance criteria
- `c=$(printf "python3 -c 'import os; os.system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "/usr/bin/python3 -u -c 'import os; os.system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "cd x && python -c 'import os; os.system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "node -e 'require(\"child_process\").execSync(\"gh %s create\")'" pr); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "node --eval 'require(\"child_process\").execSync(\"gh %s create\")'" pr); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "node -p 'require(\"child_process\").execSync(\"gh %s create\")'" pr); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "node --print 'require(\"child_process\").execSync(\"gh %s create\")'" pr); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "perl -e 'system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "perl -E 'system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "perl -ne 'system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- `c=$(printf "ruby -e 'system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- (guard) `c=$(printf 'python3 scripts/check.py "git %s"' push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null`
- (guard) `c=$(printf 'git commit -m "doc: python3 -c must never git %s"' push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null`
- (guard) `c=$(printf "grep -n 'gh %s create' f" pr); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null`
- (guard) `c=$(printf "python3 -c 'import os; os.system(\"git %s\")'" push); jq -n --arg c "$c" '{tool_input:{command:$c}}' | env -u SDLC_ROLE plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null`
- (guard) `jq -n '{tool_input:{command:"python3 -c \"print(1)\""}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null`
- `grep -qF 'block-publish blocks python3 -c' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'block-publish blocks /usr/bin/python3 -c' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'block-publish blocks node -e' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'block-publish blocks node --eval' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'block-publish blocks perl -e' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'block-publish blocks ruby -e' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'block-publish allows python3 script run' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'block-publish allows interpreter word in quoted mention' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `! grep -qF 'block-publish allows python3 -c string' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qi 'interpreter inline code' plugins/sdlc-lite/hooks/block-publish.sh`
- `sed -n '/hooks\/block-publish.sh/p' CLAUDE.md | grep -qi 'interpreter'`
- (guard) `! git diff HEAD -- plugins/sdlc-lite/hooks/block-publish.sh plugins/sdlc-lite/scripts/hook-selftest.sh CLAUDE.md | grep -q '^+.*—'`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
