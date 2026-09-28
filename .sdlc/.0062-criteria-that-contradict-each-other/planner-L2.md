<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `steps.py split --only N` run step N's `(guard)` criteria against the current tree before it writes anything, and refuse as a `plan defect` if a guard is red or times out. The full `split` and `lint` still execute nothing, and the selftest and docs cover the new behavior.

## Step 1: Run guard criteria in `split --only`, with timeout and selftest
level: L3
### Do
Edit `plugins/sdlc-lite/scripts/steps.py` only.

1. Guard detection. Add a helper, for example `guard_spans(block)`, that walks `criteria_lines(block)`, so it already skips ``` fences and applies only under `### Acceptance criteria`. It keeps only lines whose text, after the leading list marker (`- ` or `* `) and whitespace, starts with `(guard)`. That is the marking `agents/planner.md` and the merge-step template already use. From those lines it returns the command-like spans, using the same span extraction and `is_command` test as `command_spans`. Reuse that logic so both paths see the same spans.
2. Skip rules. A guard span is skipped, never run, when its text contains `HEAD^1` or matches `PLACEHOLDER_RE`, meaning it holds a `<placeholder>`.
3. Execution. Only for `split` with `--only`, after `lint_or_fail`, after the `--only` missing-step check, and after the role-output (superseded) check, but before any write, run each remaining guard span of each chosen step:
   - Run it with `bash -c -- <span>`, with `stdin=subprocess.DEVNULL` and output captured.
   - Set `start_new_session=True`, and on timeout kill the whole process group with `os.killpg`, so a pipeline grandchild cannot keep the pipes open and hang the call.
   - Working directory: the git toplevel of the task dir (`git -C <task dir> rev-parse --show-toplevel`). Outside a git work tree, use the task dir itself.
   - Timeout: a new `split` option `--guard-timeout SECONDS`, default 300.
4. Refusal. A guard that exits nonzero or times out makes `split` raise `Fail`, so it exits 1 and writes nothing. The stderr text has:
   - one line per red guard: `steps: <plan> step <n>: (guard) criterion is red now (exit <rc>)` or `(timed out after <s>s)`, then `: <span>`;
   - a few indented lines of the guard's stderr/stdout tail;
   - a last line that starts with `plan defect:` and names the criterion, for example `plan defect: step <n> red guard: <span>; replan this step (/chain 3)`.

   Keep the existing `PLAN_DEFECT` constant for the lint refusal unchanged.
5. Full `split` (no `--only`) and `lint` never call the guard runner.
6. Update the module docstring (the usage text) for the `split` entry:
   - `--only N` runs that step's `(guard)` command spans before writing;
   - spans that reference `HEAD^1` or hold a `<placeholder>` are skipped;
   - each guard runs under `--guard-timeout` (default 300 seconds) from the git toplevel of the task dir (else the task dir);
   - a red guard or a timeout refuses with a `plan defect:` last line and writes nothing;
   - full `split` and `lint` never execute a span.

   The docstring must contain the literal words `red guard`, `guard-timeout`, `HEAD^1`, and `placeholder`.
7. Selftest. Add cases whose check names start with `(n) `, at least these six:
   1. `--only` with a red guard refuses, writes nothing, and the last stderr line starts with `plan defect:` and holds the span.
   2. `--only` with a green guard writes the handoff.
   3. A `HEAD^1` guard is skipped. Use one that would be red if run: the tmp task dir is not a git repo.
   4. A `<placeholder>` guard is skipped. Also one that would be red if run.
   5. A timeout refuses and writes nothing. Use `sleep 30` with `--guard-timeout 1`, so the test stays fast.
   6. Full `split` and `lint` execute nothing. Use a guard `touch <absolute tmp path>` and check the marker is absent afterwards.

   Use absolute tmp paths so no guard touches the repo.

