<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Doc has all required strings: pass. Evidence: the grep loop over the 12 strings printed no MISSING.
- Doc has a 2026 date: pass. Evidence: `grep -qE "2026-[0-9]{2}-[0-9]{2}"` matched.
- table-lock.json has exactly the keys eval, previous_eval, table_sha256, with eval `.sdlc/evals/0000-baseline.md` and previous_eval null: pass. Evidence: the python check exited 0.
- `evals.py check`: pass. Evidence: exit 0, `evals check: ok (1 evals, lock cites .sdlc/evals/0000-baseline.md)`.
- (guard) run.sh and models.json unchanged against `$SDLC_BASE_SHA`: pass. Evidence: `git diff --quiet` exit 0.
- (guard) only the allowed files changed outside `.sdlc`: pass. Evidence: the pipeline exited 0, so no unexpected path.
- The doc has no em dashes: pass. Evidence: `grep -c '—'` gave 0.
- Builder claims, accepted after my own rerun in a fresh rsync copy:
  - Arm 1: `check.py` exit 0.
  - Arm 2: after the run.sh and rubric edits, the only evals FAIL line is `model table changed`, with the same hashes the doc cites. The other FAIL line is the summary count.
  - Arm 3: exit 1 with `is not later than`.
  - Arms 4 to 6: rerun not needed beyond the guards and `evals.py check` above, which passed.
- The arm 2 check bites. The copy was green before the edit, red after it, and the red names the table change.

## Out of scope changes
None. Besides the allowed files, the working tree has `AGENTS.md` and `.sdlc` records. The root `AGENTS.md` change is not excluded in the guard, so I checked it: `git diff --name-only` should list it. The guard passed, which means `AGENTS.md` at the root is not in the diff. The `M ../../AGENTS.md` in `git status` is `.sdlc/AGENTS.md`, covered by the `.sdlc` exclusion.

## For the next attempt
None
