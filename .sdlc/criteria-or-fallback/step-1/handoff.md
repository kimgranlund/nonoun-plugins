## Task goal
A criterion with an `||` fallback between checks is refused before any build.

## Step 1: Lint `||` fallbacks in criterion commands
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py`, extend `lint_steps` so it also returns a finding for each command-like criterion span, as returned by `command_spans`, that holds an unquoted `||` operator.
- Test the span's own text, not the placeholder probe.
- Tokenize with `shlex.shlex(text, posix=True, punctuation_chars=True)`, so a `||` inside single or double quotes (such as `grep -E "a||b"`) never counts.
- Spans that fail `bash -n` are already reported. Skip or catch `ValueError` for them.
- One allowance: a `||` whose left operand is exactly `test $# -eq 0` (the empty-argument short circuit that peer merge guards use, as in `set -- $(...); test $# -eq 0 || grep ... "$@"`). The left operand is the tokens since the previous `;`, `&&`, `||`, `|`, or the start.
- Each finding reads `steps: <plan> step <n>: acceptance criterion joins two checks with ||: <span>`. It comes with one indented line saying the fallback can pass on either side, so the criterion cannot fail: split it into separate criteria.
- The existing `lint_or_fail` path appends `PLAN_DEFECT`, so split, `split --only`, and lint all refuse and write nothing.

Update the module docstring's `split` and `lint` paragraphs to say this. Add selftest cases next to (j) and (k), before or with the fix:
- `a || b` is refused by lint and by split, and split writes nothing.
- A quoted `||`, the `test $# -eq 0 ||` form, and an `&&` join all pass.

### Acceptance criteria
- `d=$(mktemp -d) && printf '## Step 1: x\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140grep -q a x \174\174 grep -q b x\140\n' > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- `d=$(mktemp -d) && printf '## Step 1: x\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140grep -q a x \174\174 grep -q b x\140\n' > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md" 2>&1 | grep -q "plan defect"`
- `d=$(mktemp -d) && printf '## Goal\ng\n' > "$d/handoff.md" && printf '## Step 1: x\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140grep -q a x \174\174 grep -q b x\140\n' > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py split "$d" && test ! -e "$d/step-1"`
- (guard) `d=$(mktemp -d) && printf '## Step 1: x\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \140grep -qE "a\174\174b" x\140\n- \140set -- $(ls); test $# -eq 0 \174\174 grep -q x "$@"\140\n- \140grep -q a x && grep -q b x\140\n' > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` prints at least one new `ok:` line covering the `||` refusal and at least one covering the allowed forms (observe the diff of the selftest).
- (guard) `plugins/sdlc-lite/scripts/check.sh` (includes the merge-step block lint in check.py, so the template stays clean)
