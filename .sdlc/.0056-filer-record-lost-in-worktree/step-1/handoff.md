## Task goal
close on main finds the filer record of work done in a lane worktree.

## Step 1: Failing selftest, then the hint in close
level: L2
### Do
In `plugins/sdlc-lite/scripts/tickets.py`:
1. Add a selftest case to the worktree section (the block that uses `m_root` and `w_root`, before the `n_root` zeta case). `filer(..., slug=...)` writes into whatever root it is given.
   - Create a fresh ticket in `m_root` (for example `eta`), then commit it so `wt` sees it. Or reuse a slug that exists in both trees, such as `beta`, if it is already in `wt`. The repro needs `<slug>/handoff.md` in both trees, and the id floor must stay consistent for the later `zeta` id assertion.
   - Write `filer('filer-L1.md', 'None', 'None', slug=<slug>)(w_root)` only in the other worktree.
   - Run `run(m_root, 'close', (<slug>,))`.
   - Snapshot the tree before and after. Assert `rc == 1`, that the snapshot is unchanged, and that stderr contains `str(w_root / <slug>)` resolved, plus `/file`.
   - Run the case before the fix and confirm it fails.
   - If adding a ticket shifts the later `zeta` T-0008 expectation, adjust that expectation or place the new case after it.
2. In `cmd_close`, at the `no filer-L*.md` refusal (around line 577), build the hint.
   - For each `r` in `worktree_roots(root)`, look for `r / d.name / 'filer-L*.md'` (glob only). Do not read the files.
   - Guard the glob with `try/except OSError`.
   - Append `; a filer record exists in <folder(s)>; commit or copy it into this tree, then rerun close` before `nothing written`. List every match.
   - When nothing matches, or outside git, keep the message byte-identical to today's.
3. Update the `close` docstring and the module usage line (line 12) to mention the hint.

Then update the docs.
4. In the root `CLAUDE.md`, in the `scripts/tickets.py` bullet, add a clause after the `close` description. The clause says a no-filer refusal names other worktrees holding `<slug>/filer-L*.md` and never reads them.
5. In `plugins/sdlc-lite/skills/file/SKILL.md` step 3.1, change "On any other refusal, report stderr and stop" to say the following. If the refusal names another worktree holding the filer record, tell the user to commit or copy it there into this tree, then rerun the dry run.
6. If `.claude/agents/sdlc-lite-author.md` restates the tickets.py behavior, keep it in sync.
### Acceptance criteria
- With the new case in place and the `cmd_close` change temporarily reverted, `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits non-zero and reports the new case. With the change, it exits 0.
- The existing (e) case still passes, and its message still contains `/file`.
- In a manual repro, `close` in main exits 1 and stderr contains the lane worktree's `<slug>` folder path. `git status` in main shows nothing written, and no filer file was read. The code path only globs.
- `grep -n "worktree" plugins/sdlc-lite/scripts/tickets.py` shows the docstring and usage text mention the hint. The root `CLAUDE.md` and `skills/file/SKILL.md` contain the new text.
- `plugins/sdlc-lite/scripts/check.sh` passes.
