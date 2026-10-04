<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `.sdlc/evals/CLAUDE.md` equals `@AGENTS.md`: pass. Evidence: the test returned rc=0.
- Required strings in `.sdlc/evals/AGENTS.md`: pass. Evidence: the loop of 18 `grep -qF` checks printed no MISSING lines. I also read the file. The sections are in the required order and cover the format table, the lock text, the procedures with every option, and the limits.
- `evals.validate_eval` on the baseline: pass. Evidence: it printed `None` and exited 0.
- Baseline field lines and the three evidence paths: pass. Evidence: the `grep -qx` and loop checks returned rc=0. I read `0000-baseline.md`: `pass_rate: 0/0`, `cost_usd: unknown`, `date: 2026-09-30`, `host: all`, and the Method and Result text match the Do.
- `table-lock.json` has exactly the three keys, `eval` names the baseline, and `previous_eval` is null: pass. Evidence: rc=0.
- Lock hash equals the independently recomputed hash: pass. Evidence: the string comparison returned rc=0. The recompute uses the handoff's inline regex, which differs in mechanism from evals.py.
- `evals.py check`: pass. Evidence: `evals check: ok (1 evals, lock cites .sdlc/evals/0000-baseline.md)`.
- `evals.py list | grep -q '^0000-baseline\.md'`: pass. Evidence: rc=0.
- Router line placed after the managed:end marker: pass. Evidence: the awk check returned rc=0, and `git diff .sdlc/AGENTS.md` shows only the `## Other records` addition after `<!-- sdlc-lite:managed:end -->`.
- (guard) `tickets.py --root .sdlc check`: pass. Evidence: `ok: 208 tickets, roadmap current`.
- (guard) The four new files are not git-ignored: pass. Evidence: rc=0.
- (guard) `run.sh` and `models.json` are unchanged against `$SDLC_BASE_SHA`: pass. Evidence: `git diff --quiet` returned rc=0.
- (guard) No changes outside `.sdlc`, `evals.py` and `check.sh`: pass. Evidence: rc=0.
- No em dashes: pass. Evidence: `grep -rn '—' .sdlc/evals .sdlc/AGENTS.md` returned nothing.

I did not run a negative control. The criteria for this step are file-content and equality checks on new artifacts, and `evals.py` is the step-1 gate. The gate rejecting a bad record is outside this step.

## Out of scope changes
None for this step. `plugins/sdlc-lite/scripts/evals.py` and `plugins/sdlc-lite/scripts/check.sh` show as changed, but they belong to other steps and the guard explicitly allows them. The `.sdlc/0185-evals-folder/*` files are run artifacts.

## For the next attempt
None
