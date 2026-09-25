<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0058: /fanout command for parallel lanes, with per-lane board view

## PR body
### Summary
Adds `/fanout <lane>=<ids>...`, so ticket lanes can run in parallel without a hand-written driver. Each lane gets its own git worktree and its own headless conductor. Under a lock, each lane merges into an integration branch (`fanout/<date>` by default), and the gates run there. A red gate resets the merge, and tickets close on the integration branch. Main is never touched. The user approves one `git merge --ff-only` of main at the end. The PR also adds `board.py --lanes`, a view with one row per worktree. The default board output does not change.

### Changes
1. **`board.py --lanes`** (step 1, builder L3, verifier L2)
   - Prints `| Lane | Branch | Board |` with one row per `git worktree list` entry. Board is that worktree's `--summary` line for the same relative root.
   - Exits 1 outside a git work tree.
   - Adds selftest case 8, and updates the `/board` skill and CLAUDE.md.
   - Verified:
     - Every criterion passed. The same command at HEAD exits 2, so the criterion can go red.
     - Two mutated copies failed the selftest: one where every row reads the local root, and one that exits 0 outside git.
     - The default board output matches HEAD with no diff.
     - `check.sh` exits 0.
2. **`scripts/fanout.py`** (step 2, builder L4, verifier L3)
   - `run` does the preflight and refusals, `--dry-run`, and setup with rollback. It runs one thread per lane.
   - Before each ticket it syncs the lane from the integration branch under the `fcntl` merge lock. It then commits the lane, merges with `--no-ff`, runs the gates, and resets on red. When the gates are green it closes the ticket.
   - A lane stops at its first outcome other than `merged`. The run writes `report.md` and exits 0, 1, or 2.
   - Includes a `selftest` on throwaway repos with a stub driver, now wired into `check.sh`. CLAUDE.md and the author agent are updated.
   - Verified:
     - The selftest passed on every run. The builder ran it 7 times; the verifier also ran it on its own and inside `check.sh`.
     - The selftest covers three merges, a red merge reset, main unchanged, tickets closed, the sync, a lane stopping and skipping its next ticket, `board.py --lanes` listing both lanes, and dry-run and refusals leaving nothing behind.
     - The verifier broke copies of the script five ways: no reset, no stop, no sync, no close, and always exit 0. It also moved setup ahead of the dry-run return. Every broken copy failed the selftest.
     - The green-lane, red-gate, and dry-run/refusal probes passed as written.
     - This repo has no `fanout/*` branches or fanout worktrees left over.
     - `check.sh` exits 0 on Python 3.9.6.
3. **`/fanout` skill and records** (step 3, builder L2, verifier L1)
   - New `skills/fanout/SKILL.md` with five steps: dry run, confirm with AskUserQuestion, run, report, then an optional ff-only merge of main after approval. It never pushes.
   - Adds a route line to the conductor.
   - Adds the skill to `check.py`'s long-run doc guard.
   - Updates CLAUDE.md and adds an author-agent sync invariant.
   - Verified:
     - Every criterion passed.
     - With `run_in_background` removed from a temp copy of the skill, `check.py` reports it missing, so the long-run guard catches the new skill.
     - `check.sh` exits 0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `/fanout <lane>=<ids>...` (`scripts/fanout.py`). It runs ticket lanes in parallel, with one worktree and one headless conductor per lane. Lanes merge under a lock into an integration branch (`fanout/<date>`), gates run there, and a red gate resets its merge. Main is never touched until you approve a single fast-forward.
- Added `board.py --lanes`, a table with one row per git worktree (lane, branch, board summary). The default board is unchanged.

## Follow-ups
- fanout.py's default lane driver does not set `SDLC_ROLE`, so `hooks/block-publish.sh` does not guard lane conductors against `git push` or `gh` writes. Only the prompt forbids them. Set `SDLC_ROLE` for lane drivers.
