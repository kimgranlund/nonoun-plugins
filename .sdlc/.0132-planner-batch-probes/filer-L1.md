<!-- role=filer level=L1 model=sonnet effort=medium -->
Both steps pass. Both verifiers confirm. Task done, measured 8 turns < 11.5. No plan defects noted beyond the initial replan of planner-L2 (superseded by L3).

## Warnings
None.

## PR title
T-0132: Planner batches its criterion probes into one Bash call per step

## PR body
Summary:
- Rule 1 in `plugins/sdlc-lite/agents/planner.md` now tells the planner to run all of a step's criterion probes (including rule 11's un-negated guard runs) in one Bash call, one `bash -c` per criterion, printing each criterion's label, exit code, and at most the first 5 lines of output. This cuts the extra Bash round-trips that 0.7.0's per-criterion probing added, without touching read-only probing or the red-now/green-guard semantics.

Changes:
- `plugins/sdlc-lite/agents/planner.md`: inserted the batching sentence after rule 1's first sentence; every other sentence of rule 1, rule 11, and the Merge steps section are unchanged.
- `plugins/sdlc-lite/scripts/check.py`: added `'one Bash call': ('agents/planner.md',)` to `PLAN_DEFECT_DOCS` so the phrase is guarded.
- `CLAUDE.md`: extended the Decisions bullet on criterion probing to describe the batched call, label, exit code, and first-5-lines behavior.
- No model, effort, or run.sh level-table changes; no other agent file touched.

How each was verified:
- Step 1 (rule + check.py + CLAUDE.md edit): verifier L1 confirmed all 5 new-behavior greps and all 5 unchanged-rule guards pass, checked the 5 new-behavior greps were red at `$SDLC_BASE_SHA` (discriminating check), ran the negative control on the check.py entry itself (phrase stripped, entry kept → `FAIL agents/planner.md: plan-defect route missing "one Bash call"`; phrase restored → pass) since the builder had skipped that control, and confirmed rule 1's and rule 11's existing sentences are verbatim preserved. `check.py` clean in the built tree.
- Step 2 (gates green + live measurement): verifier L1 confirmed `check.sh` passed clean (no T-0133 SIGPIPE flake this run), and independently reran the live-measurement criteria: a live planner L2 run against a copy of T-0137's handoff in `/tmp/t0132-probe/` recorded 8 turns (below the 11.5-average target) and 7 Bash tool calls (down from this ticket's own 8), cost $0.6159388, all matching the builder's Notes exactly. Confirmed nothing under `t0132-probe` is tracked or untracked in the repo.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Planner rule 1 now batches all of a step's criterion probes (including guard runs) into one Bash call per step, printing each criterion's label, exit code, and first 5 output lines, cutting planner L2 turns (measured 8 vs. the prior 11.5 average).

## Follow-ups
None.
