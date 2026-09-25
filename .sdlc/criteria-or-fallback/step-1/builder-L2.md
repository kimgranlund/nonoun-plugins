<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/steps.py: added `or_fallback` (a shlex tokenizer that finds an unquoted `||`, with `test $# -eq 0 ||` allowed). `lint_steps` now reports a "joins two checks with ||" finding, which comes with an indented explanation line. Updated the `split`/`lint` docstring paragraphs and added the (k2) selftest cases after (k).

## Checks
- Criterion 1: the `||` plan makes lint exit nonzero. Passed (c1=0).
- Criterion 2: lint output contains "plan defect". Passed.
- Criterion 3: split refuses and no step-1 is created. Passed.
- Criterion 4 (guard): a quoted `||`, the `test $# -eq 0 ||` form, and an `&&` join get `steps lint: ok` with exit 0. Passed.
- Criterion 5 (guard): `steps.py selftest` exits 0.
- Criterion 6: selftest prints three new `ok: (k2) ...` lines. Two cover the `||` refusal (split and lint) and one covers the allowed forms.
- Criterion 7 (guard): `plugins/sdlc-lite/scripts/check.sh` exits 0.

## Notes
Tokenizing sets `commenters = ''` so that `$#` is not read as the start of a comment, and `whitespace_split = True`. Any all-punctuation token that contains `;`, `|` or `&&` resets the left operand. This matters because shlex joins `);` into one token.
