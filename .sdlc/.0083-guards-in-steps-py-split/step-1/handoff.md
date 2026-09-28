## Task goal
`steps.py split --only N` refuses, with a `plan defect:` last line, when running a step's `(guard)` criteria changed the git work tree (tracked or untracked files), so a side-effecting guard is caught by code, not only by the planner prompt. The selftest proves the refusal fires and that a guard which changes nothing still passes.

## Step 1: Detect guard side effects in steps.py split --only
level: L3
### Do
In `plugins/sdlc-lite/scripts/steps.py`:
- In `run_guards`, when `guard_cwd(task_dir)` resolved to a git toplevel, take a snapshot of the work tree before the first runnable guard and another after the last. Use `git -C <toplevel> status --porcelain --untracked-files=all -z`, or an equivalent that sees both tracked and untracked changes. Outside a git work tree, take no snapshot and add no new refusal. That is the selftest's existing task-dir case.
- Snapshot entries present only after the guards, or changed between the two snapshots, count as "changed by the guards". A tree that was already dirty before is fine as long as the guards leave its status unchanged. Never undo anything.
- If the guards changed the tree, raise `Fail`:
  - One line per changed path, e.g. `steps: <plan> step <n>: (guard) criteria changed the work tree: <path>`.
  - Then a last line that starts `plan defect:`, contains the phrase `changed the work tree`, names every changed path, and ends `; replan this step (/chain 3)`.
  - Red guards and a changed tree may both happen. Report both, with a single `plan defect:` last line.
  - Nothing is written. The check stays before the handoff write loop in `split`.
- Full `split` and `lint` still execute nothing.
- Extend the module docstring usage text for `--only N` to describe the new refusal, using the phrase `changed the work tree`.
- Add selftest cases tagged `(o)` (`check('(o) ...', ...)`). Each builds a throwaway `git init` repo under the selftest tmp dir, with `-c user.name=t -c user.email=t@t` for any commit. Cover at least:
  - A guard that creates an untracked file refuses, writes no step handoff, and has a `plan defect:` last line naming the path.
  - A guard that modifies a committed tracked file refuses the same way.
  - A guard that changes nothing passes and writes the handoff.
  - A tree already dirty before the guards, with guards that change nothing, passes.

  The existing `(n)` cases stay unchanged and keep passing.
### Acceptance criteria
- A guard that creates an untracked file in a git repo refuses: `t=$(mktemp -d) && git -C "$t" init -q && mkdir -p "$t/.sdlc/x" && printf "## Goal\ng\n" > "$t/.sdlc/x/handoff.md" && printf "## Step 1: x\nlevel: L1\n### Do\nd\n### Acceptance criteria\n- (guard) \x60touch sdlc-guard-made\x60\n" > "$t/.sdlc/x/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py split "$t/.sdlc/x" --only 1 2>"$t/err" && tail -n1 "$t/err" | grep -q "^plan defect:.*sdlc-guard-made" && test ! -e "$t/.sdlc/x/step-1/handoff.md"`
- A guard that modifies a tracked file refuses: `t=$(mktemp -d) && git -C "$t" init -q && echo a > "$t/tracked.txt" && git -C "$t" add tracked.txt && git -C "$t" -c user.name=t -c user.email=t@t commit -qm i && mkdir -p "$t/.sdlc/x" && printf "## Goal\ng\n" > "$t/.sdlc/x/handoff.md" && printf "## Step 1: x\nlevel: L1\n### Do\nd\n### Acceptance criteria\n- (guard) \x60echo b >> tracked.txt\x60\n" > "$t/.sdlc/x/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py split "$t/.sdlc/x" --only 1 2>"$t/err" && tail -n1 "$t/err" | grep -q "^plan defect:.*tracked.txt" && test ! -e "$t/.sdlc/x/step-1/handoff.md"`
- (guard) A guard that changes nothing passes in a git repo: `t=$(mktemp -d) && git -C "$t" init -q && mkdir -p "$t/.sdlc/x" && printf "## Goal\ng\n" > "$t/.sdlc/x/handoff.md" && printf "## Step 1: x\nlevel: L1\n### Do\nd\n### Acceptance criteria\n- (guard) \x60test -d .sdlc\x60\n" > "$t/.sdlc/x/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py split "$t/.sdlc/x" --only 1 && test -f "$t/.sdlc/x/step-1/handoff.md"`
- (guard) A tree that was dirty before the guards passes: `t=$(mktemp -d) && git -C "$t" init -q && mkdir -p "$t/.sdlc/x" && printf "## Goal\ng\n" > "$t/.sdlc/x/handoff.md" && echo pre > "$t/already-dirty" && printf "## Step 1: x\nlevel: L1\n### Do\nd\n### Acceptance criteria\n- (guard) \x60test -f already-dirty\x60\n" > "$t/.sdlc/x/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py split "$t/.sdlc/x" --only 1 && test -f "$t/.sdlc/x/step-1/handoff.md"`
- `test "$(python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -c '^ok: (o)')" -ge 3`
- `grep -q "changed the work tree" plugins/sdlc-lite/scripts/steps.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -n1 | grep -qx 'steps selftest: PASS'`
- (guard) `test "$(python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -c '^ok: (n)')" -ge 7`
- Observable: `git diff HEAD -- plugins/sdlc-lite/scripts/steps.py` shows no edit to the existing `(n)` selftest case bodies.
