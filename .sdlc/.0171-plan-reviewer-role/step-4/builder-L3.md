<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/adapters/codex/models.json`: added `"plan-reviewer": {"L1": ["gpt-6-astra", "high"]}` after `verifier`. No other line changed.
- `plugins/sdlc-lite/scripts/codex_roles.py`: new `PAIRED = {'verifier': 'builder', 'plan-reviewer': 'planner'}`. `definitions()` makes an `-alternate` profile for every role in `PAIRED`. `resolve()` switches on `order.newest(directory, PAIRED[role])` and that result's `model=` header. Docstrings updated.
- `plugins/sdlc-lite/scripts/codex_exchange.py`: the `-alternate` agent name now applies to any role in `codex_roles.PAIRED` whose resolved model differs from its default.
- `plugins/sdlc-lite/adapters/codex/instructions.md`: the last paragraph now says "a verifier or plan-reviewer alternate profile".
- `plugins/sdlc-lite/adapters/codex/agents/*.toml`: regenerated. The 22 existing profiles changed only in the prelude line. `sdlc-plan-reviewer-l1.toml` and `sdlc-plan-reviewer-l1-alternate.toml` are new.
- `plugins/sdlc-lite/scripts/codex-selftest.py`: added `test_plan_reviewer_alternate_follows_newest_planner` and `test_runner_records_plan_reviewer_alternate_agent`. Existing tests are unchanged.
- `docs/references/codex-role-execution.md`: the count is now 24 (20 base, four alternate), `sdlc-plan-reviewer-l1` is named, the `| Plan reviewer | Astra high | | | | |` row is added, and the alternates paragraph now covers the plan reviewer and what `shared_with_builder` means for it.
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: `sdlc-plan-reviewer-l1` added to the agent-name list.
- `plugins/sdlc-lite/HARNESS-NOTES.md`: the install sentence now says 20 base agents, 24 with the default configuration. The runner paragraph also gets one added sentence saying the plan reviewer is compared with the latest planner result through the same map.

## Checks
All criteria ran from the repo root with `SDLC_BASE_SHA=b185cbc473f6f07a682515049287d2af35350899`. Every one passed:
- c1: `resolve plan-reviewer L1` printed `gpt-6-astra high`.
- c2: with an astra `planner-L3.md` fixture, resolve printed `gpt-6.1-sol high`.
- c3: with a sol `planner-L2.md` fixture, resolve printed `gpt-6-astra high`.
- c4: both plan-reviewer toml files exist.
- c5: the `model = "gpt-6.1-sol"` and `sandbox_mode = "read-only"` greps matched.
- c6: the models.json check exited 0.
- c7: `codex-selftest.py CodexTests.test_plan_reviewer_alternate_follows_newest_planner` passed.
- c8: `codex-selftest.py CodexTests.test_runner_records_plan_reviewer_alternate_agent` passed.
- c9 to c12: the greps for `PAIRED`, `plan-reviewer`, `24 project agent definitions`, the table row, `sdlc-plan-reviewer-l1` and `24 with the default configuration` all matched.
- Guard `codex_roles.py generate --check`: passed.
- Guard `codex-selftest.py` (full suite): passed.
- Guard for changed files outside the allowed list: no stray files.
- Extra: `git diff --check` was clean, `python3 scripts/check-packaging.py` passed, and `python3 plugins/sdlc-lite/scripts/check.py` passed ("19 role levels, 9 agents checked").

## Notes
- The comment above the Codex resolve block in `plugins/sdlc-lite/scripts/run.sh` (around line 217) still describes only the verifier. The code behaves correctly because it calls `codex_roles.py resolve` for every role. run.sh is not in this step's file list, so I left the comment alone; the plan can fix it later.
- The runner selftest sets `SDLC_CODEX_TIMEOUT_SECONDS` to the suite deadline and runs the negative control as a second run (`plan-reviewer-L1-2.request.json`) in the same step dir.
- No commits made.
