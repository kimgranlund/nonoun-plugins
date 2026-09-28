<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `steps.py lint` and `split` refuse, as a plan defect, a criterion that requires a clean whole work tree through `git diff` (a `--quiet` or `--exit-code` diff, or an emptiness test on diff output, with no `-- <pathspec>` and no two-commit range). Scoped diffs, commit-to-commit diffs and the existing porcelain rule keep working. The docs say that a clean check hidden inside a script the span calls stays out of reach.

## Step 1: Detect a clean whole-tree diff in the steps.py lint
level: L3
### Do
In `plugins/sdlc-lite/scripts/steps.py`, next to `requires_clean_status` (around lines 512 to 528), add a detector `requires_clean_diff(text)`. It matches a `git diff` invocation: the word `git`, whitespace, then `diff` not followed by `[\w-]`, so `git diff-tree` never matches. It takes that invocation's args up to `|;&)` or a backtick, the same way `STATUS_RE` does. The span is flagged when all of these hold:
- the args hold no `--` pathspec separator (reuse `PATHSPEC_RE`);
- the args hold no commit-to-commit range: no `A..B` or `A...B` token, and not two or more non-option revision words (`HEAD~1 HEAD` passes; a single rev such as `HEAD` or `"$SDLC_BASE_SHA"` is still whole-tree against the work tree and is flagged);
- `--no-index` is absent;
- either (a) the args hold `--quiet` or `--exit-code` and the invocation is not negated by a `!` word right before `git`, or (b) the span tests the diff output for emptiness (reuse `EMPTY_TEST_RE`, as in `test -z "$(git diff --name-only HEAD)"`).

In `lint_steps`, add a finding for a flagged span. Its text must contain `acceptance criterion requires a clean whole-tree diff`. Say why: builders never commit, so the step's own changes keep the whole-tree diff non-empty and the criterion can never pass. Recommend `git diff --quiet "$SDLC_BASE_SHA" -- <path>` plus `git ls-files --others --exclude-standard -- <path>` instead. `lint_or_fail` then adds the `plan defect` line, as for the other findings.

Leave the porcelain rule, its message and its (k6) fixtures unchanged.

Add selftest fixtures (for example a new `(k8)`) built like (k6), assembling the words as `'git ' + 'diff'`. They must prove that:
- lint and split refuse `git diff --quiet`, `git diff --exit-code HEAD`, `git diff --quiet "$SDLC_BASE_SHA"` and `test -z "$(git diff --name-only HEAD)"`, and split writes nothing;
- `git diff --quiet HEAD -- src`, `git diff --quiet HEAD~1 HEAD`, `git diff --exit-code main...HEAD`, `! git diff --quiet`, `git diff --name-only HEAD` and `git diff-tree --cc HEAD` pass lint.

Extend the module docstring's lint paragraph (lines 57 to 62) to describe the new rule using the phrase `clean whole-tree diff`. Add a sentence stating that the detector reads only span text, so a clean check hidden inside a script the span calls stays out of reach (use the exact words `script the span calls`).
### Acceptance criteria
- `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff' && printf '%s\n' "$out" | grep -q 'plan defect'`
- `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --exit-code HEAD'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff'`
- `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet "$SDLC_BASE_SHA"'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff'`
- `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' 'test -z "$(git' 'diff --name-only HEAD)"'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff'`
- `d=$(mktemp -d); mkdir "$d/t"; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet'; } >"$d/t/planner-L2.md"; printf 'h\n' >"$d/t/handoff.md"; out=$(python3 plugins/sdlc-lite/scripts/steps.py split "$d/t" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean whole-tree diff' && test ! -e "$d/t/step-1"`
- (guard) `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' git 'diff --quiet HEAD -- src' git 'diff --quiet "$SDLC_BASE_SHA" -- plugins' git 'diff --quiet HEAD~1 HEAD' git 'diff --exit-code main...HEAD' git 'diff --name-only "$SDLC_BASE_SHA"' '! git' 'diff --quiet' git 'diff-tree --cc HEAD'; } >"$f"; python3 plugins/sdlc-lite/scripts/steps.py lint "$f"`
- (guard) `f=$(mktemp -d)/p.md; { printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n'; printf -- '- \140%s %s\140\n' 'test -z "$(git' 'status --porcelain)"'; } >"$f"; out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$f" 2>&1); test $? -eq 1 && printf '%s\n' "$out" | grep -q 'clean porcelain status'`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest >/dev/null 2>&1`
- `grep -qF 'clean whole-tree diff' plugins/sdlc-lite/scripts/steps.py`
- `grep -qF 'script the span calls' plugins/sdlc-lite/scripts/steps.py`

## Step 2: Sync the docs and check.py guard, then gates green
level: L2
### Do
Update the rule in these places:
- `plugins/sdlc-lite/agents/planner.md` rule 13: extend it so a clean whole-tree diff is also forbidden. That means `git diff --quiet` or `git diff --exit-code` with no `-- <pathspec>` and no two-commit range, or an empty `git diff` output. Say that `steps.py split` refuses it as a `plan defect`, using the exact phrase `clean whole-tree diff`. Add that the detector reads only span text, so a clean check hidden inside a script the span calls is not caught and must not be written (exact words `script the span calls`). Keep the existing `clean porcelain status` wording.
- Root `CLAUDE.md`, the `scripts/steps.py` bullet: next to the porcelain clause, add that it also refuses a criterion that requires a clean whole-tree diff (a `--quiet`/`--exit-code` diff or an emptiness test on diff output, with no `--` pathspec and no two-commit range), and that a clean check inside a script the span calls stays out of reach.
- `.claude/agents/sdlc-lite-author.md` line 18: after "one that requires a clean porcelain status", add "or a clean whole-tree diff".
- `plugins/sdlc-lite/scripts/check.py` `PLAN_DEFECT_DOCS`: add the entry `'clean whole-tree diff': ('agents/planner.md', 'scripts/steps.py'),` in exactly that form.

Then run `bash plugins/sdlc-lite/scripts/check.sh` and fix any red that step 1 or this step introduced. No em dashes.
### Acceptance criteria
- `grep -qF 'clean whole-tree diff' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'script the span calls' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'clean whole-tree diff' CLAUDE.md`
- `grep -qF 'clean whole-tree diff' .claude/agents/sdlc-lite-author.md`
- `grep -qF "'clean whole-tree diff': ('agents/planner.md', 'scripts/steps.py')" plugins/sdlc-lite/scripts/check.py`
- (guard) `grep -qF 'clean porcelain status' plugins/sdlc-lite/agents/planner.md`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest >/dev/null 2>&1`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- `check.sh` took 5m21s on this host under load. That is over `split --only`'s default 300s `--guard-timeout`, so step 2's `check.sh` guard may time out. If it does, run split with a larger `--guard-timeout` (for example 900); that is not a plan defect.
- The fixture criteria keep `git` and `diff`/`status` apart as separate printf args (`git 'diff ...'`). That way this plan's own spans never trip the new detector on a later replan or `split --only`. A detector that matches across quote characters would flag them, so the builder must keep the `git\s+diff` word match.
- The flag-or-pass boundary for single-rev diffs (`git diff --quiet HEAD` is flagged) and for negated diffs (`! git diff --quiet` passes) is a design choice. It is pinned by the step 1 criteria.
