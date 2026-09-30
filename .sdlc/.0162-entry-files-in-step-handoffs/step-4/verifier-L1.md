<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1 (builder.md, `Read first` replaced with `Read later`): pass. Evidence: I ran the criterion's mutation on a copy of the plugin. The check exited 1 and printed `FAIL agents/builder.md: read-first route missing "Read first"`. The unmutated tree is green (`ok: 18 role levels, 8 agents checked`, rc=0), so the check goes red only on the mutation.
- Criterion 2 (skills/fix/SKILL.md, same mutation): pass. Evidence: the same run exited 1 and printed `FAIL skills/fix/SKILL.md: read-first route missing "Read first"`.
- Do requirements: pass. Evidence: `git diff` of `check.py` shows these three changes.
  - Docstring item 10 names all seven files.
  - The `READ_FIRST_FILES` tuple lists the same seven files.
  - The error text matches the spec.
  - A negative control (`text.replace(READ_FIRST, '')`) follows the same pattern as the other checks. It reports `read-first negative control not flagged` if the detector stops firing.

## Out of scope changes
None. The only tracked change is `plugins/sdlc-lite/scripts/check.py`. The untracked files are run artifacts under `.sdlc/`.

## For the next attempt
None
