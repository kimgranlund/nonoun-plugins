<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Block: `ps aux | grep x | awk '{print $2}' | xargs kill` exits 2: pass. Evidence: the criterion command printed `C1 ok`. At HEAD (throwaway worktree) the same command exits 0 (`base C1 rc=0`), so the check goes red before the change.
- Block: `ps -ef | ... | xargs kill -9` exits 2: pass. Evidence: printed `C2 ok`.
- Block: `kill $(ps aux | grep x | awk '{print $2}')` exits 2: pass. Evidence: printed `C3 ok`. Base HEAD gives `base C3 rc=0`.
- Block: `p=pkill; $p x` exits 2: pass. Evidence: printed `C4 ok`.
- Block: `k=killall; ${k} node` exits 2: pass. Evidence: printed `C5 ok`. Base HEAD gives `base C5 rc=0`.
- (guard) `kill $(cat pidfile)`, `kill $pid`, `kill %1`, `echo $! | xargs kill`, `cmd=ls; $cmd -la`, `pid=$!; kill "$pid"` allowed under `SDLC_ROLE=builder`: pass. Evidence: a `run` loop printed `rc=0` for all six.
- (guard) `p=pkill; $p x` with `SDLC_ROLE` unset: pass. Evidence: `unset rc=0`.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: `hook selftest: PASS`. The diff shows the 5 new block and 4 new allow fixtures.
- (guard) `plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: `rc=0` from check.sh itself, redirected to a file. The tail shows `ok: shellcheck` and `ok: plugin validate`, and `grep -i fail | grep -vi '^ok'` on the output was empty.
- Selftest greps `xargs kill -9`, `${k}`, `cat pidfile`, `kill %1`: pass. Evidence: `greps ok`.
- `head -20` of the hook contains `ps` and `variable`: pass. Evidence: `head ok`.
- CLAUDE.md `block-pattern-kill.sh` line contains `ps` and `variable`: pass. Evidence: `claude ok`, and the diff shows the line.
- `sdlc-lite-author.md` line contains `ps` and `variable`: pass. Evidence: `author ok`, and the diff shows the line.
- Observable: `git diff --stat HEAD` touches no other file under `plugins/sdlc-lite/hooks/`: pass. Evidence: `git diff --stat HEAD -- plugins/sdlc-lite/hooks/` lists only `block-pattern-kill.sh`.
- Stays allowed, and the criterion commands are never blocked when run under the hook as `SDLC_ROLE=verifier` (Do section, not a listed criterion): pass. Evidence: I ran the criterion commands as my own Bash calls under the live hook, and the printf/jq forms all ran. One combined command of mine was denied, which I traced to the `bash ...` command word triggering the designed fail-closed raw scan. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` run alone passes.

## Out of scope changes
None. The changed files are `plugins/sdlc-lite/hooks/block-pattern-kill.sh`, `plugins/sdlc-lite/scripts/hook-selftest.sh`, `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`, all named in the step. `.sdlc/pattern-kill-hook-misses-forms/handoff.md`, `planner-L2.md` and `runs.jsonl` are the task's own artifacts, and the builder notes the handoff was already modified before the step started. `block-publish.sh` and `block-background.sh` are untouched.

## For the next attempt
None
