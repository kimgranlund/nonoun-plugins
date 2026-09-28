<!-- role=planner level=L1 model=sonnet effort=medium -->
Good, parses cleanly. Now composing the final plan.

## Goal
Make `plugins/sdlc-lite/hooks/block-pattern-kill.sh` block a kill word that reaches a command through a variable holding a command substitution (`$(...)` or backtick), while a substitution holding an unrelated command (`cmd=$(command -v ls); $cmd -la`) still passes, and keep the docs and fixtures that describe the hook accurate.

## Step 1: Catch a kill word assigned through a command substitution
level: L3
### Do
In `plugins/sdlc-lite/hooks/block-pattern-kill.sh`, extend the name-extraction the `held_kill`/`assign` mechanism uses so a variable assigned from a `$(...)` or backtick substitution whose body contains a bare `pkill`, `killall`, or `kill` token anywhere inside (not only as the immediate next bare word after a recognized wrapper like `command -v` or `which`, which is the only case the current `assign`/`cp` regex happens to reach) is treated the same as a direct `NAME=pkill` assignment: if `$NAME`/`${NAME}` is later used in command position, block. Verified gaps on the current tree that must become red→green: `p=$(echo find pkill); $p x`, `` p=`echo find pkill`; $p x ``, and `k=$(compgen -c | grep killall | head -1); ${k} node`. Keep `cmd=$(command -v ls); $cmd -la` and the ticket's two named examples (`p=$(command -v pkill); $p x`, `k=$(which killall); ${k} node`, and their backtick form) passing/blocking exactly as today — those are already correctly handled by the existing regex and must not regress. Add matching fixtures to `plugins/sdlc-lite/scripts/hook-selftest.sh` (following its existing `printf`-built-word convention, e.g. `pkw=$(printf 'p%s' kill)`, so the file never holds a kill word literally), for both the new block forms and a pass fixture using an unrelated command inside the substitution. Update the header comment in `block-pattern-kill.sh`, the `block-pattern-kill.sh` line in the repo-root `CLAUDE.md`, and the matching line in `.claude/agents/sdlc-lite-author.md` to mention the substitution form. Every existing fixture keeps its current result.
### Acceptance criteria
- `pk=$(printf 'p%s' kill); json="$(python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "p=\$(echo find ${pk}); \$p x")"; rc=$(SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh <<< "$json" >/dev/null 2>&1; echo $?); test "$rc" -eq 2`
- `pk=$(printf 'p%s' kill); json="$(python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "p=\`echo find ${pk}\`; \$p x")"; rc=$(SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh <<< "$json" >/dev/null 2>&1; echo $?); test "$rc" -eq 2`
- `ka=$(printf 'kill%s' all); json="$(python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "k=\$(compgen -c | grep ${ka} | head -1); \${k} node")"; rc=$(SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh <<< "$json" >/dev/null 2>&1; echo $?); test "$rc" -eq 2`
- (guard) `pk=$(printf 'p%s' kill); json="$(python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "p=\$(command -v ${pk}); \$p x")"; rc=$(SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh <<< "$json" >/dev/null 2>&1; echo $?); test "$rc" -eq 2`
- (guard) `ka=$(printf 'kill%s' all); json="$(python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "k=\$(which ${ka}); \${k} node")"; rc=$(SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh <<< "$json" >/dev/null 2>&1; echo $?); test "$rc" -eq 2`
- (guard) `pk=$(printf 'p%s' kill); json="$(python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "p=\`command -v ${pk}\`; \$p x")"; rc=$(SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh <<< "$json" >/dev/null 2>&1; echo $?); test "$rc" -eq 2`
- (guard) `json="$(python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' 'cmd=$(command -v ls); $cmd -la')"; rc=$(SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-pattern-kill.sh <<< "$json" >/dev/null 2>&1; echo $?); test "$rc" -eq 0`
- `grep -qF 'echo find' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF 'compgen' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `git diff --quiet HEAD -- plugins/sdlc-lite/hooks/block-pattern-kill.sh && exit 1; test $? -eq 1`

## Step 2: Gates green
level: L1
### Do
Run `plugins/sdlc-lite/scripts/check.sh` (which runs `hook-selftest.sh`, shellcheck, and `claude plugin validate` among its other selftests) and fix any red it turns up from step 1's change, including any doc-guard mismatch.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
The current regex catches the ticket's two named examples (`p=$(command -v pkill); $p x`, `k=$(which killall); ${k} node`) already, by coincidence of its generic wrapper/flag matching rather than by design — confirmed by direct testing against the current tree. Step 1 keeps those as guards and targets the real remaining gap (a substitution body with an intervening bare word or a pipe before the kill word), so the fix generalizes past the two named forms rather than special-casing them. The masker's raw-text fallback path (triggered by a heredoc or a shell/evaluator word in the scanned command) is not covered by a dedicated criterion here; if the builder's fix only touches the masked-scan path, a substitution-held kill word inside a heredoc-shaped command could still slip through that fallback, which the Do should keep in mind but which is out of this ticket's named scope.
