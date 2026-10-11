<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
fail

## Criteria
- #1 `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` passes, including the five `T-0426` cases: pass. Evidence: I ran it on the built tree. It exited 0 and ended with `dispatch selftest: PASS`. All five cases printed `ok:` (two worktrees cleaned with `cleaned: 2 tmp worktrees`, sibling and outside survive, symlink refused, `.worktrees/tmp` itself refused, failed attempt `cleaned: 1 tmp worktrees`).
- #2 Those cases failed before the change to `remove_tmp`: pass. Evidence: I made a throwaway worktree at `$SDLC_BASE_SHA`. In it I put the built `dispatch.py` with only the `remove_tmp` function swapped back to the base version (the swap is shown by `diff`). Its selftest exited 1 with `dispatch selftest: FAIL` and three failing cases: `FAIL: T-0426 a recorded role with two detached worktrees ... cleaned: 2 tmp worktrees`, `FAIL: T-0426 a symlinked tmp_prefix is refused ...` and `FAIL: T-0426 a failed attempt also cleans ...`. These are exactly the three the criterion names. The sibling case and the `.worktrees/tmp` case stayed `ok` at base, as the criterion allows. No `process-deviations.md` exists.
- #3 `check.py`, `hook-selftest.sh`, and `tickets.py --root .sdlc check` pass: pass. Evidence: `check.py` exited 0 (`ok: 19 role levels, 9 agents, 22 generated definitions checked`). `hook-selftest.sh` exited 0 (`hook selftest: PASS`), and in this session the `block-stray-worktree` hook really did deny a `git worktree add` it could not parse. `tickets.py --root .sdlc check` exited 0 (`ok: 420 tickets, roadmap current`); its warnings are about older closed tickets.
- #4 No path outside the role's own prefix is removed (inspect `remove_tmp`): fail. Evidence:
  - The defect is at `plugins/sdlc-lite/scripts/dispatch.py:806`. It builds `real = realpath(dirname(prefix)) + basename(prefix)`, so a last component of `.` or `..` is never normalized. The string check at :810 (`real.startswith(root + os.sep)`) then accepts it. But `under(path, real)` at :816 and `shutil.rmtree(real)` at :819 resolve it to the whole `.worktrees/tmp` root.
  - Probe (`/tmp/v0426s/probe.py` in a fresh repo with a sibling worktree at `.worktrees/tmp/sibling-role/wt`):
    - Built code, `tmp_prefix=<tree>/.worktrees/tmp/x/..` gives `cleaned: 1 tmp worktrees` and `sibling survives: False`.
    - Built code, `tmp_prefix=<tree>/.worktrees/tmp/.` gives the same: `cleaned: 1 tmp worktrees` and `sibling survives: False`.
    - Base code refused both (`refusing to remove ...: not under ...`), and the sibling survived.
  - So the change removes another role's worktree and weakens a guard the base code already had. It also misses the Do's rule "refusing any path that is not strictly under `.worktrees/tmp/`".
  - Steelman checked: `prepare` never writes such a name. But the dispatch JSON is a file on disk, the ticket asks for refusal, and the old code refused it. So the finding stands.

## Out of scope changes
None.
- `docs/references/sdlc-internals.md`: the diff changes one sentence to describe the new `record` cleanup. AGENTS.md asks that the contract be updated when behavior changes, so this is in scope.
- The `.sdlc/0426-record-removes-tmp-prefix/handoff.md` change adds `## Acceptance criteria`. `plugins/sdlc-lite/agents/solo.md:48` tells an L2 solo to do exactly that.
- `git diff --check` is clean, and no em or en dashes appear in the diff.

## For the next attempt
Fix `remove_tmp` in `plugins/sdlc-lite/scripts/dispatch.py:806-810`:
- Normalize the prefix before the containment check, for example `real = os.path.join(os.path.realpath(os.path.dirname(os.path.normpath(prefix))), os.path.basename(os.path.normpath(prefix)))`.
- Also refuse a basename of `.` or `..`, or any `..` component.
- Keep the symlink refusal on the un-resolved last component, and require `real != root` and `real.startswith(root + os.sep)` on the normalized path.

Add a selftest case `T-0426` in which a `tmp_prefix` of `<tree>/.worktrees/tmp/x/..` and one of `<tree>/.worktrees/tmp/.` are both refused and the sibling worktree survives. Run it against the current code first and see it fail.
