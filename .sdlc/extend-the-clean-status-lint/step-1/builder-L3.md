<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: I kept the superseded build's uncommitted work as it was, because it already meets every criterion. It adds `requires_clean_diff` (with `DIFF_RE`, `DIFF_QUIET_RE`, `NEGATED_RE`, `REDIRECT_RE`), a `lint_steps` finding "acceptance criterion requires a clean whole-tree diff" that recommends `git diff --quiet "$SDLC_BASE_SHA" -- <path>` plus `git ls-files --others --exclude-standard -- <path>`, a docstring paragraph that includes "script the span calls", and the (k8) selftest fixtures. I made no new edits this run.

## Checks
- Criterion 1 (`git diff --quiet`): lint exits 1 and prints both "clean whole-tree diff" and "plan defect". rc=0
- Criterion 2 (`git diff --exit-code HEAD`): lint exits 1 and prints "clean whole-tree diff". rc=0
- Criterion 3 (`git diff --quiet "$SDLC_BASE_SHA"`): lint exits 1 and prints "clean whole-tree diff". rc=0
- Criterion 4 (`test -z "$(git diff --name-only HEAD)"`): lint exits 1 and prints "clean whole-tree diff". rc=0
- Criterion 5 (split on a task dir): split exits 1, prints "clean whole-tree diff", and writes no `step-1`. rc=0
- Criterion 6 (guard: scoped, range, negated, listing and diff-tree spans): lint prints "steps lint: ok". rc=0
- Criterion 7 (guard: the porcelain rule still refuses with "clean porcelain status"). rc=0
- Criterion 8 (guard): `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with 133 ok lines and "steps selftest: PASS". All nine (k8) checks are ok.
- Criterion 9: `grep -qF 'clean whole-tree diff' plugins/sdlc-lite/scripts/steps.py`. rc=0
- Criterion 10: `grep -qF 'script the span calls' plugins/sdlc-lite/scripts/steps.py`. rc=0

## Notes
Nothing is committed, as expected for a non-merge step. The (k6) porcelain rule, its message and its fixtures are unchanged in the diff. The other uncommitted files under `.sdlc/extend-the-clean-status-lint/`, including the modified task `handoff.md`, come from the planner and runner, not from this step.
