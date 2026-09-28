<!-- role=filer level=L1 model=sonnet effort=medium -->
Both steps passed verification (step-1 verifier-L2 pass, step-2 verifier-L1 pass), and check.sh is green. No warnings.

## Warnings
None

## PR title
T-0135: Extend the clean-status lint to catch a whole-tree diff check

## PR body
Summary: `steps.py lint` and `split` refused a plan criterion that used `git status --porcelain`/`-s` to demand a clean tree, but let the same requirement through when written as a whole-tree `git diff` (`--quiet`, `--exit-code`, or an emptiness test on diff output). Such a criterion can never pass, since builders never commit and their own edits keep the diff non-empty. This closes that gap while keeping scoped (`-- <pathspec>`) and commit-to-commit range diffs passing.

Changes:
- `plugins/sdlc-lite/scripts/steps.py`: added `requires_clean_diff` (with `DIFF_RE`, `DIFF_QUIET_RE`, `NEGATED_RE`, `REDIRECT_RE`) next to the existing `requires_clean_status`. It flags a `git diff` span with no `--` pathspec and no commit-to-commit range, when the span uses `--quiet`/`--exit-code` unnegated or tests the diff output for emptiness, while `--no-index` stays exempt. `lint_steps` now reports a "acceptance criterion requires a clean whole-tree diff" finding recommending `git diff --quiet "$SDLC_BASE_SHA" -- <path>` plus `git ls-files --others --exclude-standard -- <path>`. Added a `(k8)` selftest block covering refused and passing spans. The porcelain rule, its message, and `(k6)` fixtures are untouched. The module docstring gained a paragraph noting the detector reads only span text, so a check hidden inside a script the span calls stays out of reach.
- `plugins/sdlc-lite/agents/planner.md` (rule 13), root `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md`, and `plugins/sdlc-lite/scripts/check.py` (`PLAN_DEFECT_DOCS`): synced the new rule's wording and the span-text limitation into the docs the doctrine requires to stay current with a plan-defect rule.

Verified:
- Step 1 (builder L3 / verifier L2, pass): all 10 acceptance criteria run directly against the built tree, including a negative control at the pre-build HEAD showing the new rule is red-for-new-behavior at base and green after the build, plus the full `steps.py selftest` (133 ok lines including the new `(k8)` fixtures) and the porcelain rule's fixtures unaffected.
- Step 2 (builder L2 / verifier L1, pass): all 5 doc/`check.py` grep criteria plus 3 guards (porcelain wording preserved, `steps.py selftest`, and full `scripts/check.sh`) run directly; `check.sh` came back green with all selftests, shellcheck, and `claude plugin validate` passing.
- One step-1 build attempt was blocked by a plan defect in the acceptance criteria (a fixture handoff missing `## Goal`, so `split` stopped on the goal check before it could lint); recorded under the task's `## Plan review`, fixed by a replan, and re-verified clean on the next attempt (`step-1.superseded-1/` kept for the record).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
`steps.py lint`/`split` now also refuse a plan criterion that checks for a clean whole work tree via `git diff --quiet`/`--exit-code` or an emptiness test on diff output, not only via `git status --porcelain`; scoped and commit-range diffs still pass. Docs (`planner.md`, `CLAUDE.md`, `sdlc-lite-author.md`, `check.py`) updated to match.

## Follow-ups
None
