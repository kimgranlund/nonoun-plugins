<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - Added the new `wip_commit(wt, tid, outcome)` helper.
  - `run_ticket` now calls it under the lock before the sync `git merge --ff --no-edit`, using the outcome text `dirty before sync`.
  - `run_lane` now calls it after any outcome other than `merged`, including the `error:` exception path. That happens before later tickets are marked `skipped`. It prints `[<lane>] <id> wip <sha7> on <branch>` and fills an empty Commit cell with `wip <sha7>`.
  - Added selftest case 4 (the WIP lane).
  - Added one sentence about case 4 to the `selftest` part of the module docstring.

## Checks
- New selftest case written first and run against the old `run_ticket`/`run_lane`: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exited 1 with 5 "wip case:" misses (tree clean, tip subject, edit.txt, ancestor, report cell).
- Pre-change criterion in a throwaway worktree (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`, only the case-4 block pasted in, 27 insertions): `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exited 1 and named the same 5 "wip case:" misses. The worktree was removed and pruned afterwards.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS, rc=0.
- `grep -qF "wip(" plugins/sdlc-lite/scripts/fanout.py`: rc=0.
- The full end-to-end criterion command, run as written: rc=0. Output showed `[alpha] T-0001 wip f9b861e on fanout/w-alpha` and the report row `| alpha | T-0001 | driver failed rc=3 | wip f9b861e |`.
- `python3 -m py_compile plugins/sdlc-lite/scripts/fanout.py`: rc=0.
- `run_ticket` check (read in code): `wip_commit(wt, ...)` runs inside the first `with lock:` before `git(wt, 'merge', '--ff', '--no-edit', integration)`. The helper runs git only through `git(wt, ...)`, never in the integration worktree, and never calls `git stash`.

## Notes
- For the next step: the pre-sync WIP commit in `run_ticket` stays on the lane branch. If that ticket then finishes and merges, the `wip(<id>): dirty before sync` commit goes into the integration branch as part of the lane merge. The handoff asks for that call as written, and its "never merge a `wip(` commit" rule covers only the stopped ticket, whose flow still returns before the locked merge. In the current flow this path does not trigger: a lane stops at its first non-merged outcome, and every stopped ticket is already WIP-committed in `run_lane`. So it only fires if a lane tree is dirty before its first ticket.
- A stopped outcome whose lane sha already exists (red gate, merge conflict, merge failed) keeps that sha in the Commit cell. The tree there is already committed, so the helper returns `''`.
- The module docstring still says step 2's driver failure leaves "the tree left as is". Step 2 owns the full docstring and doc updates.
- `.sdlc/chain-stop-leaves-dirty-tree/handoff.md` was already modified before this run, and this step did not touch it.
