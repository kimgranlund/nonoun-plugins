<!-- role=verifier level=L2 model=sonnet effort=high -->
Cleaned up already. All criteria verified with real command runs against the built tree, and the negative-control run at pre-build HEAD confirms the checks actually bite (red at base, green after the build; base's own gates unaffected).

## Verdict
pass

## Criteria
- `git diff --quiet` lint refusal (criterion 1): pass. Evidence: ran the exact command span; rc=1, output contains "acceptance criterion requires a clean whole-tree diff" and "plan defect: replan this step (/chain 3)".
- `git diff --exit-code HEAD` lint refusal (criterion 2): pass. Evidence: ran the exact command span; rc=1, output "C2PASS" (contains "clean whole-tree diff").
- `git diff --quiet "$SDLC_BASE_SHA"` lint refusal (criterion 3): pass. Evidence: ran the exact command span; rc=1, "C3PASS".
- `test -z "$(git diff --name-only HEAD)"` lint refusal (criterion 4): pass. Evidence: ran the exact command span; rc=1, "C4PASS".
- `split` on a task dir refuses and writes no `step-1` (criterion 5): pass. Evidence: ran the exact command span; rc=1, output contains "clean whole-tree diff", `test ! -e "$d/t/step-1"` true, "C5PASS".
- (guard) scoped/range/negated/listing/diff-tree spans pass lint: pass. Evidence: ran the exact span; `steps lint: ok`, rc=0.
- (guard) porcelain rule unaffected: pass. Evidence: ran the exact span; rc=1, output contains "clean porcelain status", "C7PASS".
- (guard) `steps.py selftest`: pass. Evidence: `python3 plugins/sdlc-lite/scripts/steps.py selftest` rc=0, "steps selftest: PASS", 133 `ok` lines including the new `(k8)` fixtures (`ok: (k8) split refuses...`, `ok: (k8) lint refuses...`, `ok: (k8) a pathspec, a two-commit range, a negated --quiet, a listing, and diff-tree pass lint`).
- `grep -qF 'clean whole-tree diff' plugins/sdlc-lite/scripts/steps.py`: pass. Evidence: grep exits 0.
- `grep -qF 'script the span calls' plugins/sdlc-lite/scripts/steps.py`: pass. Evidence: grep exits 0, and file:line at plugins/sdlc-lite/scripts/steps.py:68-70 ("The detector reads only span text, so a clean check hidden inside a script the span calls stays out of reach.").
- Check bites (negative control, checks-that-bite): pass. Evidence: same criterion-1 span run against a throwaway worktree at `$SDLC_BASE_SHA` (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" "$SDLC_BASE_SHA"`) gave rc=0 "steps lint: ok" (red-for-the-new-rule at base), while the built tree gives rc=1 with the new finding (green after). The gate criterion (guard selftest) also passes standalone at base (rc=0, PASS), confirming it is an unrelated pre-existing gate, not inherited red. Worktree removed after (`git worktree remove --force`).
- Porcelain rule, its message and (k6) fixtures left unchanged: pass. Evidence: `git diff plugins/sdlc-lite/scripts/steps.py` shows no changes to `STATUS_RE`, `PORCELAIN_RE`, `requires_clean_status`, its finding text, or the (k6) selftest block; only additive lines (`DIFF_RE`, `DIFF_QUIET_RE`, `NEGATED_RE`, `REDIRECT_RE`, `requires_clean_diff`, a new `lint_steps` branch, docstring paragraph, and a new (k8) block) were added.

## Out of scope changes
`.sdlc/0135-extend-the-clean-status-lint/handoff.md` (task-level Goal/Constraints/Plan review edit) and the untracked planner artifacts (`planner-L2.md`, `planner-L3.md`, `runs.jsonl`, `step-1.superseded-1/`, `step-2/`) are present in the diff/status but predate this build: the builder's own transcript (`builder-L3.log`, first tool result) shows this exact `git status --porcelain`/diff state (including the modified handoff.md) captured before the builder made any edit, and the builder's `## Changes` section names only `plugins/sdlc-lite/scripts/steps.py`. Checked, not attributable to this step's build; dismissing as pre-existing planner/replan state, not out of scope for this build.

## For the next attempt
None.
