## Task goal
`steps.py split --only N` runs that step's `(guard)` criteria against the current tree before writing its handoff, and refuses with a `plan defect` line when a guard is red now, so a plan whose guard cannot pass is caught before the build instead of by the verifier.

Done when: `split --only N` executes each runnable `(guard)` command span of step N (skipping spans that reference `HEAD^1` or contain a `<placeholder>`, each under a timeout), refuses and writes nothing on a red or timed-out guard with `plan defect` as the last stderr line naming the criterion, the full `split` (no `--only`) and `lint` still execute nothing, `steps.py selftest` proves each case (red guard refuses, green guard passes, HEAD^1 and placeholder guards skipped, timeout refuses, full split does not execute), and the docs that describe `split` (the `steps.py` usage text, CLAUDE.md, `.claude/agents/sdlc-lite-author.md`, `/chain` 4.2 and the plan-defect decision) say so. `scripts/check.sh` passes.

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
