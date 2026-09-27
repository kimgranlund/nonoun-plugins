<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/steps.py: added `ANCESTRY_RE`. `pins_sha` now strips the `git merge-base --is-ancestor <sha> HEAD` form before it runs the sha test. Updated the docstring in the `split` and `lint` paragraphs and the lint hint, and added two `(k3)` selftest cases (is-ancestor pass, is-ancestor refuse).

## Checks
- Criterion 1: the ancestry form is not pinned. rc=0
- Guard: `git diff --quiet <sha> -- src` is still pinned. rc=0
- Guard: `..HEAD`, `^`, `<sha> main`, and `HEAD <sha>` forms are still pinned. rc=0
- Guard: the ancestry form plus a second sha is still pinned. rc=0
- Docstring contains `is-ancestor`. rc=0
- Extra probe: `HEAD~1` and `HEAD^` after the ancestry sha are still pinned. rc=0
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: rc=0.
  - It printed `ok: (k3) is-ancestor <sha> HEAD pass: lint ok and split writes the step` and `ok: (k3) is-ancestor plus a second pinned sha: refuse with plan defect`.
  - The last line was `steps selftest: PASS`.

## Notes
None
