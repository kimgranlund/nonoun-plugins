<!-- role=filer level=L1 model=sonnet effort=medium -->
Both steps passed verification. Now drafting the filer output.

## Warnings
None.

## PR title
T-0138: Lint compound criteria with a trailing redirect or pipe

## PR body
### Summary
Extends the `steps.py` `||` lint (used by `split` and `lint`) to catch an unlinted `||` fallback inside a compound criterion (`for`/`while`/`until`/`if`/`{`) that ends in a trailing redirect or pipe after its closing keyword, such as `while read x; do ...; done < f`. Previously such spans were not recognized as commands at all, so a fallback like `test -f x || echo m` inside one slipped past the lint.

### Changes
- `plugins/sdlc-lite/scripts/steps.py`: `is_command` now also treats a compound span as a command when its closing keyword (`done`/`fi`/`}`) is followed by a trailing redirect (`<`, `>`, `>>`, `<<<`, an fd-prefixed form, `&>`) or a single pipe `|` (not `||`), provided a `;`, `&`, or newline precedes the closing keyword — this keeps prose like "for each file done < f" a non-command while catching the real compound forms. Docstring and usage text updated with the literal phrase "trailing redirect or pipe". Four new `(k2)` selftest cases added.
- `CLAUDE.md`: the `scripts/steps.py` bullet now states that compound criteria are linted when they end in a trailing redirect or pipe after the closing keyword (example: `done < f`).
- No other doc needed updating (sdlc-lite-author.md, planner.md, handoff-format don't describe this coverage).

### How verified
- Step 1 (builder L2, verifier L1, pass): all 7 acceptance criteria verified pass/fail across the built tree versus a throwaway worktree at pre-build HEAD (each check flips from failing to passing, confirming it actually bites). `scripts/check.sh` exits 0 on the built tree. The verifier flagged one Do-prose inconsistency (the literal "whitespace precedes closing keyword" spec would have broken the guard case) which the builder resolved by requiring `;`/`&`/newline before the keyword instead — verifier confirmed this is the only choice under which all criteria including the guard hold, and did not fail it since no acceptance criterion itself was violated.
- Step 2 (builder L1, verifier L1, pass, gates green): both gate guards (`check.sh`, `steps.py selftest`) already passed with step 1's changes, no further fixes needed. Verifier independently confirmed by mutating `is_command` in a throwaway worktree (forcing `return False`) and observing both gates go red exactly on the new mechanism (3 selftest cases fail), then confirmed they pass clean on the built tree.

## Changelog entry
Fixed: the `steps.py` `||` lint now also catches an unlinted fallback inside a compound criterion (`for`/`while`/`until`/`if`/`{`) that ends in a trailing redirect or pipe after its closing keyword, such as `while read x; do ...; done < f`.

## Follow-ups
- decide: a compound span followed by `&&`, `;`, or `||` after its closing keyword (for example `done || echo x`) stays unlinted by design in this change; the planner's Risks section flags this as a likely follow-up scope if such forms show up in practice.
