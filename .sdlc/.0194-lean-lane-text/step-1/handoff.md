## Task goal
Add the lean lane text and the coarse-step rule to the chain skill and the planner contract, plus a steps.py lint warning, so a size-S or M ticket can run in one or two coarse steps.

## Step 1: steps.py lint warning for non-coarse lean-eligible plans
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets are `plugins/sdlc-lite/scripts/steps.py` (a new function `lean_warnings(plan, task_dir, steps)`, `cmd_lint`, the lint entry of the module docstring, and `selftest`) and `docs/references/sdlc-internals.md` (the `## scripts/steps.py` paragraph, in the sentence ``lint <planner.md | task dir>` runs the same check and writes nothing``).

Settled decisions:
- **Eligibility.** A plan is eligible ("meets the lean plan conditions") only when all of these hold. Each one reuses an existing helper, so the facts stay where they already live.
  - `result_level(plan)` is 1 or 2. Catch `Fail` and treat it as not eligible: a file named `handoff.md` or `base-lint.md` raises today (steps.py:935-939). This keeps `/fix`'s step-handoff lint and the selftest `base-lint.md` case unwarned.
  - `plan_facts(plan)` returns no `unresolved:` item, every level is in 1..3, and no title starts with `Merge `.
  - `len(order.ordered(task_dir, 'planner')) < 2`, which means no replan.
  - `task_dir / 'handoff.md'` has no line equal to `## Plan review`. A missing handoff counts as none.
  - These are the plan-time facts `review_action` uses (steps.py:1213-1242). Ticket size and the AGENTS.md-owner condition are not computable here. T-0197 owns `steps.py lane` and the `review_required()` extraction, so this step does not extract `review_required()` and does not add `lane`.
- **Warnings.** Each warning is one stderr line. Exact formats:
  - more than two steps: `steps lint: warning: <plan>: <k> steps; the coarse-step rule allows at most 2 in a plan that meets the lean plan conditions (agents/planner.md, Coarse steps)`
  - a step whose `### Acceptance criteria` holds exactly one top-level list item (count `criteria_lines(block)` lines matching `^[-*] `): `steps lint: warning: <plan> step <n>: one acceptance criterion; the coarse-step rule merges it into a neighboring step (agents/planner.md, Coarse steps)`
- **Where warnings appear.** `cmd_lint` prints the warnings only after `lint_or_fail` passes. Stdout stays exactly `steps lint: ok` and the exit code stays 0. `split`, `swap`, and `widen` print no warnings: leave `lint_steps` and `lint_or_fail` unchanged, because split, swap, and widen share them.
- **Docstring.** Extend the `lint` entry so `steps.py -h` includes the literal `steps lint: warning:` and the eligibility list.
- **Internals doc.** Add one sentence to the sdlc-internals.md lint description naming `steps lint: warning:` and both triggers.
- **New selftest cases.** Print exactly these labels through `check(...)`:
  - `(lean) lint warns on a lean-eligible plan with 3 steps`: a `planner-L2.md` with three steps at L1 to L3 and two criteria each. Expect rc 0, stdout `steps lint: ok`, and stderr holding `steps lint: warning:` and `3 steps`.
  - `(lean) lint warns on a one-criterion step`: the existing `PLAN` fixture. Expect stderr to name step 1 and step 2.
  - `(lean) no warning for a planner L3 plan, a step at L4, a merge step, a replan, a ## Plan review line, or an unresolved: assumption`: six task dirs, each with err == '' and rc 0. The replan dir holds two planner files; the Plan review dir's `handoff.md` holds a `## Plan review` line.
  - `(lean) no warning for a two-step plan with two criteria per step`
- **Existing check (j).** It asserts `err == ''` for a task dir with two planner files. It stays green because a replan is not eligible. Do not weaken it.

Contract dependents:
- `/fix` lints `step-1/handoff.md`, which `result_level` excludes.
- `check.py`'s merge-block lint is a file target named for the merge block, so it is not eligible.
- No hook or other script reads lint stderr: `git grep -n "steps.py lint"` shows only docs and skills.

Depends on: none. Focused check: `python3 plugins/sdlc-lite/scripts/steps.py selftest`.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lean) lint warns on a lean-eligible plan with 3 steps"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lean) lint warns on a one-criterion step"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lean) no warning for a planner L3 plan, a step at L4, a merge step, a replan, a ## Plan review line, or an unresolved: assumption"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lean) no warning for a two-step plan with two criteria per step"`
- `d=$(mktemp -d) && printf "## Step 1: a\nlevel: L1\n### Acceptance criteria\n- x\n" > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d" 2>&1 >/dev/null | grep -qF "steps lint: warning:"`
- (guard) `d=$(mktemp -d) && printf "## Step 1: a\nlevel: L1\n### Acceptance criteria\n- x\n" > "$d/planner-L2.md" && out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$d" 2>/dev/null) && test "$out" = "steps lint: ok"`
- `python3 plugins/sdlc-lite/scripts/steps.py -h | grep -qF "steps lint: warning:"`
- `grep -qF "steps lint: warning:" docs/references/sdlc-internals.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/steps.py -e docs/references/sdlc-internals.md | grep -q .`
