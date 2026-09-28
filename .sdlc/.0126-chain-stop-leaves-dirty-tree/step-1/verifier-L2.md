<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass. Evidence: run in the tree, printed `fanout selftest: PASS`, rc=0. The new case can go red (see the pre-change criterion below).
- `grep -qF "wip(" plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: rc=0. The matches are in the helper's commit message, in `run_ticket` and `run_lane`, and in the selftest.
- End-to-end criterion (stub driver `echo x >edit.txt; exit 3`, one lane, one ticket): pass. Evidence: I ran the full command as written and got rc=0. The run printed `[alpha] T-0001 wip 17d2099 on fanout/w-alpha` and `[alpha] T-0001 driver failed rc=3`. The report row was `| alpha | T-0001 | driver failed rc=3 | wip 17d2099 |`. The command can go red: against the pre-change `fanout.py` in a throwaway worktree, its first conjunct (lane tree clean) returned 1.
- The new selftest case fails on the pre-change `run_ticket` and `run_lane`: pass. Evidence: I made a `git worktree add --detach` copy at HEAD and pasted only the case-4 block into that copy's `fanout.py`. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exited rc=1 and named five `wip case:` misses (lane tree clean, tip subject `got 'fixture'`, holds edit.txt, not an ancestor, Commit cell `-`). The integration and main assertions held, which is correct for old code. I removed the worktree and pruned it.
- WIP helper is called on the lane worktree before the sync `git merge --ff --no-edit`, and never touches the integration worktree or the stash: pass. Evidence: `fanout.py:415` calls `wip_commit(wt, ...)` inside `with lock:` and before the `git(wt, 'merge', '--ff', '--no-edit', integration)` that follows. `grep -n "wip_commit\|stash"` finds only the docstring mention at line 393, the definition at 391, and the calls at 415 and 494. Both calls pass the lane dir. The helper uses only `git(wt, ...)`, and no code calls `git stash`.
- `python3 -m py_compile plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: rc=0.
- Behavior details in the Do, checked against the diff and the observed run (the acceptance criteria above pin most of them):
  - The commit message is `wip(<id>): <outcome>`. The helper returns the 7-char sha and returns `''` when the tree is clean or the add or commit fails.
  - `run_lane` calls the helper for any non-merged outcome, so the `error:` path is covered. An existing commit cell is kept (`commit = commit or ...`).
  - The stopped ticket's flow returns before the locked merge, as before.
  - The docstring's `selftest` paragraph lists the new case.

Steelman: I drafted a fail on the builder's note that the pre-sync `wip(...): dirty before sync` commit could end up merged into the integration branch. The rebuttal holds. The handoff's Do asks for that call as written, and its "never merge a `wip(` commit" rule covers only the stopped ticket's flow. That flow still returns before the merge. I dropped the finding.

## Out of scope changes
- None from the builder. The `git diff` for `plugins/` shows only `fanout.py`, which the step named. `.sdlc/0126-chain-stop-leaves-dirty-tree/handoff.md` shows as modified. The diff shows a `## Intent` section appended (clarify output), and the builder reports the file was already modified before its run. Not attributable to this step and harmless (`git diff` on the file).
- The untracked `.sdlc/0126-chain-stop-leaves-dirty-tree/{planner-L2.md,runs.jsonl,step-1/,step-2/}` are chain artifacts, not project files.

## For the next attempt
None
