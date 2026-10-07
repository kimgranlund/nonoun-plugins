<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: `RESULT_LEVEL_RE` widened to `^[a-z][a-z-]*-L(\d+)`. New read-only `review <task dir>` subcommand (`review_verdict`, `plan_facts`, `review_action`, `cmd_review`), with ordering from `order.py` only. `split` now refuses before any write, via `rejected_by_review`, when the newest plan review counting after the plan says `replan` or `blocked`. Also added: a docstring usage line and `review` section, the split refusal documented, `review` added to argparse, `import json`, and `ok: (r) ...` selftest cases.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: section 3 now runs `steps.py review` and routes on its first line (split / review L1 / replan / stop). It also states the split refusal, that the replan count is per task dir, and that the split-refusal replan goes back through `steps.py review`. The section 4 resume paragraph now sends a task with a plan but no `step-<n>/` back to section 3.
- `plugins/sdlc-lite/agents/conductor.md`: one "How you run roles" bullet for the review route.
- `plugins/sdlc-lite/skills/plan/SKILL.md`: step 5 runs `steps.py review` and reports the outcome.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: `plan-reviewer-L1.md` layout line, and the `plan review: <verdict>: <finding>` entries in the `## Plan review` paragraph.
- `plugins/sdlc-lite/scripts/check.py`: new docstring item 11. The plan-defect route dict gains `plan-reviewer`, `steps.py review`, `## Assumptions`, `unresolved:`, `Missing decisions` and `plan review:` with the file sets from the handoff.
- `docs/references/sdlc-internals.md`: the `steps.py` entry gains `review <task dir>` and the split refusal. The `run.sh` entry gains the plan-reviewer family rule (an Opus planner moves the review to Fable at the same effort).

## Checks
- All 18 non-guard acceptance criteria: PASS. AC1 to AC18 were run in one bash loop with the printf formats requoted. AC9 and AC13 were also run verbatim: AC9 prints `stop`; AC13 split exits 1, prints the refusal, and leaves no `step-1`.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: PASS (rc 0). All new `(r)` review and split-refusal cases print `ok:`.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: `ok: 19 role levels, 9 agents checked`, rc 0.
- (guard) scope diff against `$SDLC_BASE_SHA` (0d15d3f): nothing outside the allow-list, rc 0.
- Negative control for the selftests: a temp copy of steps.py with the split refusal disabled, the L3 rule broken, and the replan-count rule broken. The selftest FAILs, naming the planner L3, verdict-routing and all six split-refusal cases.
- Negative control for check.py: a temp plugin copy with `Missing decisions` removed from chain SKILL.md fails with `skills/chain/SKILL.md: plan-defect route missing "Missing decisions"`, rc 1.
- `python3 plugins/sdlc-lite/scripts/order.py selftest`: PASS.
- `git diff --check`: clean.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: rc 2, drift in `adapters/codex/agents/sdlc-planner-l1.toml`. Same rc 2 and same file at base 0d15d3f in a throwaway worktree, so it was already there. This is not a criterion of this step.

## Notes
- The handoff calls check.py "docstring item 11", but check.py had only items 1 to 10. I added item 11 to the docstring and put the new phrases in the existing `PLAN_DEFECT_DOCS` dict.
- Codex generated-agent drift in `sdlc-planner-l1.toml` existed before this step, most likely from step 1's planner.md change. Regenerating writes files outside this step's scope guard, so I left it. The step that closes this task (or the merge) should run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`.
- `review` reads the plan leniently: a malformed plan is never an error there, because `split` and `lint` refuse it. The planner level is read from the file name and must be exactly L3.
- The `replan`→`stop` count covers every plan-reviewer result in the task dir with Verdict `replan`, not only those after the newest plan, as specified.
- /chain 4.2 mid-build replans still go straight to `steps.py split --only`. The section 3 split-refusal paragraph now routes through `steps.py review`, and it already says "the same handling applies to the split in 4.2". I did not change the 4.2 item text, to stay in scope.
- `bash plugins/sdlc-lite/scripts/check.sh` was not run.
