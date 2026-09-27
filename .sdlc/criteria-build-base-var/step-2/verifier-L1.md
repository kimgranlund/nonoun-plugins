<!-- role=verifier level=L1 model=sonnet effort=medium -->
Same as before, nothing changed by my verification activity. All good.

## Verdict
pass

## Criteria
- `sp=$PWD/plugins/sdlc-lite/scripts/steps.py && d=$(mktemp -d) && ... && python3 "$sp" split --only 1 "$d/t" && test -f "$d/t/step-1/handoff.md"`: pass. Evidence: ran the command verbatim; output printed `.../step-1/handoff.md` then `CRIT1_PASS`, exit 0.
- `grep -q SDLC_BASE_SHA plugins/sdlc-lite/scripts/steps.py`: pass. Evidence: ran it, printed `CRIT2_PASS`.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: ran it in the built tree; all ~110 cases printed `ok:`, ending `steps selftest: PASS`, exit 0.

Negative control (checks-that-bite): copied `plugins/sdlc-lite/scripts/` to a scratch dir (not under git state, no working-tree change), broke `span_env` to no longer set/strip `SDLC_BASE_SHA`, and reran `selftest`. It went red on exactly the two new cases (`(o) split --only runs a guard with SDLC_BASE_SHA = HEAD, overriding the caller env` and `swap: a new span sees SDLC_BASE_SHA from the stored base-sha, not HEAD`), confirming these checks bite. Restored nothing needed since the scratch copy was never part of the working tree.

Read the diff (`git diff plugins/sdlc-lite/scripts/steps.py`): `rev_commit`, `base_sha`, `span_env` helpers added; `run_guard` takes `base=None` and runs spans via `subprocess.Popen(..., env=span_env(base))`; `run_guards` (used by `split --only`) computes `base = base_sha(top)` (HEAD at toplevel); `swap` computes `base = base_sha(top, d)` (reads `<step dir>/base-sha` first line, falls back to HEAD via `rev_commit` validation). Docstring and `--only`/`--timeout` help text updated to describe the env var. Matches the Do exactly.

## Out of scope changes
`plugins/sdlc-lite/scripts/run.sh` and `plugins/sdlc-lite/scripts/run-selftest.sh` are modified in the working tree but not touched by this step's builder. Checked: these are step 1's own changes in the same task (`.sdlc/criteria-build-base-var/step-1/handoff.md` assigns exactly these two files to step 1, "Do" section), already independently verified pass in `step-1/verifier-L2.md` (`## Verdict\npass`). Not out of scope for step 2; dismissing.

## For the next attempt
None.
