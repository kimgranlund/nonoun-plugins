<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0126: WIP-commit a stopped fanout lane so the next sync merge is never blocked

## PR body
### Summary
When a fanout lane's driver stopped mid-step (for example a nonzero exit), the builder's uncommitted edits stayed in the lane worktree. A later `git merge --ff --no-edit <integration>` in that lane then refused with "commit your changes before you merge". `fanout.py` now commits a stopped lane's work as `wip(<id>): <outcome>` on the lane branch only, so the tree is clean after any stop.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - New `wip_commit(wt, tid, outcome)` helper. It runs only in the lane worktree. It returns `''` when the tree is clean or the add or commit fails, and otherwise returns the 7-char sha of a `wip(<id>): <outcome>` commit. It never touches the integration worktree, main, or the stash.
  - `run_lane` calls it after any outcome other than `merged`, including the `error:` path, before later tickets are marked `skipped`. The report's Commit cell shows `wip <sha7>` when it was empty, and an existing lane sha is kept. The outcome text, the `skipped` marking, and exit code 1 are unchanged. It prints `[<lane>] <id> wip <sha7> on <branch>`.
  - `run_ticket` calls it under the lock before the sync `git merge --ff --no-edit`, so an already-dirty lane tree is committed instead of failing the sync.
  - The stopped ticket's flow still returns before the locked merge, so a stopped ticket's `wip(` commit is never merged.
  - New selftest case 4 (a stub driver writes a file and exits nonzero).
- Docs updated to say where stopped work lands: the `fanout.py` module docstring, `skills/fanout/SKILL.md`, `skills/chain/SKILL.md`, and the `scripts/fanout.py` bullet in `CLAUDE.md`.
- Builder no-commit rule and the conductor's "never commit" prompt are unchanged. The script commits, not the driver. Nothing commits on main or the integration branch.

### How each was verified
- Step 1 (verifier L2, pass):
  - Case 4 was written first and went red on the old code with 5 `wip case:` misses. The verifier reproduced this in a throwaway `git worktree` at HEAD with only the case-4 block pasted in.
  - `python3 plugins/sdlc-lite/scripts/fanout.py selftest` passes, and `py_compile` is clean.
  - An end-to-end fixture run (stub driver `echo x >edit.txt; exit 3`) gave a clean lane tree and a `wip(T-0001): driver failed rc=3` tip holding `edit.txt`. The lane branch was not an ancestor of the integration branch, and the integration branch still equalled main. The report row was `| alpha | T-0001 | driver failed rc=3 | wip <sha7> |`.
  - The code read confirms `wip_commit` runs before the sync merge, only through `git(wt, ...)`, with no `git stash`.
- Step 2 (verifier L1, pass):
  - Each doc criterion was green on the built tree and red at HEAD.
  - The no-em-dash diff check was shown to bite with a planted `—`.
  - The fanout selftest went red on a planted miss.
  - `plugins/sdlc-lite/scripts/check.sh` exited 0 on the built tree.

## Changelog entry
- fanout: a lane that stops after its driver ran (nonzero exit or any outcome other than `merged`) now commits its uncommitted work as `wip(<id>): <outcome>` on the lane branch, and a dirty lane tree is WIP-committed before each sync. The commit is never merged, and the report's Commit cell shows `wip <sha>`. The next sync merge no longer fails with "commit your changes before you merge".

## Follow-ups
- Pre-sync `wip(<id>): dirty before sync` commit in `fanout.py` `run_ticket` would be merged into the integration branch if that ticket then merges. It is unreachable today, but a lane with a dirty tree before its first ticket would trigger it; decide whether to guard or drop that commit from the merge.
