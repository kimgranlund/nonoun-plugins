<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0519: Model batch for planner, architect, plan-reviewer, verifier, scout, researcher, filer, messenger and conductor

## PR body
## Summary
Records the maintainer's 2026-10-12 model decisions for the roles not yet changed. The change is one model-table edit with one new eval (`.sdlc/evals/0009-model-batch-roles.md`) and one lock. Builder and solo rows are untouched (T-0516, T-0517). The one plan step (builder L3) passed independent verification (verifier L2, verdict pass, no process deviations).

## Changes
- Claude rows in `levels.json`, the mirror `case` rows in `run.sh`, and the `level-rubric/SKILL.md` tables:
  - planner L1 sonnet high, L2 opus medium, L3 opus high.
  - architect L1 opus xhigh.
  - plan-reviewer L1 fable high.
  - verifier L1 opus low.
  - scout L1 sonnet low.
  - researcher L1 sonnet high.
  - filer L1 sonnet low.
- Codex: scout L1 is now `gpt-6.1-sol` low. No other Codex row changed.
- `messenger.md` gets `model: sonnet` and `effort: low`. `conductor.md` gets `model: opus` and `effort: medium`.
- `dispatch.py` `family()` gains two moves: an Opus-built or Opus-solo step gets a Sonnet verifier, and a Fable-planned plan gets an Opus reviewer. `run.sh` mirrors both.
- 8 `T-0519:` selftest cases added in `dispatch.py`. Old pins were updated in `check.py`, `messages.py`, `run-selftest.sh`, `.sdlc/messages/AGENTS.md`, and five docs.
- Two `run-selftest.sh` fixtures changed so they still discriminate now that verifier L1 is on Opus.
- Generated agents (Claude `agents/*.md`, Codex TOML) regenerated.
- New eval `0009-model-batch-roles.md` and `table-lock.json` (cites 0009, previous 0008).

## Verification
- Four pre-edit controls were recorded red before the first edit, then green after. Red covered the Claude table, the Codex table, the messenger and conductor front matter, and `family()`.
- `dispatch.py selftest` shows 8 `ok: T-0519` lines. Before `family()` changed, two cases were observed red (verifier L1 after an opus L1 build, plan-reviewer after a fable planner). The other six were green on the table rows alone.
- The verifier disabled the two new `family()` branches in a temp copy and saw those cases fail, so the cases bite.
- `claude_roles.py generate --check`, `codex_roles.py generate --check`, `check.py` and `check-packaging.py` exit 0. `solo_run.py selftest`, `messages.py selftest`, `codex-selftest.py` and `run-selftest.sh` pass. `evals.py check` passes with the lock citing 0009. `git diff --check` is clean.
- Not verified: live behavior of the new rows (no replay ran), and whether the host honors `effort:` in the messenger and conductor front matter. The full `check.sh` is left to the `fanout.py land` gate.

## Changelog entry
Model table: planner L1 sonnet high, L2 opus medium, L3 opus high; architect L1 opus xhigh; plan-reviewer L1 fable high; verifier L1 opus low; scout L1 sonnet low (Codex scout L1 gpt-6.1-sol low); researcher L1 sonnet high; filer L1 sonnet low; messenger sonnet low; conductor opus medium. The verifier stays off the builder's family, and the plan-reviewer stays off the planner's.

## Follow-ups
- decide: `prices.json` was not recalibrated for the new rows (handoff non-goal); a person must choose whether to open the one follow-up ticket for it.
- note: the Pareto read behind these decisions comes from third-party Artificial Analysis summaries, is unverified, and has no copy in `docs/reports/`; no replay ran.
- note: live host behavior of the new rows and of `effort:` in the messenger and conductor front matter is not proven; the full `check.sh` is left to the `fanout.py land` gate.
