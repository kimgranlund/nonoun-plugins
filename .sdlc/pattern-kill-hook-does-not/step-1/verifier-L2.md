<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- C1 `p=$(echo find pkill); $p x` exits 2: pass. Evidence: ran in built tree, rc=2; ran in throwaway worktree at pre-build HEAD (`git worktree add --detach $SDLC_TMP_WORKTREES/base HEAD`), rc=0 (red-then-green confirmed), worktree removed after.
- C2 backtick `echo find pkill` form exits 2: pass. Evidence: built tree rc=2; pre-build worktree rc=0.
- C3 `compgen | grep killall | head -1` form exits 2: pass. Evidence: built tree rc=2; pre-build worktree rc=0.
- C4 `k=$(command -v kill); $k $(pgrep -f vite)` exits 2: pass. Evidence: built tree rc=2; pre-build worktree rc=0.
- (guard) C5 `p=$(command -v pkill); $p x` exits 2: pass. Evidence: built tree rc=2; pre-build worktree also rc=2 (already-passing gate, unbroken).
- (guard) C6 `k=$(which killall); ${k} node` exits 2: pass. Evidence: built tree rc=2; pre-build worktree rc=2.
- (guard) C7 backtick `command -v pkill` form exits 2: pass. Evidence: built tree rc=2; pre-build worktree rc=2.
- (guard) C8 `cmd=$(command -v ls); $cmd -la` exits 0: pass. Evidence: built tree rc=0; pre-build worktree rc=0.
- (guard) C9 backtick `command -v ls` form exits 0: pass. Evidence: built tree rc=0; pre-build worktree rc=0.
- (guard) C10 quoted mention exits 0: pass. Evidence: built tree rc=0; pre-build worktree rc=0.
- (guard) C11 `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: built tree prints `hook selftest: PASS` rc=0; pre-build worktree (old selftest vs old hook) also PASS rc=0 (gate held both sides).
- C12 new fixtures bite (edited selftest fails against pre-step hook): pass. Evidence: ran the exact command from the criterion; output `hook selftest: FAIL: block-pattern-kill blocks 'p=$(echo find pkill); $p x': exit 0, want 2`, rc=0 (i.e. the `!` negation succeeded), matching `test "$rc" -eq 0`.
- C13 hook header comment contains "substitution": pass. Evidence: `sed -n '1,/^[^#]/p' ... | grep -q substitution` rc=0 in built tree, rc=1 (red) in pre-build worktree.
- C14 CLAUDE.md Layout entry contains "substitution": pass. Evidence: same grep, rc=0 built / rc=1 pre-build.
- C15 sdlc-lite-author.md hazard line contains "substitution": pass. Evidence: same grep, rc=0 built / rc=1 pre-build.
- C16 hook-selftest.sh header clause contains "substitution": pass. Evidence: same grep, rc=0 built / rc=1 pre-build.

## Out of scope changes
None. `git status` shows five tracked files modified (`block-pattern-kill.sh`, `hook-selftest.sh`, `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md`, `.sdlc/pattern-kill-hook-does-not/handoff.md`) plus several untracked planner/step artifacts. Checked mtimes: `handoff.md` (21:10:07), `planner-L1.md` (21:09:32), `planner-L3.md`/`step-1/handoff.md`/`step-2/`/`runs.jsonl` (21:43:xx) all predate the builder's edit to `block-pattern-kill.sh` (21:44:41), confirming they are pre-existing planning artifacts the builder did not touch, matching its own note ("`handoff.md` was already modified before this step, and I did not touch it").

## For the next attempt
None.
