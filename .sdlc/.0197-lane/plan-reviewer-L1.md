<!-- role=plan-reviewer level=L1 model=fable effort=high -->
## Verdict
replan

## Findings
- step 2: interfaces: the Do fixes the size read as `tickets.parse(handoff text).get('size')`, but `tickets.parse` returns `None` for text with no front matter, so that expression raises `AttributeError` on the "no front matter" handoff that the step's own selftest label `(lane) before planning, size alone decides: ... no size full` requires. The Do says a missing front matter "gives no size" but names an expression that cannot deliver it. Evidence: `plugins/sdlc-lite/scripts/tickets.py:227-232` (`if not m: return None`); `python3 -c "import tickets; tickets.parse('## Goal\nx').get('size')"` → `AttributeError: 'NoneType' object has no attribute 'get'`.
- plan: goal coverage: the handoff's Done-when requires "affected guidance is updated". Step 2 makes `steps.py lane` write a new file `<task>/skips.md` into every ticket folder, but the task-folder layout record, `plugins/sdlc-lite/skills/handoff-format/SKILL.md:10-35` (which enumerates `handoff.md`, `design.md`, `decompose/`, `runs.jsonl`, `step-<n>/`, and every other file a task dir may hold), is not touched by any step, and step 3's scope guard excludes it. Evidence: `grep -n skips plugins/sdlc-lite/skills/handoff-format/SKILL.md` → no match; planner-L3.md:242 lists only `skills/sdlc-lite/SKILL.md`, `skills/chain/SKILL.md`, `scripts/steps.py`, `docs/maintenance/sdlc-internals.md`, and generated TOMLs; T-0198 and T-0199 handoffs name no handoff-format edit either, so the listing goes stale with no owner.

## Missing decisions
None
