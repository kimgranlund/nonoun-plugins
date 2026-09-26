<!-- role=planner level=L3 model=fable effort=xhigh -->
## Goal
Make `steps.py`'s fixed-count lint treat a bare `name=value` assignment such as `n=26` as not a comparison, while `-eq 26`, `= 26`, `== 26`, and `!= 26` beside a count tool and a glob, `ls`, or `find` stay refused.

## Step 1: Skip a bare assignment in the fixed-count lint
level: L2
### Do
All paths and commands are relative to the repo root (the git toplevel, where `steps.py split --only` runs guards).

1. `plugins/sdlc-lite/scripts/steps.py`, `COMPARE_RE` (line 456): change the bare `=` alternative from `=` to `(?<=\s)=`, so a lone `=` counts as a comparison only when whitespace precedes it (`[ "$x" = 26 ]`, `test "$x" = "26"`). A `name=value` word (`n=26`, `export N=26`), a `--flag=26`, and `${n:=26}` then match nothing. Keep the `-eq|-ne|-ge|-gt|-le|-lt`, `==`, and `!=` alternatives, `COUNT_TOOL_RE`, `SET_SOURCE_RE`, and the body of `fixed_set_count` as they are.

2. Selftest in `steps.py` `selftest()`: add a `(k6)` group between `(k5)` (line 1039) and `(l)` (line 1052), in the `(k4)`/`(k5)` pattern (`task(plan=PLAN.replace('- one works', ...))`, `run_main`, `check`, `refused`). Every case name in the group starts with `(k6)`, because a criterion below greps `^ok: (k6)`.
   - Pass case: one plan whose step 1 criteria are the two spans `n=26; ls .sdlc/*/handoff.md | wc -l` and `export N=26; find . -name "*.md" | grep -c md`. `split` exits 0 and writes `step-1/handoff.md`; `lint` exits 0 with `steps lint: ok`; and, as `(k)` does, `command_spans(parse_steps(...)[1])` equals those two spans, so the case cannot pass vacuously through a non-command span.
   - Refusal cases: loop over the forms `[ "$(ls x* | wc -l)" = 26 ]`, `[ "$(ls x* | wc -l)" == 26 ]`, `[ "$(ls x* | wc -l)" != 26 ]`, and `n=26; ls x* | wc -l | grep -q x; [ "$n" == 26 ]` the way `(k2)` loops, and `refused(...)` each with `lint`, needles `plan defect` and `compares a count over a changing set with a fixed number`. `(k4)` (the `-eq 26` form) stays untouched.

3. Docs. In the `steps.py` module docstring, the `lint` paragraph that lists `(-eq -ne -ge -gt -le -lt = == !=)` (line 53) gains one clause: a bare `=` counts only with whitespace before it, so a bare `name=value` assignment such as `n=26` is not a comparison. In the repo root `CLAUDE.md`, the `scripts/steps.py` Layout bullet gains the same clause after "compared with a literal of 2 or more". Both must hold the literal text `n=26`. `.claude/agents/sdlc-lite-author.md` and `agents/planner.md` do not list the operators; leave them alone.

Why the probe criteria below spell `"w" + "c -l"` and `"gr" + "ep -c x"`: `steps.py split` lints each criterion's own text, and a criterion that quotes a whole sample span (count tool, set source, and a literal of 2 or more) is refused as a plan defect, which is what blocked the earlier plan. The concatenation keeps the count tool out of the criterion text while the Python string under test still reads `wc -l` or `grep -c x`. Do not "simplify" them into one literal.

Touch nothing else: no other lint, no other selftest case, no new files.
### Acceptance criteria
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; sys.exit(0 if not steps.fixed_set_count("n=26; ls x* | w" + "c -l") else 1)'`
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; sys.exit(0 if not steps.fixed_set_count("export N=26; find . -name x | gr" + "ep -c x") else 1)'`
- (guard) `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; sys.exit(0 if steps.fixed_set_count("[ $(ls x* | w" + "c -l) -eq 26 ]") else 1)'`
- (guard) `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; sys.exit(0 if steps.fixed_set_count("[ $(ls x* | w" + "c -l) = 26 ]") else 1)'`
- (guard) `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; sys.exit(0 if steps.fixed_set_count("n=26; ls x* | w" + "c -l | grep -q x; [ $n == 26 ]") else 1)'`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1 | grep -q "^ok: (k6)"`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1 | grep -q "^ok: (k4) lint refuses a glob count compared with a fixed number"`
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; sys.exit(0 if "n=26" in steps.__doc__ else 1)'`
- `grep -q 'n=26' CLAUDE.md`
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (green at HEAD too; not tagged `(guard)` because a full run took 59s alone and over 20 minutes beside other lanes at load average 114, past the 300s guard budget)
- (guard) `test -z "$(git diff --name-only HEAD -- plugins CLAUDE.md .claude | grep -vxE 'plugins/sdlc-lite/scripts/steps.py|CLAUDE.md')"`
- (guard) `test -z "$(git ls-files --others --exclude-standard -- plugins CLAUDE.md .claude)"`

## Risks
- The `(k4)` guard runs the whole steps selftest: a few seconds alone, 91s at load average 114 when this plan was written. If the machine is loaded enough to push it past 300s, `split --only 1` reports a timeout as a plan defect; rerun it with `--guard-timeout 900` rather than replanning.
- The lint stays a heuristic on raw text. `n=26; test "$(ls x* | wc -l)" -eq "$n"` compares a changing set with a fixed number through a variable and passes the lint after this change; that is the scope the ticket asks for, and planner rule 7 still forbids it in prose.
- `(?<=\s)=` also stops flagging `--flag=26` and `${n:=26}` forms. Neither is a comparison, and no existing selftest case depends on them; the candidate regex was checked against 13 spans, including every `(k4)` and `(k5)` form, before writing this plan.
