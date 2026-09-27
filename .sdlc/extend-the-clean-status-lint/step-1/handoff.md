## Task goal
`steps.py lint` and `split` also refuse, as a plan defect, a criterion that requires a clean whole work tree through `git diff` (for example `git diff --quiet` or `git diff --exit-code` with no `-- <pathspec>` and no two-commit range), not only through an empty `git status --porcelain`/`-s`, while scoped and commit-to-commit diffs still pass. A clean check hidden inside a script the span calls stays out of reach, since the detector only reads span text; the docs say so.

## Step 1: Detect a clean whole-tree diff in the steps.py lint
level: L3
### Do
Replan note: the superseded build (`step-1.superseded-1/builder-L3.md`) left this work uncommitted in `plugins/sdlc-lite/scripts/steps.py` (`DIFF_RE`, `DIFF_QUIET_RE`, `NEGATED_RE`, `REDIRECT_RE`, `requires_clean_diff`, the `lint_steps` finding, the docstring paragraph, and the (k8) fixtures). It blocked only because criterion 5's fixture handoff had no `## Goal` section, so `split` stopped on the goal before it linted; that fixture now writes `## Goal` plus a body. Start from the work already in the tree and keep it wherever it meets the criteria below; if the tree was reset to HEAD, build it as described here.

In `plugins/sdlc-lite/scripts/steps.py`, next to `requires_clean_status`, add a detector `requires_clean_diff(text)`. It matches a `git diff` invocation: the word `git`, whitespace, then `diff` not followed by `[\w-]`, so `git diff-tree` never matches. It takes that invocation's args up to `|;&)` or a backtick, the same way `STATUS_RE` does. The span is flagged when all of these hold:
- the args hold no `--` pathspec separator (reuse `PATHSPEC_RE`);
- the args hold no commit-to-commit range: no `A..B` or `A...B` token, and not two or more non-option revision words (`HEAD~1 HEAD` passes; a single rev such as `HEAD` or `"$SDLC_BASE_SHA"` is still whole-tree against the work tree and is flagged);
- `--no-index` is absent;
- either (a) the args hold `--quiet` or `--exit-code` and the invocation is not negated by a `!` word right before `git`, or (b) the span tests the diff output for emptiness (reuse `EMPTY_TEST_RE`, as in `test -z "$(git diff --name-only HEAD)"`).

In `lint_steps`, add a finding for a flagged span. Its text must contain `acceptance criterion requires a clean whole-tree diff`. Say why: builders never commit, so the step's own changes keep the whole-tree diff non-empty and the criterion can never pass. Recommend `git diff --quiet "$SDLC_BASE_SHA" -- <path>` plus `git ls-files --others --exclude-standard -- <path>` instead. `lint_or_fail` then adds the `plan defect` line, as for the other findings.

Leave the porcelain rule, its message and its (k6) fixtures unchanged.

Add selftest fixtures (a new `(k8)`) built like (k6), assembling the words as `'git ' + 'diff'`. They must prove that:
- lint and split refuse `git diff --quiet`, `git diff --exit-code HEAD`, `git diff --quiet "$SDLC_BASE_SHA"` and `test -z "$(git diff --name-only HEAD)"`, and split writes nothing;
- `git diff --quiet HEAD -- src`, `git diff --quiet HEAD~1 HEAD`, `git diff --exit-code main...HEAD`, `! git diff --quiet`, `git diff --name-only HEAD` and `git diff-tree --cc HEAD` pass lint.

Extend the module docstring's lint paragraph to describe the new rule using the phrase `clean whole-tree diff`. Add a sentence stating that the detector reads only span text, so a clean check hidden inside a script the span calls stays out of reach (use the exact words `script the span calls`).
### Acceptance criteria
- `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff' && printf '%s\n' "$out" | grep -q 'plan defect'`
- `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --exit-code HEAD'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff'`
- `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet "$SDLC_BASE_SHA"'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff'`
- `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' 'test -z "$(git' 'diff --name-only HEAD)"'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff'`
- `d=$(mktemp -d); mkdir "$d/t"; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet'; } >"$d/t/planner-L2.md"; printf '## Goal\nh\n' >"$d/t/handoff.md"; out=$(python3 plugins/sdlc-lite/scripts/steps.py split "$d/t" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff' && test ! -e "$d/t/step-1"`
- (guard) `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet HEAD -- src' git 'diff --quiet "$SDLC_BASE_SHA" -- plugins' git 'diff --quiet HEAD~1 HEAD' git 'diff --exit-code main...HEAD' git 'diff --name-only "$SDLC_BASE_SHA"' '! git' 'diff --quiet' git 'diff-tree --cc HEAD'; } >"$f"; python3 plugins/sdlc-lite/scripts/steps.py lint "$f"`
- (guard) `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' 'test -z "$(git' 'status --porcelain)"'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean porcelain status'`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest >/dev/null 2>&1`
- `grep -qF 'clean whole-tree diff' plugins/sdlc-lite/scripts/steps.py`
- `grep -qF 'script the span calls' plugins/sdlc-lite/scripts/steps.py`
