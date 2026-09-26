## Task goal
Inside a role run, `hooks/block-pattern-kill.sh` also blocks the two pattern-kill forms that pass today (a process list filtered by name piped into `xargs kill`, and a kill word held in a shell variable), without blocking killing a PID the builder saved.

## Step 1: Block ps-fed kills and variable-held kill words in block-pattern-kill.sh
level: L3
### Do
1. Edit `plugins/sdlc-lite/hooks/block-pattern-kill.sh`. Keep the existing structure: cheap exit, strict regex on the masked text, loose regex on the raw text when the masker fails closed. Extend all three:
   - Cheap exit: stop exiting 0 for commands that can hold the new forms. The prefilter must let through a command that holds `ps` together with `kill`, and a command that assigns a value holding pkill, killall, or kill and later expands a variable.
   - Strict (masked) patterns to add:
     - (a) `ps` in command position, followed later in the same pipeline (over any number of `| grep ... | awk ...` stages) by `| xargs [flags] kill`.
     - (b) `kill` whose arguments hold `$(` or a backtick, where `ps` is in command position inside that substitution. Mirror the existing `pgrep` form.
     - (c) A variable assignment `NAME=pkill`, `NAME=killall`, or `NAME=kill` (the value may also be a path ending in one of those), followed in the same command by `$NAME` or `${NAME}` in command position. A regex backreference or a small check in the python masker is fine.
   - Loose (raw) additions: the same forms at word level, e.g. word `ps` ... word `kill`, and `=(pkill|killall|kill)` ... `$`-expansion in command position.
   - Must stay allowed (exit 0): `kill $(cat pidfile)`, `kill $pid`, `kill %1`, `echo $! | xargs kill`, `cmd=ls; $cmd -la`, `pid=$!; kill "$pid"`, plus every existing allowed fixture.
   - Must never be blocked: the criterion commands of this step, run as a verifier's own Bash command under the hook (they build the fixture text with `printf` inside single quotes, which the masker drops).
   - Update the header comment's Blocked and Allowed lists to name the ps-fed forms and the variable-held kill word. Update the `block()` stderr message too if it lists forms. It must still contain `PID` and the role.
2. Edit `plugins/sdlc-lite/scripts/hook-selftest.sh`, in the block-pattern-kill section:
   - Block fixtures (exit 2 with `SDLC_ROLE=builder`): `ps aux | grep x | awk '{print $2}' | xargs kill`, `ps -ef | grep x | awk '{print $2}' | xargs kill -9`, `kill $(ps aux | grep x | awk '{print $2}')`, `p=<pkill>; $p x`, `k=<killall>; ${k} node`. Build the kill-pattern words with the existing `$pkw`/`$kaw` printf variables, as the file already does.
   - Allow fixtures (exit 0): `kill %1`, `kill $(cat pidfile)`, `echo $! | xargs kill`, `cmd=ls; $cmd -la`.
   - Update the file's header comment (lines 9 to 11) to match.
3. Update the block-pattern-kill line in `CLAUDE.md` (Layout, `hooks/block-pattern-kill.sh`) and the matching hazard line in `.claude/agents/sdlc-lite-author.md`. Both must name the `ps`-fed forms and the variable-held kill word.
4. Do not touch block-publish.sh or block-background.sh. Add no dependencies. Do not commit.
### Acceptance criteria
- `c=$(printf '%s aux | grep x | awk %s | xargs kill' ps "'{print \$2}'"); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- `c=$(printf '%s -ef | grep x | awk %s | xargs kill -9' ps "'{print \$2}'"); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- `c=$(printf 'kill $(%s aux | grep x | awk %s)' ps "'{print \$2}'"); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- `c=$(printf 'p=p%s; $p x' kill); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- `c=$(printf 'k=kill%s; ${k} node' all); jq -n --arg c "$c" '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh; test $? -eq 2`
- (guard) `jq -n --arg c 'kill $(cat pidfile)' '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh`
- (guard) `jq -n --arg c 'kill $pid' '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh`
- (guard) `jq -n --arg c 'kill %1' '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh`
- (guard) `jq -n --arg c 'echo $! | xargs kill' '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh`
- (guard) `jq -n --arg c 'cmd=ls; $cmd -la' '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh`
- (guard) `jq -n --arg c 'pid=$!; kill "$pid"' '{tool_input:{command:$c}}' | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh`
- (guard) `c=$(printf 'p=p%s; $p x' kill); jq -n --arg c "$c" '{tool_input:{command:$c}}' | env -u SDLC_ROLE plugins/sdlc-lite/hooks/block-pattern-kill.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- `grep -qF 'xargs kill -9' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF '${k}' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'cat pidfile' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'kill %1' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `head -20 plugins/sdlc-lite/hooks/block-pattern-kill.sh | grep -qw ps`
- `head -20 plugins/sdlc-lite/hooks/block-pattern-kill.sh | grep -qi variable`
- `grep -F 'hooks/block-pattern-kill.sh' CLAUDE.md | grep -qw ps`
- `grep -F 'hooks/block-pattern-kill.sh' CLAUDE.md | grep -qi variable`
- `grep -F 'block-pattern-kill.sh' .claude/agents/sdlc-lite-author.md | grep -qw ps`
- `grep -F 'block-pattern-kill.sh' .claude/agents/sdlc-lite-author.md | grep -qi variable`
- Observable: `git diff --stat HEAD` touches no file under `plugins/sdlc-lite/hooks/` other than `block-pattern-kill.sh`.
