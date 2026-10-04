<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0194: Lean lane text and coarse-step rule in chain and planner

## PR body
### Summary
This adds the lean lane text and the coarse-step rule, so a size-S or M ticket can run in one or two coarse steps. The text does not claim a lane the code cannot compute. `steps.py lane` is not added, because T-0197 owns it. The lint warning only warns and never refuses.

### Changes
- `plugins/sdlc-lite/scripts/steps.py`: new `lean_warnings(plan, task_dir, steps)`. `steps.py lint` now prints a `steps lint: warning:` line on stderr after a clean lint when a lean-eligible plan has more than two steps, or has a step with one acceptance criterion.
  - A plan counts as eligible when all of these hold: planner L1 or L2, no `unresolved:` assumption, every step level 1 to 3, no `Merge ` step, no replan, and no `## Plan review` line in the handoff.
  - `steps.py -h` now carries the warning literal through an argparse epilog with `RawDescriptionHelpFormatter`.
  - Four new `(lean)` selftest cases cover the positive and negative paths.
- `docs/maintenance/sdlc-internals.md`: the `steps.py` lint sentence now names the warning, the eligibility conditions and both triggers.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: new `## Lean chain` section before `## 1. Brief`. It states the lean conditions and the mandatory full-chain triggers, links the planner's coarse-step rule, and says lean close-out always runs the filer. It also notes that no script computes the lane yet.
- `plugins/sdlc-lite/agents/planner.md`: new `## Coarse steps` section with the "one step per independently verifiable outcome" rule, placed before `## Criteria that can pass`.
- `plugins/sdlc-lite/scripts/check.py`: docstring item 13 and a `LEAN_LANE` guard. Each phrase and file pair has its own negative control.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l1.toml`, `sdlc-planner-l2.toml`, `sdlc-planner-l3.toml`: regenerated with `codex_roles.py generate`.

### Verification
Both steps got an independent verifier verdict of pass, from the sonnet L1 verifier.
- Step 1 (`steps.py` warning):
  - The four `(lean)` selftest labels pass and the selftest ends `steps selftest: PASS`.
  - A one-criterion L2 plan prints the warning on stderr, and stdout stays exactly `steps lint: ok`.
  - The warning check can go red: the same lint at the base SHA prints no warning.
  - A one-criterion `handoff.md` (the `/fix` contract) lints with no warning.
  - The `-h` and `sdlc-internals.md` greps match, and only the two allowed files changed.
- Step 2 (text, guard, Codex agents):
  - The greps on chain `SKILL.md`, `planner.md` and `sdlc-planner-l2.toml` pass.
  - Negative control, planner phrase removed: `check.py` fails with `lean lane text missing "independently verifiable outcome"`.
  - Negative control, `## Lean chain` removed: `check.py` fails with `lean lane text missing "## Lean chain"`.
  - The em dash guard and the scope guard pass.
- Ticket gates, run by the builder and re-run by the verifier:
  - `bash plugins/sdlc-lite/scripts/check.sh`: pass, ending `ok: plugin validate`. `shellcheck` is not installed, so that step was skipped.
  - `python3 scripts/check-packaging.py`: pass.
  - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass.
  - `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: pass (208 tickets, roadmap current).
  - `git diff --check`: pass.

No live host run was performed. Model and effort defaults are unchanged, and there is no version bump or push.

## Changelog entry
- Added the lean lane text to the chain skill and the coarse-step rule to the planner contract. `steps.py lint` now warns, never refuses, when a lean-eligible plan has more than two steps or a step with one acceptance criterion. `check.py` guards the new text, and the Codex planner agents are regenerated.

## Follow-ups
- note: Lean eligibility in `steps.py lint` covers only plan-time facts, because ticket size and the nearest-AGENTS.md-owner condition cannot be computed there; T-0197 owns `steps.py lane`.
- note: `steps.py -h` now uses `RawDescriptionHelpFormatter` with an epilog, added so the warning literal appears in help; subcommand help was reported unchanged.
- note: `shellcheck` is not installed on the build host, so that part of `check.sh` was skipped in this run.
