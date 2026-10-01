<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- AC1 (external branch with `ticket_root: tickets` is counted by `new` on main): pass. Evidence: the command ran green on the built tree (rc=0, gamma gets `id: T-0003`). At the pre-build SHA f432d09 in a throwaway worktree, the same scenario made gamma `T-0002`, a collision, so the check goes red without the change.
- AC2 (the real selftest passes and a mutant of `other_ticket_dirs` fails it): pass. Evidence: the command returned rc=0, so the real selftest passed and the mutant that makes `other_ticket_dirs` return `worktree_pairs(root)` failed it. I also mutated the new config-reading branch in `branch_tickets` to `if False:`. The selftest then printed `tickets selftest: FAIL, these did not bite:`, so the new external-branch cases catch that regression.
- AC3 (the docstring contains `own config`): pass. Evidence: the python assert ran with rc=0. The diff shows the phrase in the "Ids across git worktrees" paragraph.
- (guard) default-layout external branch mints `T-0003`: pass. Evidence: rc=0, no change in behavior for a branch without the line.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass. Evidence: printed `tickets selftest: PASS`.
- (guard) scope check, only `tickets.py` changed outside `.sdlc`: pass. Evidence: rc=0. `git status` shows only `M plugins/sdlc-lite/scripts/tickets.py` plus untracked files under `.sdlc/`.
- Contract dependent, `fanout.py` calls `branch_tickets`: pass. Evidence: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` printed `fanout selftest: PASS`.
- Do bullets, read from the diff: pass. Evidence:
  - `other_ticket_dirs` falls back to the tree's root on `Fail`, and also on `OSError` and `UnicodeDecodeError`. That is a superset of the handoff's wording and fits its rule that another tree's problems never fail this one.
  - `id_floor`, the no-filer hint and the `close --dry-run` worktree lines all use `other_ticket_dirs`.
  - `worktree_pairs` and `worktree_roots` are unchanged.
  - `branch_tickets` reads the `<branch>:<rel>/config` blob with `git cat-file -p` and lists `<rel>/tickets` only when the line is `tickets`.
  - The selftest block (v) covers all four required cases plus the negative control, and it passed.

## Out of scope changes
None. The tracked change is only `plugins/sdlc-lite/scripts/tickets.py`. The untracked files are step artifacts under `.sdlc/0175-ticket-root-router/step-2/`, which the scope guard excludes.

## For the next attempt
None
