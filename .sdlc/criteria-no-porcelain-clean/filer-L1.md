<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0125: Refuse criteria that require a clean porcelain status

## PR body
### Summary
A builder never commits, so its own changes keep `git status --porcelain` dirty. A criterion that requires a clean porcelain status can therefore never pass. This came from gen-ui's T-0232, which staged 538 baselines and had such a criterion. This change makes `steps.py lint` and `split` refuse those criteria as a `plan defect`. It also gives the planner a rule to check `git diff` plus untracked files instead.

### Changes
- `scripts/steps.py`:
  - New predicate `requires_clean_status()`. It flags one span that holds `git status` in porcelain or short form (`--porcelain`, `--short`, or a standalone `-s`), has no `--` pathspec, and tests for emptiness (`-z`, a compare with `0` or `""`, or `! ... | grep -q`).
  - `lint_steps` reports a flagged span and tells the planner to use `git diff --quiet HEAD -- <path>` plus `git ls-files --others --exclude-standard -- <path>`. `split` and `swap` refuse through the same path.
  - The module docstring's `lint` paragraph now describes the check.
  - New selftest case `(k6)`.
- `agents/planner.md`: new rule 13 under "Criteria that can pass".
- `scripts/check.py`: `'clean porcelain status'` added to `PLAN_DEFECT_DOCS`, so the phrase must stay in `planner.md` and `steps.py`.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: the new refusal is added to the `steps.py` lint lists.

A path-scoped status (`git status --porcelain -- src`) stays allowed, because it can be met.

### How each step was verified
Both steps passed an independent verifier.
- Step 1 (verifier L1, Sonnet):
  - The three flagged spans (`test -z "$(git status --porcelain)"`, `test -z "$(git status -s)"`, and `... | wc -l ... -eq 0`) each get a finding.
  - The four allowed spans get none.
  - `steps.py selftest` and `check.py` pass.
  - The `(k6)` and phrase greps pass.
  - The verifier ran the criterion at HEAD and it failed there, so it can go red.
  - Two extra spans were flagged as expected (`! git status --short | grep -q .` and `test "$(git status --porcelain)" = ""`). A bare `git status --porcelain` and `test -n ...` were not.
- Step 2 (verifier L1, Opus):
  - All five greps pass on the built tree and fail at HEAD.
  - `check.py` passes, and it reports the phrase missing from `planner.md` when run against HEAD's `planner.md`.
  - `steps.py selftest` passes.
  - Diffs checked against the Do.

Note on step 2's builder: it did not run separate greps for the phrase in `check.py`, `CLAUDE.md` and the author file. The verifier ran them.

## Changelog entry
- Planner criteria no longer require a clean `git status --porcelain` or `-s`. `steps.py lint` and `split` now refuse an emptiness test on an unscoped porcelain or short status as a `plan defect`, and planner rule 13 says to check `git diff` plus untracked files instead (T-0125).

## Follow-ups
- Extend the clean-status lint in steps.py to catch a whole-tree clean check not written as a `git status --porcelain` emptiness test (for example `git diff --quiet && ...` over the whole tree, or a script that hides it). The detector only matches span text.
- Decide whether path-scoped `git status --porcelain -- <path>` emptiness criteria should be flagged when the path is one the step itself changes. Today they pass the lint and could still never pass.
