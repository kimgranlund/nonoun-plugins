## Task goal
The `steps.py` `||` lint refuses only real fallbacks (a criterion that passes when either side passes) and stops refusing the fail-fast `||` forms that peer repos' plans actually use, so a valid plan is never sent to a replan as a plan defect.

## Step 1: Allow fail-fast `||` and lint compound-command criteria in steps.py
level: L3
### Do
Edit `plugins/sdlc-lite/scripts/steps.py`. Nothing else changes in this step.

1. Change `or_fallback` (and `OR_ALLOWED_LEFT` if needed) so an unquoted `||` passes in two cases:
   - Its left operand is exactly `test $# -eq 0`. This case is kept as it is.
   - Its right operand is a nonzero exit. That means `exit N` with N a nonzero integer literal, ending at `;`, `&&`, `|`, `}`, a newline, the end of the span, or `done`/`fi` after a `;`. It also means a brace group `{ ...; exit N; }` whose last command is such an exit.
   
   Every other unquoted `||` is still a finding. That includes `|| exit 0`, bare `|| exit`, `|| true`, `|| false`, `|| return N`, `|| echo ...`, `|| { echo x; }`, and `|| { exit 1; echo x; }` (the exit is not last), plus `grep a x || grep b x`. The check stays pure text: it executes nothing and writes nothing.

2. Fix a gap found while planning. Loop criteria are never linted today, because `is_command` judges only the head token, and `for`, `while`, `until`, `if` and `{` are not in `BUILTINS`. A criterion like `for p in a b; do grep -q a "$p" || grep -q b "$p"; done` passes lint unchecked.
   - Make `is_command` treat a span as a command when its head is `for`, `while` or `until` and the span ends with `done`, when its head is `if` and the span ends with `fi`, or when its head is `{` and the span ends with `}`.
   - Prose that starts with those words, such as `for each changed file`, must stay non-command. Otherwise it would reach `bash -n` and be refused.

3. Update the `lint` usage text (around line 36) and the `or_fallback` docstring to state the new allowance. Use the literal phrase ``nonzero `exit` `` and say why it is allowed: a nonzero exit fails the criterion when the left side fails, so it cannot pass on either side.

4. Extend the `(k2)` selftest with both kinds of control:
   - Must pass: `for f in a b; do test -f "$f" || exit 1; done` and `for id in P1 P2; do grep -qE "x" "$f" || { echo "missing $id"; exit 1; }; done`. Also `test -f a || exit 1`, the existing quoted `||` spans, the `test $# -eq 0` span, and `&&`.
   - Must be refused: `grep -q a x || grep -q b x`, `test -f a || exit 0`, `test -f a || true`, a loop with `|| echo MISSING "$p"`, and a loop with `grep -q a "$p" || grep -q b "$p"`.
   - Add a prose control: a `for each changed file` span stays a non-command span.
### Acceptance criteria
- `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'test -f a || exit 1' > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'grep -q x a || { echo missing; exit 1; }' > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'for p in a b; do test -f "$p" || echo MISSING "$p"; done' > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'for p in a b; do grep -q a "$p" || grep -q b "$p"; done' > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- `grep -q 'nonzero .exit' plugins/sdlc-lite/scripts/steps.py`
- (guard) `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'for f in a b; do test -f "$f" || exit 1; done' > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- (guard) `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'grep -q a x || grep -q b x' > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- (guard) `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'test -f a || exit 0' > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- (guard) `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'test -f a || true' > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- (guard) `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'set -- $(ls); test $# -eq 0 || grep -q x "$@"' > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- (guard) `d=$(mktemp -d) && printf '## Goal\ng\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140%s\140\n## Risks\nNone\n' 'for each changed file' > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- In the `(k2)` block of `plugins/sdlc-lite/scripts/steps.py`, the verifier can see new selftest cases for each pass and refuse control listed in Do item 4.
