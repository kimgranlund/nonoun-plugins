## Task goal
Criteria never require a clean porcelain status, which a no-commit builder can't meet.

## Step 1: steps.py lint refuses a clean porcelain status criterion
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py`:
- Add a predicate `requires_clean_status(text)` next to `pins_sha` and `fixed_set_count`. It returns True when all of these hold in one span:
  - It holds `git status` (the word `git`, then `status` as a word).
  - It uses a porcelain or short form: `--porcelain` (with or without `=v1`/`=v2`), `--short`, or a standalone `-s`.
  - No ` -- <pathspec>` follows the status. A path-scoped status, such as "this step did not touch src/", can be met and stays allowed.
  - It tests for emptiness: `-z`, a comparison (`-eq`, `=`, `==`) with the literal `0` or with `""`, or a leading `!` over a `grep -q`.
- Call it in `lint_steps` for every span that parses. On a match, append the finding `steps: <plan> step <n>: acceptance criterion requires a clean porcelain status: <span>`. Follow it with a second line saying that builders never commit, so the step's own changes keep the status dirty and the criterion can never pass. The same line tells the planner to check `git diff --quiet HEAD -- <path>` plus untracked files (`git ls-files --others --exclude-standard -- <path>`) instead.
- Since `split` and `swap` already call `lint_steps`, they refuse through the same path.
- Extend the `lint` paragraph of the module docstring to describe the new check.
- Add selftest case `(k6)` after `(k5)`, following the `(k3)`/`(k4)` pattern:
  - `split` and `lint` refuse, writing nothing, with the needles `plan defect` and `clean porcelain status`. Use each of `test -z "$(git status --porcelain)"`, `test -z "$(git status -s)"` and `test "$(git status --porcelain | wc -l)" -eq 0`.
  - An ok-spans case passes `lint` with `steps lint: ok` for `git diff --quiet HEAD -- src`, `test -z "$(git ls-files --others --exclude-standard -- src)"`, `test -z "$(git status --porcelain -- src)"` and `! git rev-parse -q --verify MERGE_HEAD`.

The selftest case and the fix land in this one step.
### Acceptance criteria
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; b = chr(96); st = "git " + "status"; bad = ["test -z \"$(" + st + " --porcelain)\"", "test -z \"$(" + st + " -s)\"", "test \"$(" + st + " --porcelain | wc -l)\" -eq 0"]; fs = [steps.lint_steps("p", {1: "### Acceptance criteria\n- " + b + s + b + "\n"}) for s in bad]; sys.exit(0 if all(any("clean porcelain status" in f for f in x) for x in fs) else 1)'`
- (guard) `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; b = chr(96); st = "git " + "status"; ok = ["git diff --quiet HEAD -- src", "test -z \"$(git ls-files --others --exclude-standard -- src)\"", "test -z \"$(" + st + " --porcelain -- src)\"", "! git rev-parse -q --verify MERGE_HEAD"]; fs = [steps.lint_steps("p", {1: "### Acceptance criteria\n- " + b + s + b + "\n"}) for s in ok]; sys.exit(0 if not any(fs) else 1)'`
- `grep -q "(k6)" plugins/sdlc-lite/scripts/steps.py`
- `grep -qF "clean porcelain status" plugins/sdlc-lite/scripts/steps.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
