<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest prints `board selftest: PASS`: pass. Evidence: `python3 plugins/sdlc-lite/scripts/board.py selftest` printed `board selftest: PASS`.
- Two ticketed tasks (T-0003 older, T-0002 newer) plus one unticketed task, no flag: pass. Evidence: in a temp root, `board.py --root <tmp>` listed `new2 old3 plain`, so T-0002 first, T-0003 second and the unticketed task last. The negative control shows the check can fail: the HEAD version of board.py on the same fixture gave `old3 new2 plain`.
- No ticketed tasks, no flag equals `--sort recent`: pass. Evidence: on a two-task fixture with no tickets, I deleted `.board-state.json` between runs and `cmp` of the default output against the `--sort recent` output reported `same`.
- `--sort id`, `--sort name` and `--sort recent` on the ticketed fixture: pass. Evidence: id gave `new2 old3 plain`, name gave `new2 old3 plain`, recent gave `old3 new2 plain`. Only one task on the fixture lacks a ticket, so that fixture cannot show the unticketed pair ordering. The code covers it: explicit `id` uses a 0 as the mtime component (board.py `sort_tasks`), so unticketed tasks still sort by name. The updated selftest asserts `['yankee-two','zulu-three','alpha','bravo']` for `--sort id`.
- `--summary` unchanged: pass. Evidence: `grep -n "sort_tasks"` shows the only call is at line 461 in `main()`, and `summary()` (line 147) does not call it. The `--summary` run printed `plain not planned`.
- `--task <slug>` renders only that task: pass. Evidence: `--task new2` produced 0 matching lines for `old3` or `plain`.
- No doc assumes newest-last order (risk check): pass. Evidence: grep for "newest" and "recency" in `skills/board` and `skills/chain` returned nothing.

## Out of scope changes
None. The diff touches only `plugins/sdlc-lite/scripts/board.py`, plus `.sdlc` task artifacts.

## For the next attempt
None
