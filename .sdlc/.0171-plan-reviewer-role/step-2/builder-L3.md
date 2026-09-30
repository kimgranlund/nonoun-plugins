<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: added the `plan-reviewer:L1) model=opus; effort=high ;;` row, written exactly as the handoff gives it. Added the `plan-reviewer) sect=Verdict; allowed='pass|replan|blocked' ;;` section line and put plan-reviewer on the read-only role list. Added the Claude-only family rule after the verifier swap: when the newest planner result says `model=opus`, the reviewer moves to Fable, effort unchanged. Updated the header comments (required sections, family rules, section-case comment).
- `plugins/sdlc-lite/agents/plan-reviewer.md` (new): frontmatter with `level-rubric` and `checks-that-bite`. The body covers the reading order, the seven named checks, the verdict rules, the rules copied from the verifier, the ban on writing replacement plan text, and the three-section output (`## Verdict`, `## Findings`, `## Missing decisions`).
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: the Codex paragraph now names the plan-reviewer. Added a `## When a plan is reviewed` section after the planner table (when a review is required, `steps.py review`, the Claude and Codex family rules, how each verdict routes). Added the `| plan-reviewer | L1 | Opus high |` row.
- `plugins/sdlc-lite/scripts/order.py`: `RESULT` and `LOOSE` now accept a role of `[a-z][a-z-]*`. Added selftest case (f): ordering follows `runs.jsonl` lines against reversed file times, and role `plan` finds nothing.
- `plugins/sdlc-lite/scripts/check.py`: widened the run.sh case regex, the rubric section-header regex and the single-level row regex to `[\w-]+`. Added a plan-reviewer guard (L1 row plus the exact section line) with an inline negative control.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: four dry-run family-rule cases (no planner, sonnet planner, opus planner newest by `runs.jsonl`, fable planner newest), plus a read-only flag check. Result checks: exit 0 for `pass`, `replan`, `blocked`; exit 3 for `maybe` and for a result with no `## Verdict`. Header comment updated.

## Checks
- All 10 non-guard acceptance criteria: PASS. I ran each one through `bash -c`, with double-quoted printf strings in place of the handoff's single quotes; the commands are otherwise the same.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: `ok: 19 role levels, 9 agents checked`, rc 0.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`, rc 0.
- (guard) `python3 plugins/sdlc-lite/scripts/order.py selftest`: `order selftest: PASS`, including the three (f) cases.
- (guard) scope diff against `$SDLC_BASE_SHA` (8219084): nothing outside the allowed list, rc 0.
- Negative control, check.py (on a temp copy): deleting the section line gives `FAIL scripts/run.sh: plan-reviewer role: no section line ...`, rc 1. Deleting the L1 row gives `no plan-reviewer:L1 row`, rc 1. The base check.py run on the new tree reports `agents/plan-reviewer.md has no run.sh case`, rc 1, which confirms the regex widening was needed.
- Negative control, run-selftest.sh (on a temp copy): with the family rule disabled it fails with `opus planner newest: plan-reviewer should swap to '--model fable --effort high'`. With `blocked` removed from the allowed values it fails with `... blocked': exit 3, want 0`.
- Neighbor checks: `steps.py selftest` rc 0, `board.py selftest` rc 0, `python3 -m traces.selftest` (from scripts/) rc 0, `git diff --check` rc 0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: rc 2 with drift on `sdlc-planner-l1.toml`. The same drift shows at base 8219084 in a throwaway worktree (removed afterwards).

## Notes
- Codex generated-agent parity is not green, and this step did not cause the existing drift. `sdlc-planner-l1.toml` already drifts at base because step 1 changed `agents/planner.md`. There is also no Codex profile or `models.json` entry for plan-reviewer yet. Both are step 4 (Codex generation), which is outside this step's file scope.
- A Codex-backend run of plan-reviewer still depends on `codex_roles.py resolve` knowing the role (step 4). The Claude family rule does not run on the codex backend.
- The Codex sentence in level-rubric says the plan-reviewer "takes the model that map gives for the newest planner result's recorded model". That is the rule recorded in the handoff's Decisions; step 4 implements it.
- The new check.py guard is not listed in the module docstring's numbered list. I kept the change to the regexes and the guard.
