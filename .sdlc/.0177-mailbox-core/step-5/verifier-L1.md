<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I ran it, exit 0. The output has `messages selftest: PASS` at line 385, `skip: shellcheck not installed` (allowed), and `ok: plugin validate`. It examines the full current tree, so it bites.
- `python3 scripts/check-packaging.py`: pass. Evidence: exit 0, output `PASS: catalog parity, identity, skill routes, hook isolation and context links`.
- `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: pass. Evidence: exit 0. `SDLC_BASE_SHA` is 5efe084, equal to HEAD, so the diff is empty and this check examined nothing. I repeated the same check over steps 1 to 4 (`7cb47d3^..HEAD`): exit 0, so it also holds on the real code.
- Em-dash guard on lines added to tracked files: pass. Evidence: the inner grep found no match (rc=1, so the `!`-negated guard is true). The diff is empty here, so this is also vacuous against the base. Over steps 1 to 4 (`7cb47d3^..HEAD`) I counted 0 added lines containing an em dash.
- Em-dash guard on new untracked files: pass. Evidence: exit 0. No untracked files exist outside `.sdlc`.
- Scope guard (changed and untracked files restricted to the allowed list): pass. Evidence: the output is empty and `test -z` returned 0. Nothing changed outside `.sdlc`.

Builder claims checked against the tree:
- "No changes": `git status --short` shows only untracked files under `.sdlc`.
- "`SDLC_BASE_SHA` equals HEAD": `git log` shows HEAD is 5efe084, matching the base-sha file.
- "All gates green": I reran `check.sh` and `check-packaging.py` myself; both exit 0.

## Out of scope changes
None. `git status --short` shows only untracked step artifacts under `.sdlc`, which the guards exclude.

## For the next attempt
None
