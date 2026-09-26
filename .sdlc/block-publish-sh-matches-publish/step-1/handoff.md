## Task goal
Inside a role run, `hooks/block-publish.sh` blocks only commands that would actually publish, so a Bash call that merely writes or edits text containing a publish phrase (a heredoc body into a file, a quoted argument to `sed`, `python3 -c`, `printf`, `grep`, a commit message) is no longer blocked, while every real publish, including one fed to a shell, stays blocked.

## Step 1: Mask heredoc bodies and quoted strings in block-publish.sh, with selftest cases and doc line
level: L3
### Do
1. Edit `plugins/sdlc-lite/hooks/block-publish.sh`. Keep these as they are today:
   - the `SDLC_ROLE` early exit
   - the `jq` extraction
   - the publish `pattern`
   - the exit contract: 0 allow, 2 block, one stderr message

2. Before the `grep`, build a masked copy of `$cmd` and match the pattern against it. The masked copy has:
   - heredoc bodies removed, for `<<WORD`, `<<'WORD'`, `<<"WORD"` and `<<-WORD`, up to the terminator line
   - single-quoted contents removed
   - double-quoted contents removed, except for any `$(...)` or backtick substitution inside the double quotes, which stays as scannable text

   Replace masked text with nothing or a neutral letter. Never insert `|`, `;` or `&`, because the `gh api` branch of the pattern stops at those.

   You may do the masking with a small `python3` scanner embedded in the hook (python3 is already a plugin dependency: every `scripts/*.py`) or with bash/awk. Do not use `shlex`: it does not understand heredocs.

3. The hook must fail closed. Scan the raw, unmasked `$cmd`, which is today's behavior, in each of these cases:
   - The masker errors or python3 is missing.
   - The command has an unterminated quote or heredoc.
   - The command contains a shell or evaluator as a command word anywhere, such as at the start or after `;`, `&`, `|`, `(`, `&&`, `||`, `$(` or whitespace. The words are `bash`, `sh`, `zsh`, `dash`, `ksh`, `eval`, `xargs`, `ssh`, `source`, `.` and `env`.

   The third rule is coarse on purpose. It keeps these blocked: `bash -c "..."`, `sh -c '...'`, `bash <<EOF`, `cat <<EOF | sh`, `eval "..."` and `ssh host "..."`.

4. Update the header comment to say what is masked and when the hook falls back to the raw text.

5. In `plugins/sdlc-lite/scripts/hook-selftest.sh`, add `run "$pub" ...` cases for both directions. Always build publish phrases with `printf '... %s ...' push` (or `pr`, `publish`, `POST`) as the existing push case does. Never write a publish phrase literally, because the hook guards Bash calls in role sessions.
   - Allowed (exit 0, `SDLC_ROLE=builder`):
     - `cat > f <<'EOF'` with the body line `git push origin main`
     - `sed -i 's/x/git push/' f`
     - `python3 -c 'print("gh pr create")'`
     - `git commit -m "doc: never git push"`
     - `grep -n "npm publish" f`
   - Blocked (exit 2):
     - `git push origin main`
     - `cd x && git push`
     - `bash -c "git push"`
     - `sh -c 'gh pr create'`
     - `bash <<EOF` with the body `git push`
     - `echo "$(git push)"`
     - a backtick substitution inside double quotes
     - `eval "git push"`
     - `gh api -X POST repos/o/r/issues`
     - `npm publish`
     - `cat <<EOF | sh` with the body `gh pr create`
     - `ssh host "git push"`
     - an unterminated quote around `git push` (fail closed)

   Build the JSON with `jq -n --arg c "$c" '{tool_input:{command:$c}}'` so newlines and quotes are escaped correctly. Update the file's header comment to match.

6. In repo-root `CLAUDE.md`, extend the Layout bullet for `hooks/block-publish.sh`. Say that it matches after masking heredoc bodies and quoted string contents, and that it scans the raw text when a shell or evaluator (such as `bash`, `sh`, `eval`, `xargs` or `ssh`) is present or when parsing fails. The line must contain the word `heredoc`. `.claude/agents/sdlc-lite-author.md` line 16 does not describe matching, so leave it alone.

7. Do not change the list of publish commands. Do not commit.
### Acceptance criteria
- `c=$(printf 'cat > f <<%s\ngit %s origin main\nEOF\n' "'EOF'" push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh`
- `c=$(printf "sed -i 's/x/git %s/' f" push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh`
- `c=$(printf "python3 -c 'print(\"gh %s create\")'" pr) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh`
- `c=$(printf 'git commit -m "doc: never git %s"' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh`
- `c=$(printf 'grep -n "npm %s" f' publish) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh`
- (guard) `c=$(printf 'git %s origin main' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'cd x && git %s' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'bash -c "git %s"' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf "sh -c 'gh %s create'" pr) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'bash <<EOF\ngit %s\nEOF\n' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'echo "$(git %s)"' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'eval "git %s"' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'gh api -X %s repos/o/r/issues' POST) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'npm %s' publish) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'cat <<EOF | sh\ngh %s create\nEOF\n' pr) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'ssh host "git %s"' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'git log | xargs git %s' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'ls | (git %s origin main)' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh; test $? -eq 2`
- (guard) `c=$(printf 'git %s' push) && jq -n --arg c "$c" '{tool_input:{command:$c}}' | env -u SDLC_ROLE plugins/sdlc-lite/hooks/block-publish.sh`
- `test "$(grep -c 'run "$pub"' plugins/sdlc-lite/scripts/hook-selftest.sh)" -ge 20`
- The new selftest fails against the base hook: `t=$(mktemp -d) && mkdir "$t/hooks" "$t/scripts" && git show HEAD:plugins/sdlc-lite/hooks/block-publish.sh > "$t/hooks/block-publish.sh" && cp plugins/sdlc-lite/hooks/block-background.sh "$t/hooks/" && cp plugins/sdlc-lite/scripts/hook-selftest.sh "$t/scripts/" && chmod +x "$t/hooks/"*.sh && ! bash "$t/scripts/hook-selftest.sh"`
- `grep -n 'hooks/block-publish.sh' CLAUDE.md | grep -qi heredoc`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `shellcheck plugins/sdlc-lite/hooks/block-publish.sh plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- Observable: running `git diff --stat HEAD` shows changes only in `plugins/sdlc-lite/hooks/block-publish.sh`, `plugins/sdlc-lite/scripts/hook-selftest.sh` and `CLAUDE.md` (plus `.sdlc/` artifacts), and no commit was made (HEAD is unchanged).
