<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- AC1 (`external_branches` returns `["codex/x","ext"]`, `config_numbered` holds): pass. I ran the span on the built tree: rc=0. At `$SDLC_BASE_SHA` in a throwaway worktree it exits 1 with `AttributeError: module 'tickets' has no attribute 'external_branches'`, so the check can go red.
- AC2 (registered `ext` holds T-0002, `new` mints T-0003): pass. Built tree rc=0. At base rc=1, so it bites.
- AC3 (`ext` holds `0002-b`, `.0003-c`, `_templates` T-0009 and `plain`; `new` mints T-0004): pass. Built tree rc=0. At base rc=1. T-0004 is only reachable if `.0003-c` is counted and `_templates` (T-0009) and `plain` are skipped, so the folder rule is checked.
- AC4 (`check` prints `warning: external_branch nosuch is not a local branch`): pass. Built tree rc=0. At base rc=1.
- AC5 (`"external_branch: <branch>"` in `tickets.__doc__`): pass. Built tree rc=0. At base `AssertionError`.
- (guard) unregistered `ext` branch still leaves `new` minting T-0002: pass. Built tree rc=0 (the collision behaviour is unchanged). Base rc=0, as a guard should be.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass. Output `tickets selftest: PASS`, rc=0. I read the new selftest cases (i) to (iv) in the diff. They include negative controls (the unregistered copies mint the colliding T-0002) and the outside-git and missing-branch cases.
- (guard) scope diff touches only `tickets.py`: pass. The command exits 0. `git status --short` outside `.sdlc` shows only `M plugins/sdlc-lite/scripts/tickets.py`.
- Other builder claims: `git diff --check` exits 0, and `python3 plugins/sdlc-lite/scripts/check.py` prints `ok: 18 role levels, 8 agents checked`. I ran both myself. I did not re-run the builder's 6 mutations, so the negative-control claim is unverified. My base-tree runs cover the new-behavior ACs instead.
- Docstring and code against the Do:
  - Docstring: the usage block, the check line and the "Ids across git worktrees" paragraph are updated, and `id_floor`'s docstring names the registered branches (diff).
  - `id_floor`: folds `branch_tickets` over `external_branches`.
  - `branch_tickets`: uses `ls-tree`, one `cat-file --batch`, and catches errors to `[]`.
  - `cmd_check`: warns only inside git and keeps exit 0.
  - The steelman pass found no defect to file. Each of my candidate objections (the new `-`-prefixed name guard, the newline-name skip, the extra `unknown_branches` helper) is either harmless or something the Do does not forbid.

## Out of scope changes
None. The `.sdlc/` artifacts are excluded from scope by the guard, and `tickets.py` is the only project file changed.

## For the next attempt
None
