<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- #1 `python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0, and its case 8c is absent from the pre-change script (red first: it failed with `got []`): pass.
  - Built tree: the selftest printed `board selftest: PASS` with rc=0.
  - Pre-change script: `git show HEAD:plugins/sdlc-lite/scripts/board.py | grep -n "8c\|Uncovered\|uncovered"` gave grep_rc=1, so case 8c is absent there.
  - Red first: I copied the new board.py into a throwaway worktree at base f9474d97 and made `uncovered_merges` return `[]`. The selftest gave nc_rc=1 with `two light merges after the ledger entry are both uncovered, got []`. This matches the stated red.
  - The clear leg also goes red. With the ledger read oldest-first instead of `reversed(lines)`, rc=1 and `a cover entry at the tip clears the uncovered merges, got ['Uncovered light merge T-0101 ...', 'Uncovered light merge T-0102 ...']`.
  - No process-deviations.md exists, so no builder red-checkpoint was recorded. This criterion's red evidence is my own control above.
- #2 `board.py --lanes` output is unchanged when no merge is uncovered or no ledger exists (the case 8 and 8b assertions still pass): pass.
  - The diff only adds case 8c; the 8 and 8b blocks are untouched, and the full selftest passes on the built tree.
  - I diffed the base and new `--lanes --root .sdlc` output on this repo (18 worktree rows, no ledger): diff_real=0.
  - Throwaway fixture repo with no ledger: diff_noledger=0.
  - Same fixture with a `Merge lane1: T-0101` merge whose ledger `to` is the tip: diff_covered=0.
  - Same fixture with the ledger `to` moved to HEAD~1: the new script prints `Uncovered light merge T-0101 beb4ea2 on main ...`. The check discriminates.
- #3 `git diff --check` exits 0; only `board.py` and `docs/references/sdlc-internals.md` changed outside this ticket folder: pass.
  - `git diff --check` gave check=0.
  - `git status --short` shows modified `.sdlc/0482-light-merge-uncovered-board/handoff.md`, `docs/references/sdlc-internals.md` and `plugins/sdlc-lite/scripts/board.py`. The untracked files are all inside the ticket folder.

## Out of scope changes
None.
- `.sdlc/0482-light-merge-uncovered-board/handoff.md` gained `## Acceptance criteria`. It is inside the ticket folder, and solo.md:51 tells the solo agent to write the task handoff's `## Acceptance criteria` if it has none.
- The `MERGE_SUBJECT` regex in board.py matches the subject the merge writes, `Merge {lane.branch}: {t.id}` (fanout.py:1523), and fanout.py:2464 uses the identical regex.
- I found no other consumers of `uncovered_merges` or the new output line outside board.py and sdlc-internals.md.
- Draft concern, dropped: the criteria pin the exact string `Uncovered light merge`, which solo.md:51 says calls for a `verifier: L3` line in the handoff. That rule only picks the verifier level and is not one of the handoff's criteria, so it is not a fail.

## For the next attempt
None
