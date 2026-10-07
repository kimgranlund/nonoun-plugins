<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Temp-repo lint criterion (ok.md exits 0, bad.md exits 1, names `gone/AGENTS.md`, ends with `plan defect`): pass. Evidence: I ran the full command and it printed `C1PASS`. `ok.md` gave `steps lint: ok`. `bad.md` gave `steps: …/bad.md step 1: ### Read first lists a path that does not exist: gone/AGENTS.md`, then `plan defect: replan this step (/chain 3)`. At `$SDLC_BASE_SHA` in a throwaway worktree, the same `bad.md` lints `steps lint: ok` with rc=0, so the check goes red on the old code and green on the new.
- Selftest `(r) lint accepts a ### Read first path that exists`: pass. Evidence: `steps.py selftest` prints `ok: (r) lint accepts a ### Read first path that exists`.
- Selftest `(r) lint refuses a ### Read first path that does not exist`: pass. Evidence: the same output prints `ok: (r) lint refuses a ### Read first path that does not exist`. The case also asserts that `split` refuses and writes no step dir (steps.py diff).
- Selftest `(r) split copies ### Read first into the step handoff`: pass. Evidence: the same output prints `ok: (r) split copies ### Read first into the step handoff`. The case compares the handoff text byte for byte with the expected text.
- `grep -qF '### Read first' plugins/sdlc-lite/scripts/steps.py`: pass. Evidence: `grep -c` gives 14 matches, including the docstring and the finding text.
- `grep -qF 'Read first' docs/references/sdlc-internals.md`: pass. Evidence: the `scripts/steps.py` entry now names `### Read first`, the one-line item form, the path base, and the refusal.

Other checks:
- The whole selftest ends with `steps selftest: PASS`.
- `git diff --check` is clean.
- The `steps.py` diff has the `read_first_paths` helper, which stops at the next `## ` or `### ` line, skips ``` fenced lines, and takes the first code span of a list item. It also has the `lint_steps` resolution against `git_toplevel` (else the plan's folder), the docstring updates, and case (r).
- `swap` and the `split` copy logic are untouched in the diff.

## Out of scope changes
None. The diff touches only `plugins/sdlc-lite/scripts/steps.py` and `docs/references/sdlc-internals.md`. The other untracked files are run artifacts in the step dir.

## For the next attempt
None
