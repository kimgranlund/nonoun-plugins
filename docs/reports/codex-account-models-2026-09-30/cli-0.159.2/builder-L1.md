<!-- role=builder level=L1 model=gpt-6-astra effort=low -->
## Status
done

## Changes
value.txt — set to exactly `value: 2` with one trailing newline.

## Checks
- Required Python byte predicate — printed `fixture PASS`.
- Python check of `git show HEAD:value.txt` — base bytes rejected; printed `base rejection PASS`.
- `git diff --name-only` — only value.txt.
- `git status --short` — only ` M value.txt`.
- `git diff -- value.txt` — confirmed the intended change.

## Notes
Changes remain uncommitted. External repository untouched; independent maintenance review remains for the verifier.
