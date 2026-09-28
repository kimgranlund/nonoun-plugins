<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Let `steps.py`'s pinned-sha lint accept exactly the ancestry form `git merge-base --is-ancestor <sha> HEAD` while every other pinned sha is still refused, with selftest cases and docs updated to match.

## Step 1: Exempt the ancestry form in pins_sha, with selftest cases
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py`, change `pins_sha(text)` (around line 539) so that a hex run in the exact shape `git merge-base --is-ancestor <sha> HEAD` no longer counts as a pinned sha. `HEAD` must be a whole word, not `HEAD~1` or `HEAD^`. Any other sha-like hex run in the same span still counts. So the span is still refused when it also holds a second pinned sha (for example `... HEAD && git diff --quiet <sha2> -- src`), when the ancestry form names another ref (`<sha> main`), and when the sha comes second (`--is-ancestor HEAD <sha>`). `git diff <sha>`, `<sha>..HEAD`, `<sha>^`, `<sha>~2` all stay refused. One way to do it: remove each match of the exempt shape from the text, then run the existing `GIT_WORD_RE`/`SHA_RE` test on what is left. Keep the exemption inside `pins_sha` so `lint_steps`, `split`, and `swap` all pick it up. Do not touch the `||`, fixed-set count, clean-status, or `bash -n` checks.

Update the pinned-sha text in the module docstring (the `split` paragraph near line 19 and the `lint` paragraph near line 50) to name the exemption, with the literal words `git merge-base --is-ancestor <sha> HEAD`. Update the lint finding's hint if it helps.

In `selftest()`, next to the `(k3)` cases (around line 1281), add:
- a pass case: a plan holding a `git merge-base --is-ancestor <sha> HEAD` criterion lints `ok` and splits. Its check label must contain `is-ancestor` and `pass`.
- a refuse case: a span holding the ancestry form plus a second pinned sha is refused with `plan defect` and `pins a commit sha`. Its label must contain `is-ancestor` and `refuse`.
Build the fixture shas by concatenation, as `(k3)` does, so the source never holds a literal sha.
### Acceptance criteria
- `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import steps; s = '3f9c' + '2ab'; sys.exit(0 if not steps.pins_sha('git merge-base --is-ancestor ' + s + ' HEAD') else 1)"`
- (guard) `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import steps; s = '3f9c' + '2ab'; sys.exit(0 if steps.pins_sha('git diff --quiet ' + s + ' -- src') else 1)"`
- (guard) `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import steps; s = '3f9c' + '2ab'; sys.exit(0 if all(steps.pins_sha(x) for x in ('git diff --quiet ' + s + '..HEAD -- src', 'git log ' + s + '^', 'git merge-base --is-ancestor ' + s + ' main', 'git merge-base --is-ancestor HEAD ' + s)) else 1)"`
- (guard) `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import steps; s = '3f9c' + '2ab'; t = 'e81d' + '04c'; sys.exit(0 if steps.pins_sha('git merge-base --is-ancestor ' + s + ' HEAD && git diff --quiet ' + t + ' -- src') else 1)"`
- `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import steps; sys.exit(0 if 'is-ancestor' in steps.__doc__ else 1)"`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep '^ok:' | grep 'is-ancestor' | grep -q 'pass'`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep '^ok:' | grep 'is-ancestor' | grep -q 'refuse'`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -1 | grep -qx 'steps selftest: PASS'`

## Step 2: Update the docs and run the gates
level: L1
### Do
Describe the exemption in the same words wherever the pinned-sha rule is stated. Only `git merge-base --is-ancestor <sha> HEAD` passes, and every other pinned sha is still refused, including a span that also holds another sha.
- `plugins/sdlc-lite/agents/planner.md` rule 6: add to the last sentence ("`steps.py split` refuses a criterion that pins a commit sha as a `plan defect`") that `git merge-base --is-ancestor <sha> HEAD` is the one allowed form.
- Repo `CLAUDE.md`, the `scripts/steps.py` bullet: extend the parenthetical "(the word `git` plus a 7 to 40 char hex run with a digit and a letter; compare against `HEAD` instead)" with the exemption. In the Decisions bullet, change only the pinned-sha wording, if any.
- `.claude/agents/sdlc-lite-author.md`: in the plan-defect route line, add the exemption after "one that pins a commit sha fixed at plan time".

This is the gates green step. Run `plugins/sdlc-lite/scripts/check.sh` and fix any red that step 1 or this step introduced.
### Acceptance criteria
- `grep '^6\. ' plugins/sdlc-lite/agents/planner.md | grep -q 'merge-base --is-ancestor'`
- `grep -F 'scripts/steps.py' CLAUDE.md | grep -q 'is-ancestor'`
- `grep -F 'pins a commit sha' .claude/agents/sdlc-lite-author.md | grep -q 'is-ancestor'`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- Commands in the criteria spans are themselves linted by `steps.py split`. They build shas by concatenation (`'3f9c' + '2ab'`), so no span holds a 7-char hex run. A builder who writes a literal sha into a doc example inside a code span in `planner.md` could trip check.py's lint of the merge-step template. Keep doc examples as `<sha>`.
- check.py may guard exact phrases of rule 6 or of the CLAUDE.md steps.py line. If it does, step 2 must keep those phrases while adding the exemption.
