<!-- role=filer level=L1 model=sonnet effort=medium -->
Both steps passed verification. Everything checks out for the filer draft.

## Warnings
None

## PR title
T-0139: Guard the pre-sync wip commit in fanout.py from ever being merged

## PR body
### Summary
A `wip(<id>): dirty before sync` commit that `fanout.py`'s `run_ticket` makes on a lane branch, when the lane tree was already dirty before a ticket's sync, could reach the integration branch if that ticket then merged. That contradicts the documented contract that a `wip(<id>)` commit is never merged. This closes the gap with a guard: when the pre-sync `wip_commit` finds a dirty tree, the ticket now stops with outcome `dirty before sync` before any sync, driver run, lane commit, or merge happens, so that commit can never be merged.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`: `run_ticket` returns `('dirty before sync', 'wip <sha7>')` as soon as the pre-sync `wip_commit` finds a dirty tree, skipping sync/driver/lane-commit/merge for that ticket. Clean-tree path is unchanged. Module docstring updated to describe the new behavior. `selftest()` gained case 8 (`dirty-sync case:`) proving the guard end-to-end plus a negative control (`dirty-sync control:`) proving a clean lane still merges as before.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: line 9 updated to describe the new pre-sync behavior.
- `CLAUDE.md`: the `scripts/fanout.py` bullet's wip sentence rewritten to cover both the stop case and the pre-sync case, stating both commits stay on the lane branch only and are never merged.
- `.claude/agents/sdlc-lite-author.md`: left unchanged (it doesn't describe this behavior).

### How verified
- Step 1 (builder Opus/high, verifier Sonnet/high): verifier reran the end-to-end mktemp fixture from the handoff against the built tree (exit 1, correct report row, correct lane tip commit subject, tip not an ancestor of the integration branch, `dirty.txt` absent from the integration branch, `T-0001.txt` present) and confirmed the check bites by reverting the guard on a throwaway copy and reproducing the original bug (`fanout selftest: FAIL`, T-0002 wrongly merged, `dirty.txt` reaching the integration branch). All other doc/grep acceptance criteria independently re-run and confirmed pass. `.claude/agents/sdlc-lite-author.md` confirmed untouched.
- Step 2 (builder Sonnet/low, verifier Opus/medium): confirmed `plugins/sdlc-lite/scripts/check.sh` and the fanout selftest both green on the built tree, with no fixes needed since step 1 already left both gates green. Verifier proved the guard's bite by mutating a throwaway worktree copy (deleting the new early return) and confirming `check.sh` and the selftest both go red with the expected failure messages, then removed the worktree cleanly.

Both verifier verdicts: pass.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Fixed: a `fanout.py` lane tree already dirty before a ticket's sync now stops that ticket (`dirty before sync`) instead of risking its pre-sync WIP commit being merged into the integration branch.

## Follow-ups
None
