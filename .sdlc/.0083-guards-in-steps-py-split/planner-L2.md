<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `steps.py split --only N` refuse, with a `plan defect:` last line that names the changed paths, whenever running a step's `(guard)` criteria changed the git work tree, and keep the docs and check.py in step with that rule.

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

## Step 2: Keep docs and check.py in step with the new refusal
level: L2
### Do
Describe the new refusal with the exact phrase `changed the work tree` in each of these places:
- `CLAUDE.md`:
  - Layout `scripts/steps.py` bullet: `--only N` also refuses when its guards changed the work tree, tracked or untracked, versus before they ran, and names the paths. Outside git there is no check. A tree already dirty before is fine.
  - Decisions "A plan defect goes to a replan" bullet: a guard that changed the work tree is a plan defect, and the `split --only` guard run is a code gate for it.
  - Systems line naming the three code gates.
- `.claude/agents/sdlc-lite-author.md`: the Plan-defect route bullet.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: section 3 and 4.2 text on `--only N`, i.e. a red guard or a guard that changed the work tree.
- `plugins/sdlc-lite/agents/planner.md`: rule 1 under "Criteria that can pass". Add one sentence saying `steps.py split --only N` runs every `(guard)` and refuses one that changed the work tree, so a guard must be side-effect free. Do not touch the `merge-step` block.

In `plugins/sdlc-lite/scripts/check.py`, add a `PLAN_DEFECT_DOCS` entry `'changed the work tree': ('agents/planner.md', 'skills/chain/SKILL.md', 'scripts/steps.py')`. That way check.py fails if the phrase drops out of any of those files.
### Acceptance criteria
- `grep -q "changed the work tree" CLAUDE.md`
- `grep -q "changed the work tree" .claude/agents/sdlc-lite-author.md`
- `grep -q "changed the work tree" plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q "changed the work tree" plugins/sdlc-lite/agents/planner.md`
- `grep -q "'changed the work tree'" plugins/sdlc-lite/scripts/check.py`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -n1 | grep -qx 'steps selftest: PASS'`
- (guard) `test -z "$(git status --porcelain --untracked-files=all -- plugins/sdlc-lite/skills/handoff-format)"`. This shows the merge-step template copy was not touched, and check.sh's identity check on the planner.md copy covers the other side.

## Risks
- Porcelain status only sees a change of state. If a guard edits a file that was already modified, the status stays ` M` and the change goes unseen. Hashing the contents of dirty paths would close that gap. The Constraints accept porcelain, so the builder may add hashing but it is not required.
- Ignored files, such as `*.log`, `.running`, and `__pycache__`, are invisible to the check. That is intended, but it means a guard that writes only ignored files passes.
- In a real task tree, a guard that runs `scripts/check.sh` must leave the tree clean. That holds today: I ran it and the porcelain status did not change. If a future check writes a tracked or unignored file, every such guard will refuse.
- The step 1 fixture criteria leave `mktemp -d` dirs behind in the system temp dir. They are harmless but not cleaned up.
