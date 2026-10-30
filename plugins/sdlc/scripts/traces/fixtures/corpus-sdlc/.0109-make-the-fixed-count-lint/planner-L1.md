<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Make `steps.py` `fixed_set_count` ignore a bare shell assignment such as `n=26` and still flag real comparisons.

## Step 1: Skip bare assignments in COMPARE_RE
level: L2
### Do
In `plugins/sdlc/scripts/steps.py`, change the bare `=` alternative in `COMPARE_RE` so it matches only when whitespace precedes it, as in `[ "$x" = 26 ]`. That means `(?<=\s)=` replaces the plain `=`. The `-eq`/`-ne`/`-ge`/`-gt`/`-le`/`-lt`, `==` and `!=` alternatives stay unchanged.

Add a `steps.py selftest` case after (k4) and before (k5). It uses spans that combine a count tool and a glob, `ls` or `find`:
- One with `n=26` as the only literal, and no comparison, must pass `lint` and `split`.
- A second `n=26` span must still be flagged. It compares against `n=26` with `-eq 26`, so it still hits the fixed-number finding. This proves the lint still fires.
- The existing (k4) refusal case stays as it is.

Update the two places that describe the comparison operators, the `steps.py` docstring (the `lint` paragraph, "(-eq -ne -ge -gt -le -lt = == !=)") and the `steps.py` bullet in `CLAUDE.md` Layout if it lists them. State that a bare `name=value` assignment is not a comparison. Touch no other lint or selftest case.
### Acceptance criteria
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc/scripts'); import steps; sys.exit(0 if not steps.fixed_set_count('n=26; ls x* | wc -l') else 1)"`
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc/scripts'); import steps; sys.exit(0 if steps.fixed_set_count('test \"\$(ls x* | wc -l)\" -eq 26') else 1)"`
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc/scripts'); import steps; sys.exit(0 if steps.fixed_set_count('[ \"\$(ls x* | wc -l)\" = 26 ]') else 1)"`
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc/scripts'); import steps; sys.exit(0 if steps.fixed_set_count('n=26; ls x* | wc -l | grep -q x; [ \"\$n\" == 26 ]') else 1)"`
- `python3 plugins/sdlc/scripts/steps.py selftest` exits 0 and its output contains a new case for the `n=26` assignment.
- `scripts/check.sh` exits 0 (run from `plugins/sdlc/`).
- `git diff --name-only HEAD` lists only `plugins/sdlc/scripts/steps.py` and, if edited, `CLAUDE.md`.

The first criterion is red at HEAD, because `n=26` is flagged there. Criteria 2 and 3 are red only if the fix breaks them; they check that real comparisons still get flagged. The selftest case does not exist yet, so the selftest criterion is red for now as well.

## Risks
- A comparison written as `[ "$x"=26 ]` without spaces is invalid shell anyway, so it stays unflagged. `$((n==26))` is still caught by `==`.
- Criteria 2 and 3 are guards for the finished state, not red now. They are stated as regression checks, not `(guard)`.
