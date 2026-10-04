<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1, copy with `.sdlc/evals` and `docs/validation` present and `check.py` run on it: pass. Evidence: I ran the command and got `ok: 19 role levels, 9 agents checked`, rc=0. The in-script negative control therefore flagged, since otherwise it would have appended an error.
- Criterion 2, `builder:L1` model rewritten in the copy: pass. Evidence: rc=1 and the output contained `FAIL evals: .sdlc/evals/table-lock.json: model table changed: sha256 dec3a8… is not the locked ab3aa5…`. This is the red case, and criterion 1 on the same tree is the green case.
- Criterion 3, bare plugin copy with no repository `.sdlc`: pass. Evidence: rc=0, output `skip: evals lock guard (no /private/var/.../T/.sdlc)` and `ok: …`.
- Criterion 4, `.sdlc` present but empty: pass. Evidence: rc=1 and the output contained `FAIL evals: .sdlc/evals: missing`.
- Criterion 5, `14. Evals lock` in the docstring: pass. Evidence: `grep -qF '14. Evals lock' plugins/sdlc-lite/scripts/check.py` gave rc=0. The diff also shows the item at check.py:50-53.
- Guard, `check.py` on the real plugin: pass. Evidence: `ok: 19 role levels, 9 agents checked`, rc=0.
- Guard, `run.sh` and `models.json` unchanged from `$SDLC_BASE_SHA`: pass. Evidence: rc=0.
- Guard, only `evals.py`, `check.sh` and `check.py` changed outside `.sdlc`: pass. Evidence: rc=0.

Builder claims: I did not take the builder's summary as evidence. I read the `git diff` and ran every criterion myself.

I considered failing criterion 3 on a possible rebuttal, and dropped it. The `skip:` line prints from the `else` branch of `sdlc.is_dir()` (diff, check.py). Criterion 3 observes that line directly, and the same code gives the red result in criterion 4 when the directory exists but is empty.

## Out of scope changes
None. `check.sh` gained an `evals.py selftest` line and a comment edit. That file is allowed by the third guard and is plausibly step 1's work. `.sdlc/AGENTS.md` and `.sdlc/evals` are under `.sdlc`, which is excluded from the scope guard.

## For the next attempt
None
