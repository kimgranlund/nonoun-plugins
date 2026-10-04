## Task goal
Add `steps.py lane`, extract `review_required()`, and write the lane and skip history to skips.md.

## Step 1: Extract review_required() from review_action
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Target is `plugins/sdlc-lite/scripts/steps.py`: a new function `review_required(plan, task_dir)` in the `# --- review ---` section, plus `review_action`, `lean_warnings`, and `selftest`. Line numbers moved after T-0194. `review_action` now starts at steps.py:1275 and inlines its reasons at about 1288-1305. `lean_warnings` (steps.py:949-974) holds a second copy of the same conditions.

Settled decisions:
- **Signature and return.** `review_required(plan, task_dir)` returns a tuple `(unresolved, why)`.
  - `unresolved` is the first element of `plan_facts(plan)`.
  - `why` holds the reasons a plan review is required. Use these exact strings, in this order, moved verbatim from `review_action`:
    1. `f'{pname} is a planner L3 plan'` when `result_level(plan) == 3`
    2. `'a step is at builder L4 or L5'`
    3. `'the plan has a merge step'`
    4. `f'{n} planner results (a replan)'` when `n = len(order.ordered(task_dir, 'planner')) >= 2`
    5. `'handoff.md holds ## Plan review'` when `task_dir/handoff.md` has a line whose rstrip equals `## Plan review`
  - `pname` is `os.path.basename(plan)`.
  - It lets `result_level`'s `Fail` propagate. Callers pass only names that carry a level.
  - Its docstring says that review, lane, and lint's lean warnings read this one rule.
- **review_action.** Keep the structure check, the `plans` list, and the newest-plan pick. Replace the inline `plan_facts` call and the `why` building with `unresolved, why = review_required(plan, t)`. Keep the `stop` on `unresolved[0]` with the same reason text, and keep everything after it unchanged. Output must stay byte-identical. At HEAD, a fixture with `planner-L3.md` and `planner-L3-2.md` (one step `Merge x` at `level: L4`) and a handoff holding `## Plan review` prints this reason line:
  `reason: a plan review is required (planner-L3-2.md is a planner L3 plan; a step is at builder L4 or L5; the plan has a merge step; 2 planner results (a replan); handoff.md holds ## Plan review) and none counts after planner-L3-2.md`
- **lean_warnings.** Keep its `result_level(plan) in (1, 2)` check, with `Fail` meaning not eligible. Replace its inline unresolved, level, `Merge `, replan, and `## Plan review` checks with `unresolved, why = review_required(plan, task_dir)`, and return `[]` when either is non-empty. This is equivalent: `plan_facts` levels are 1 to 5, so "not in 1..3" equals "4 or 5". Keep the two warning texts unchanged.
- **New selftest case.** Place it right after the existing `(r)` review cases, reusing `r_task`, `r_plan`, and `r_review`. Print exactly this label through `check(...)`: `(r) review_required returns the unresolved items and every reason review prints, in order`. It asserts three things:
  - On the fixture above (runs order `planner-L3.md`, `planner-L3-2.md`), `review_required` returns `([], [the five strings above, in order])`.
  - `review`'s second stdout line on that fixture equals the reason line above.
  - A `planner-L2.md` built with `r_plan(tail='\n## Assumptions\n- unresolved: which db\n')` returns `(['unresolved: which db'], [])`.
- Every existing `(r)` and `(lean)` case stays green unchanged. Do not weaken them.

Contract dependents:
- No other file calls `review_action` or `lean_warnings` (`git grep` finds them only in steps.py).
- The check.py phrase route for `steps.py review` reads only docs text, which this step does not touch.

Depends on: none. Focused check: `python3 plugins/sdlc-lite/scripts/steps.py selftest`.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (r) review_required returns the unresolved items and every reason review prints, in order"`
- `python3 -c 'import inspect, sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; s = inspect.getsource(steps.review_action); sys.exit(0 if "review_required(" in s and "builder L4 or L5" not in s else 1)'`
- `python3 -c 'import inspect, sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; s = inspect.getsource(steps.lean_warnings); sys.exit(0 if "review_required(" in s and "Merge " not in s else 1)'`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `! grep -qF "—" plugins/sdlc-lite/scripts/steps.py`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/steps.py | grep -q .`
