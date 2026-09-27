<!-- role=filer level=L1 model=sonnet effort=medium -->
All good, everything checks out. Step 7 (loose ends) passed. Now writing the final filer report.

## Warnings
None. All seven steps (six planned plus the Loose ends step) built and passed independent verification (builder L2/L3/L1/L2/L2/L2/L2, verifier L1/L2/L1/L1/L1/L1/L1), and `scripts/check.sh` was reported green at each guard point through step 6. Step 7's verifier reproduced the mutation test in an isolated scratch copy and confirmed the new selftest case goes red without the heading rule and green with it.

## PR title
T-0105: Close the three headless background-abandon routes (auto-timeout, task-notification, Monitor)

## PR body
**Summary**

T-0105 asked why the T-0072 background-abandon hook did not stop the builder L2 run reported in T-0103. The archaeologist found no tool-call trace in the peer log, ruled out an explicit Bash `run_in_background: true` and an Agent spawn, and named the best-fitting cause: a foreground Bash call that outlived its default ~120s timeout and was auto-backgrounded by Claude Code, a route no `PreToolUse` hook can see. It also flagged Monitor as a second uncovered candidate. The task's scope was then widened (recorded in the handoff's Intent, folded 2026-09-26) from read-only investigation to fixing all three routes in `plugins/sdlc-lite`, planned by planner L2 into six steps plus a Loose ends step, and built.

**Changes**
1. `scripts/run.sh` now floors `BASH_DEFAULT_TIMEOUT_MS`/`BASH_MAX_TIMEOUT_MS` at 3600000 for every role run (keeping a higher inherited value), matching `bench.sh`.
2. `scripts/run.sh` switches the role launch to `--output-format stream-json --verbose` and, from the resulting per-line JSON log, picks the last result event holding the role's required heading, else the last one whose origin is not `task-notification`, else the last event, so a late task-notification turn can no longer overwrite the real report.
3. `scripts/fanout.py`'s selftest driver stub now asserts it receives both raised timeout env vars (the production code already passed them; only the check was missing).
4. `hooks/block-background.sh` and `hooks/hooks.json` now deny `Monitor` calls in headless sessions, with new fixtures in `scripts/hook-selftest.sh`.
5. `agents/builder.md` and `agents/verifier.md` gained a foreground-only rule ending in the exact phrase "never end the turn while background work runs", enforced by a new `scripts/check.py` check.
6. Docs updated in the same change: `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md`, `agents/conductor.md`, `skills/handoff-format/SKILL.md`, `scripts/check.sh` header, `skills/chain/SKILL.md`.
7. Loose ends: `scripts/run-selftest.sh` gained a case (marked `# heading rule:`) that proves the heading-selection rule on its own, using two non-notification result events where only the heading rule picks the right one; previously the two required step-2 cases both happened to pass even with the rule removed.

**How each was verified**
Each step ran through an independent verifier (never the building model on its own step): step 1 (verifier L1), step 2 (verifier L2), step 3 (verifier L1), step 4 (verifier L1), step 5 (verifier L1), step 6 (verifier L1), step 7/Loose ends (verifier L1). Every verifier confirmed its criteria pass on the built tree and, for the grep/jq criteria, red at pre-build HEAD in a throwaway worktree. Step 3 and step 5 verifiers ran an added negative control (a mutated env var value, a phrase stripped from verifier.md) and confirmed the check goes red. Step 6's verifier confirmed `scripts/check.sh` passes in full (selftests, shellcheck, plugin validate) on the built tree. Step 7's verifier independently reproduced the builder's mutation test in an isolated scratch copy of the repo (the new case alone, not the whole suite): unmutated run passes, and replacing the heading-pick line with `null` makes it fail exit 3 as expected. No verifier logged a fail, replan, or plan-defect tag on any step.

## Changelog entry
Fixed three routes where a headless role run could end with "Waiting for the background job to notify." instead of its real report: Bash auto-backgrounding a call past its default timeout (run.sh now raises the timeout floor), a trailing task-notification turn overwriting the real result (run.sh now picks the correct result event from a stream-json log, proven by its own dedicated selftest case), and an unguarded Monitor call in headless sessions (now denied by block-background.sh).

## Follow-ups
- decide: step 2's fix (picking the correct result event from a `stream-json` log) rests on the assumption that `claude -p --output-format stream-json --verbose` emits one `result` event per turn, including task-notification turns; this is proven only against stubs, never against a real run that ends in a task notification (both the planner's Risks and step 2's builder Notes flag it, and a live repro was explicitly out of scope for this task) — worth deciding whether to schedule that live confirmation.
- note: the Monitor tool name in the `PreToolUse` payload is assumed to be exactly `"Monitor"` (matching the hooks.json matcher and block-background.sh's check); no live probe covers it, same as the planner's Risks and the T-0076 non-goal it inherits.
- note: step 7's builder accidentally ran `git checkout` on `run.sh` mid-mutation-test, discarding its uncommitted steps 1-6 changes, and restored it from a manual `/tmp` backup taken before the mutation; the verifier independently confirmed the restore was exact (matching diff stats and intact heading-pick and timeout-floor lines), but the near-loss is worth knowing about if this pattern recurs.