### Acceptance criteria
- `` d=$(mktemp -d) && printf '%s\n' '---' 'id: T-1' '---' '' '## Goal' 'g' > "$d/handoff.md" && printf '%s\n' '## Step 1: x' 'level: L1' '### Acceptance criteria' '- (guard) `test -e /nonexistent-sdlc-guard-x`' > "$d/planner-L1.md" && ! python3 plugins/sdlc-lite/scripts/steps.py split "$d" --only 1 2>"$d/err" && tail -n1 "$d/err" | grep -q '^plan defect:.*nonexistent-sdlc-guard-x' && test ! -e "$d/step-1" ``
- `` d=$(mktemp -d) && printf '%s\n' '---' 'id: T-1' '---' '' '## Goal' 'g' > "$d/handoff.md" && printf '%s\n' '## Step 1: x' 'level: L1' '### Acceptance criteria' '- (guard) `sleep 30`' > "$d/planner-L1.md" && ! python3 plugins/sdlc-lite/scripts/steps.py split "$d" --only 1 --guard-timeout 1 2>"$d/err" && tail -n1 "$d/err" | grep -q '^plan defect:.*sleep 30' && test ! -e "$d/step-1" ``
- `python3 plugins/sdlc-lite/scripts/steps.py split --help | grep -q -- --guard-timeout`
- `test "$(python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -c '^ok: (n) ')" -ge 6`
- `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import steps; d = steps.__doc__; sys.exit(0 if all(w in d for w in ('red guard', 'guard-timeout', 'HEAD^1', 'placeholder')) else 1)"`
- (guard) `` d=$(mktemp -d) && printf '%s\n' '---' 'id: T-1' '---' '' '## Goal' 'g' > "$d/handoff.md" && printf '%s\n' '## Step 1: x' 'level: L1' '### Acceptance criteria' "- (guard) \`touch $d/ran\`" '- (guard) `test -e /nonexistent-sdlc-guard-x`' > "$d/planner-L1.md" && python3 plugins/sdlc-lite/scripts/steps.py split "$d" >/dev/null && python3 plugins/sdlc-lite/scripts/steps.py lint "$d" >/dev/null && test -f "$d/step-1/handoff.md" && test ! -e "$d/ran" ``
- (guard) `` d=$(mktemp -d) && printf '%s\n' '---' 'id: T-1' '---' '' '## Goal' 'g' > "$d/handoff.md" && printf '%s\n' '## Step 1: x' 'level: L1' '### Acceptance criteria' '- (guard) `test -d /`' '- (guard) `git diff --quiet HEAD^1 HEAD`' '- (guard) `test -e <tmp>/nope`' > "$d/planner-L1.md" && python3 plugins/sdlc-lite/scripts/steps.py split "$d" --only 1 >/dev/null && test -f "$d/step-1/handoff.md" ``
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) Running `plugins/sdlc-lite/scripts/check.sh` from the repo root exits 0.

## Step 2: Document the guard run and add it to check.py's doc guard
level: L2
### Do
Describe the new behavior everywhere `split` is described, using the literal phrase `red guard` in each place:
- `CLAUDE.md` (repo root):
  - the `scripts/steps.py` Layout bullet: `split --only N` runs that step's `(guard)` command spans under `--guard-timeout` (default 300s) from the git toplevel, skipping `HEAD^1` and `<placeholder>` spans, and refuses on a red guard or timeout with a `plan defect:` last line; full `split` and `lint` execute nothing;
  - the Systems line that counts the code gates;
  - the "A plan defect goes to a replan" decision paragraph, which must say a red guard in `split --only` is a plan defect.
- `.claude/agents/sdlc-lite-author.md`: the plan-defect route bullet names the `split --only` red guard as a source.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: item 2 of section 4, the line starting `2. builder Status blocked`, says `--only N` runs that step's guards and that a red guard refusal is a `plan defect` handled like the section 3 split refusal. Optionally mention it in section 3 too, noting that the full split there executes nothing.
- `plugins/sdlc-lite/scripts/check.py`: add `'red guard': ('skills/chain/SKILL.md', 'scripts/steps.py')` to `PLAN_DEFECT_DOCS`.

Keep every existing phrase that check.py already guards: `plan defect`, `Plan review`, `no new findings`.
### Acceptance criteria
- `test -z "$(grep -L 'red guard' CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/skills/chain/SKILL.md)"`
- `grep 'A plan defect goes to a replan' CLAUDE.md | grep -q 'red guard'`
- `grep '^2\. builder Status blocked' plugins/sdlc-lite/skills/chain/SKILL.md | grep -q 'red guard'`
- `grep -q "'red guard'" plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) Running `plugins/sdlc-lite/scripts/check.sh` from the repo root exits 0.

## Risks
- Step 2's `split --only 2` in /chain 4.2 already runs the new code on this plan. Its only runnable guard is the steps.py selftest. The check.sh line is written in prose and is not executed, so a slow `check.sh` (about 34s now) cannot hit the timeout there.
- Killing only the direct child on timeout can hang `subprocess.run` when a grandchild holds the pipes. The Do requires a process-group kill; if the builder skips it, the timeout criterion may hang instead of failing.
- The default working directory (the git toplevel of the task dir) and the 300s default are planner choices, because the handoff left them open. A guard written for a different cwd would go red falsely.
- A guard that has side effects, even though the planner prompt forbids them, now really runs during `split --only`.
