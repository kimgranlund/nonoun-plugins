## Task goal
The `steps.py` `||` lint refuses a nonzero-exit right operand that is piped (`test -f a || exit 1 | cat`), because `a || exit 1 | cat` is `a || (exit 1 | cat)` and returns cat's status 0, so the criterion passes when the left side fails.

## Step 1: Stop treating a lone pipe as the end of a fail-fast exit
level: L1
### Do
Edit only `plugins/sdlc-lite/scripts/steps.py`.

1. In `ends_command`, drop the lone `'|'` from the operator tuple, so an `exit N` (or a `{ ...; exit N; }` group) followed by a pipe no longer counts as a fail-fast right operand. Update its docstring (it says "a pipe") to match, and add one clause to the `or_fallback` docstring saying a piped exit stays a finding and why.
2. In the `(k2)` selftest block, add refuse controls for `test -f a || exit 1 | cat` and `test -f a || { echo x; exit 1; } | cat`. Keep every existing pass control passing (`test -f a || exit 1`, the loop and brace forms, `&&` after the exit).
### Acceptance criteria
- `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'test -f a || exit 1 | cat' > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md" 2>&1 | grep -q "plan defect"`
- `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'test -f a || { echo x; exit 1; } | cat' > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md" 2>&1 | grep -q "plan defect"`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
