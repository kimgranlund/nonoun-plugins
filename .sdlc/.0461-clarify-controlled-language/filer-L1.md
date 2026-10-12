<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective: step 2 (attempt a5f852571a3946c0ba694a1f5a41b5a5, handoff sha256 ec6a39a6e6e3): 1 of 1 (red) criteria had no pre-edit red control, namely the report-file grep for `docs/reports/2026-10-12-clarify-v3-replay.md`. The control was recorded after step 1's files already differed from HEAD. The step 2 verifier passed the step. That verdict does not clear this deviation.
- Step 1 criterion 7 (the 11 literal strings in SKILL.md) has no pre-edit control in `step-1/red-checkpoint.jsonl`. The builder disclosed this. The verifier showed it red at base by checking `git show 01a8cca7:...SKILL.md` for the missing strings. No `process-deviations.md` exists for step 1.
- The replay result is unverified. The step 2 builder spawned the ten Sonnet replay sub-agents and judged their outputs itself, so this was not an independent run. The report `docs/reports/2026-10-12-clarify-v3-replay.md` says so.
- Both steps have a pass verdict (step 1 verifier L2, step 2 verifier L1). The planner file was truncated in my read, so I did not see the full criteria list for step 1.
- The ticket-level "Done when" asks for `check.sh`, `check.py` and `check-packaging.py` to exit 0. These ran at step 2 only, and the verifier ran them directly. I did not see a step 1 run of `check.sh` or `check-packaging.py`.

## PR title
T-0461: Apply the controlled language to /clarify: grammar, lint rules, evals

## PR body
## Summary
`/sdlc-lite:clarify` now writes its handoff in a controlled grammar with closed vocabularies per slot. `plan_check.py clarify` rejects a handoff that breaks the grammar. The skill prompt and the question wording follow the same rules. The 10 eval cases were rewritten or added to match, and one replay was run and recorded.

## Changes
- `plugins/sdlc-lite/scripts/plan_check.py`:
  - New constants `CLARIFY_VERBS`, `CLARIFY_HEDGE` and `CLARIFY_TYPES`.
  - `CLARIFY_PASS` gains `stopped: `.
  - Five new failing rules: `clarify-hedge`, `clarify-delta`, `clarify-do-verb`, `clarify-rfc2119`, `clarify-default-source`.
  - Two new warnings: `clarify-goal-length`, `clarify-glossary`.
  - `clarify-non-goals` now accepts list form, and `clarify-done` accepts the EARS form.
  - The selftest adds a mutant per rule, a skill drift guard and an eval loop.
- `plugins/sdlc-lite/skills/clarify/SKILL.md`:
  - Rewritten with one identity line, 3 hard gates, pasted input treated as data, and named outcomes including `stopped: <why>`.
  - Six delta types, the question option rules, the handoff grammar template, the `Do verbs:` and `Hedge words:` lines, and a good and a bad `Done when` example.
- `plugins/sdlc-lite/skills/clarify/evals/`: cases 01 to 06 rewritten to the grammar. New 09 (conflicting ask ending in `stopped: <why>`) and 10 (a pasted brief whose instruction is treated as data), each with an `.ask.md` and an `.expected.md`. `README.md` updated to ten cases.
- `docs/specs/doc-standards/core.md`: new `## Controlled handoff words` section naming `plan_check.py`, `CLARIFY_VERBS` and `CLARIFY_HEDGE` as the home. It copies neither list.
- `docs/reports/2026-10-12-clarify-v3-replay.md`: replay report, marked unverified.

The gap delta form keeps the literal `(gap: ...; default: ...)` text. `ask/SKILL.md` and `open-questions/SKILL.md` read it and stay untouched.

## How each was verified
- Step 1 (verifier L2, pass):
  - `plan_check.py selftest` printed `PASS (252 checks)` with an `ok: clarify: <rule>` line for each of the 7 new rules.
  - `clarify --text` printed `FAIL clarify-hedge` for a hedge and `FAIL clarify-delta` for a `vagueness` delta.
  - All ten `.expected.md` files pass `plan_check.py clarify --file`.
  - The verifier's single-line mutations of eval 10 each turned the named rule red: hedge, non-listed verb, a defaulted delta with no `[U]`, lower-case `must not`, `MUST` in Goal, an unlisted delta type, and a non-runnable Done when.
  - Also run: `check.py` rc=0, `prompt_lint.py` 0 errors, `git diff --check` rc=0, and the scope guard.
- Step 2 (verifier L1, pass):
  - The report holds all required keys.
  - `check.py`, `check-packaging.py` (run directly), `git diff --check` and `check.sh` all exit 0.
- Replay: ten fresh-context Sonnet sub-agents, one per case. All ten outputs passed `plan_check.py clarify --file`. The spawning builder also judged them, so the result is unverified.
- Known difference: the replay report lists level estimates that differ from the expected outputs in cases 02, 04, 05 and 06. The skill was not edited for this.

Process deviation (verbatim in substance): the step 2 `(red)` control for the report-file grep was recorded retrospectively, after step 1's files already differed from HEAD. A passing verdict does not clear this.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `/sdlc-lite:clarify` now writes its handoff in a controlled grammar. It has typed deltas, a numbered Do list with a closed verb list, and EARS or runnable Done-when items. `plan_check.py clarify` rejects hedge words, unlisted delta types and Do verbs, misplaced RFC 2119 words, and a `defaulted` delta with no `[U]` and source. It also warns on a long Goal and on glossary aliases. Clarify gains a `stopped: <why>` outcome, and its evals grow to ten cases.

## Follow-ups
- fix-now: Rerun the 10-case replay with an independent model run (the spawning builder judged the first one); the current result is unverified.
- note: Replay level estimates differ from the expected outputs in cases 02, 04, 05 and 06; the skill was left unchanged.
- note: The measured A/B of clarified versus unclarified tickets (K-005 first-pass rate, before 89 of 123) and the first `plan_check.py clarify` refusals-per-handoff baseline are left for a later retro or spike.
