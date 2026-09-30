<!-- role=scout level=L1 model=haiku effort=low -->
## Map
- plugins/sdlc-lite/agents/verifier.md:33: Out of scope changes section where dependents would be reported
- plugins/sdlc-lite/agents/planner.md:22,26-27: Scope rules and scope decision handling during replan
- plugins/sdlc-lite/agents/planner.md:11-31: Criteria rules covering which files must be checked and how
- plugins/sdlc-lite/agents/conductor.md:25: Scope decision routing to `steps.py widen` for widening scope
- plugins/sdlc-lite/agents/builder.md:7: Builder constraint: do not widen scope
- plugins/sdlc-lite/scripts/steps.py:7,145-167: `widen` command for manual scope widening by conductor
- plugins/sdlc-lite/scripts/steps.py:200-210: `find_plan()` and `read_goal()` — entry points for plan analysis
- plugins/sdlc-lite/scripts/steps.py:289-292: `criteria_lines()` — extracts acceptance criteria from step blocks
- plugins/sdlc-lite/scripts/order.py: Utility for finding newest result files by recorded order

## Entry points
1. **Planner** (plugins/sdlc-lite/agents/planner.md line 7): Reads handoff and builds steps; would need logic to detect changed contracts and pull dependents into scope criteria before writing steps
2. **Verifier** (plugins/sdlc-lite/agents/verifier.md line 2): Independently checks steps and inspects actual diffs (`git diff`, `git status`) for out-of-scope changes; would detect changed contracts and trace their dependents there
3. **Conductor** (plugins/sdlc-lite/agents/conductor.md line 25): Routes scope decisions; would pass detected dependents to `steps.py widen`
4. **steps.py split** (plugins/sdlc-lite/scripts/steps.py line 1-89): Parses and validates plans; could validate that dependent files are in scope when a contract changes

## Not found
- No code that identifies which files are "shared contracts" (catalog entries, types, exported APIs)
- No code that traces dependents of a changed contract (tests, fixtures, lint fixtures that import/use it)
- No code that automatically includes dependents in a step's scope criterion or alerts the planner
- No cross-file import analysis or dependency graph traversal
- No pattern matching for test files, fixture files, or lint-fixture files relative to contract changes
