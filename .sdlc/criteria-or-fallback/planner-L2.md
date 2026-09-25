<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
`steps.py split` and `steps.py lint` refuse, as a plan defect, any acceptance criterion command that joins two checks with `||`, and the planner rules ban such fallbacks explicitly.

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

## Step 2: Ban `||` fallbacks in the planner rules and sync the docs
level: L1
### Do
In `plugins/sdlc-lite/agents/planner.md`, under `## Criteria that can pass`, add one numbered rule after rule 4. It says:
- Never join two checks with `||` in one criterion, because a fallback passes when either side matches, so the criterion can hold at HEAD and never fail. State each check as its own criterion.
- `steps.py split` refuses a `||` join as a `plan defect`.
- The only allowed form is the empty-argument short circuit `test $# -eq 0 || ...`.

Renumber the later rules and keep their text. In `CLAUDE.md` (repo root), in the `scripts/steps.py` Layout bullet, change "refuses, with `plan defect` on stderr, a plan whose acceptance criterion command spans do not parse under `bash -n`" so it also says "or join two checks with `||` (an unquoted `||`, except after `test $# -eq 0`)". Use the literal phrase `join two checks with`. In `.claude/agents/sdlc-lite-author.md`, add the same phrase to the plan-defect route bullet (line 18), naming the split lint's `||` check, so the author agent stays in sync with CLAUDE.md.
### Acceptance criteria
- `grep -qE '[|]{2}' plugins/sdlc-lite/agents/planner.md`
- `grep -q 'join two checks with' CLAUDE.md`
- `grep -q 'join two checks with' .claude/agents/sdlc-lite-author.md`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`

## Risks
- The `test $# -eq 0 ||` allowance is inferred from the ticket. The merge-step template in this repo has no `||` today, so the exact peer form may differ. If peers use a different short-circuit shape, the allowance may need widening.
- `shlex` with `punctuation_chars` treats `$(` loosely, so a `||` inside a command substitution is flagged too. That is intended, since it is still a fallback, but it could refuse an unusual legitimate span.
- Once step 1 lands, `split --only 2` lints this whole plan with the new rule. Every span here writes `||` as the octal escape `\174\174` inside quotes for that reason. A builder who rewrites a criterion with a literal unquoted `||` would trip it.
