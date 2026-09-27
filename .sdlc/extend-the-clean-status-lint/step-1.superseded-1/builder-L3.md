<!-- role=builder level=L3 model=opus effort=high -->
## Status
blocked

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: added `DIFF_RE`, `DIFF_QUIET_RE`, `NEGATED_RE`, `REDIRECT_RE` and `requires_clean_diff(text)` after `requires_clean_status`. Added a `lint_steps` finding: "acceptance criterion requires a clean whole-tree diff", which gives the reason and recommends `git diff --quiet "$SDLC_BASE_SHA" -- <path>` plus `git ls-files --others --exclude-standard -- <path>`. Extended the module docstring's lint paragraph, including the "script the span calls" sentence. Added selftest fixtures `(k8)`, placed just before `(k7)`. The porcelain rule, its message and the (k6) fixtures are unchanged.

## Checks
- 🟢 Criterion 1 (`git diff --quiet`, lint exit 1, "clean whole-tree diff" and "plan defect"): exit 0
- 🟢 Criterion 2 (`git diff --exit-code HEAD`): exit 0
- 🟢 Criterion 3 (`git diff --quiet "$SDLC_BASE_SHA"`): exit 0
- 🔴 Criterion 4 (`test -z "$(git diff --name-only HEAD)"`): exit 0. It passes; the red marks the criterion 5 failure listed right below.
- 🔴 Criterion 5 (split refuses and writes no `step-1`): exit 1. Split prints `handoff.md has no ## Goal section` and stops before the lint runs. See Notes.
- 🟢 Criterion 5 rerun with the fixture handoff changed to `## Goal\nh\n`: exit 0. Split refuses with "clean whole-tree diff" and writes no `step-1`.
- 🟢 Criterion 6 (guard, ok spans pass lint): prints `steps lint: ok`, exit 0
- 🟢 Criterion 7 (guard, porcelain still refused): exit 0
- 🟢 Criterion 8 (guard, `python3 plugins/sdlc-lite/scripts/steps.py selftest`): exit 0, `steps selftest: PASS`, all (k8) lines ok
- 🟢 Criterion 9 (`grep -qF 'clean whole-tree diff' plugins/sdlc-lite/scripts/steps.py`): exit 0
- 🟢 Criterion 10 (`grep -qF 'script the span calls' plugins/sdlc-lite/scripts/steps.py`): exit 0
- 🟢 Base check in a throwaway worktree at `$SDLC_BASE_SHA` (since removed): the same fixture shape (a `handoff.md` holding only `h`) with the existing porcelain criterion also exits 1 with `has no ## Goal section`. The defect is in the fixture, not in this step's change.

## Notes
plan defect: criterion 5 (the `steps.py split "$d/t"` criterion) writes `printf 'h\n' >"$d/t/handoff.md"`, a handoff with no `## Goal` section. `split` reads the goal before it lints the plan, so it always exits 1 with "has no ## Goal section" and never prints "clean whole-tree diff". The criterion cannot pass whatever the lint does. Fix: write `printf '## Goal\nh\n' >"$d/t/handoff.md"`. With that one change the criterion passes against this build (exit 0).

swap old: `d=$(mktemp -d); mkdir "$d/t"; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet'; } >"$d/t/planner-L2.md"; printf 'h\n' >"$d/t/handoff.md"; out=$(python3 plugins/sdlc-lite/scripts/steps.py split "$d/t" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff' && test ! -e "$d/t/step-1"`
swap new: `d=$(mktemp -d); mkdir "$d/t"; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet'; } >"$d/t/planner-L2.md"; printf '## Goal\nh\n' >"$d/t/handoff.md"; out=$(python3 plugins/sdlc-lite/scripts/steps.py split "$d/t" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff' && test ! -e "$d/t/step-1"`

The pair above is for the planner's information only; a builder does not set its own check.

- The work is left in the tree, uncommitted. The selftest's (k8) fixtures already cover split refusing each form and writing nothing, using a valid handoff.
- How the detector works: a single revision word (`HEAD`, `"$SDLC_BASE_SHA"`) is still flagged. Two or more non-option words, an `A..B` or `A...B` token, `--no-index`, a `--` pathspec, and a `!` word right before `git` in the `--quiet`/`--exit-code` form all pass. Redirection words such as `>/dev/null` are not counted as revisions. The emptiness path reuses `EMPTY_TEST_RE` over the whole span, as the porcelain rule does.
- `.sdlc/extend-the-clean-status-lint/handoff.md` was already modified before this step. This step did not touch it.
