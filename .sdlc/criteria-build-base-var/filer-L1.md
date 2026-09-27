<!-- role=filer level=L1 model=sonnet effort=medium -->
All four steps pass with verified evidence, negative controls, and no scope creep. Now I have enough to draft the filer output.

## Warnings
None.

## PR title
T-0141: Scope criteria need a build-start base: run.sh exports SDLC_BASE_SHA

## PR body
### Summary
A step's scope criteria used to compare against `HEAD~1 HEAD` (assumes the builder commits, which it does not except on merge steps) or a bare `HEAD` (goes vacuous once the step's work is committed separately). This introduces `SDLC_BASE_SHA`: the commit HEAD was at when a step's build started, stored in the step dir's `base-sha` file, carried through builder and verifier runs and through `steps.py`'s guard and swap spans, and moved forward past a resync merge on the first-parent chain.

### Changes
- `scripts/run.sh`: for builder and verifier runs only (never on a dry run), resolves and stores the build-start base in `<step dir>/base-sha`: keeps a valid stored sha, moves it past any first-parent resync merge, and falls back to HEAD when missing, junk, or not an ancestor. Exports `SDLC_BASE_SHA` next to `SDLC_ROLE` for builder/verifier; every other role gets it unset even if the caller exported it.
- `scripts/run-selftest.sh`: new stub-`claude` section covering all six required cases (dry run writes nothing, planner leaks nothing, first builder run = HEAD, plain commit keeps the base, `--no-ff` resync merge moves the base, junk/non-ancestor stored value replaced by HEAD).
- `scripts/steps.py`: `split --only` sets `SDLC_BASE_SHA` to HEAD at the toplevel for guard spans; `swap` sets it to the stored `base-sha` (or HEAD); the caller's env value is always dropped. `lint`'s `pins_sha` check already allows `git diff --name-only "$SDLC_BASE_SHA"`; a selftest case pins that. Docstring and help text updated.
- `agents/planner.md` (rule 6 and rule 13), `agents/builder.md` (item 8), `agents/verifier.md` (item 4): scope and pre-build checks now use `$SDLC_BASE_SHA` in place of `HEAD~1 HEAD` / bare `HEAD`, keeping `HEAD^1` for merge steps.
- `scripts/check.py`: new `SDLC_BASE_SHA` entry in `PLAN_DEFECT_DOCS` covering planner, builder, verifier, run.sh, and steps.py.
- Repo-root `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: describe `SDLC_BASE_SHA` and the `base-sha` file.

### How each was verified
- Step 1 (run.sh/run-selftest.sh): verifier L2 (Sonnet high) passed all 6 criteria, each confirmed to bite against the pre-build tree or a mutated copy, plus a run against a mutated `run.sh` (`if true`) that fails as expected. `run-selftest.sh` and shellcheck both green.
- Step 2 (steps.py): verifier L1 passed all 3 criteria, with a negative control (a copy of `span_env` stripped of the env var) going red on exactly the two new selftest cases. `steps.py selftest` green.
- Step 3 (docs/planner/builder/verifier/check.py): verifier L1 passed all 6 criteria plus the no-em-dash check, each grep confirmed absent pre-build and present post-build; the negative-control criterion (`check.py` flags a stripped `planner.md`) confirmed real, not vacuous.
- Step 4 (gates green): builder and verifier both ran the full guard list (check.py, coverage_check.py, tickets.py, board.py, steps.py, order.py, fanout.py selftests, run-selftest.sh, hook-live-probe.sh --selftest, shellcheck, `claude plugin validate`) plus the whole-suite `check.sh` twice, all green; `hook-selftest.sh`'s plan-time flake (exit 141 under load) did not reproduce here and was excluded from the guard list per the plan's note.

## Changelog entry
Scope criteria now compare against `$SDLC_BASE_SHA`, the commit HEAD was at when a step's build started, instead of `HEAD~1 HEAD` or a bare `HEAD` — so scope checks hold whether or not the step's work is committed separately, and move correctly past a resync merge.

## Follow-ups
None.
