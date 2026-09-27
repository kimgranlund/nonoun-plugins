## Task goal
A plan may keep a deliberate ancestry check against a real commit (`git merge-base --is-ancestor <sha> HEAD`) without `steps.py` refusing it, while every other criterion that pins a commit sha is still refused.

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
