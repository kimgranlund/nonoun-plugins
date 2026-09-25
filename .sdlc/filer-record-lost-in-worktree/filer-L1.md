<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0056: close names the other worktree that holds the filer record

## PR body
### Summary
/chain commits only when a step passes. The filer runs after the last step, so `filer-L1.md` stays uncommitted in the lane worktree and the merge to main leaves it behind. `close <slug>` on main then refuses with "no filer-L*.md" and gives no hint of where the record is. The refusal still happens, but now it names every other worktree whose same-relative `<slug>/` folder holds a `filer-L*.md`. close only globs for these files. It never reads or uses a filer file from another tree.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - When `cmd_close` finds no filer file, it globs `<other root>/<slug>/filer-L*.md` for each root from `worktree_roots`. The glob is wrapped in `try/except OSError`.
  - Each match is added to the message: "a filer record exists in <folder(s)>; commit or copy it into this tree, then rerun close".
  - With no match, or outside git, the message is byte-identical to before.
  - The usage text and the `cmd_close` docstring are updated.
  - A new worktree selftest case runs after `zeta`, so no ids shift. It reuses `alpha`, whose filer record exists only in `wt`.
- `CLAUDE.md`: the tickets.py bullet describes the hint (glob only, never read).
- `plugins/sdlc-lite/skills/file/SKILL.md` step 3.1: when the refusal names another worktree, commit or copy the record from there into this tree, then rerun the dry run.
- `.claude/agents/sdlc-lite-author.md`: a keep-in-sync line for the hint.

### Verification
- Builder: `tickets.py selftest` with the new case and without the fix reported only the new case as failing. With the fix it passed. `check.sh` exited 0.
- Verifier L1 verdict was pass:
  - It ran the selftest in a throwaway worktree with the hint turned off. The new case failed ("did not bite"). The assertion that makes it fail is the resolved `w_root/alpha` path in stderr. The rc, snapshot and `/file` checks also pass on the old message.
  - With the real change the selftest printed PASS, and the existing (e) case still contains `/file`.
  - `check.sh` exited with rc=0.
  - Its shell did not report exit codes for the selftest runs, so it relied on the PASS/FAIL lines.
- Neither role ran a separate manual repro. The selftest case covers the same steps: rc 1, main's `.sdlc` snapshot unchanged, and the lane folder named in stderr.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py close`: when this tree has no filer record, the refusal now names every other git worktree whose `<slug>/` folder holds a `filer-L*.md`, so you can commit or copy it in and rerun. It never reads those files. (T-0056)

## Follow-ups
None
