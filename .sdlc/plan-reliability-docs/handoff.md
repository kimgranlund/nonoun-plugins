## Goal
Write the goal, KPIs, specs and a ticket plan for the next SDLC Lite patch (0.22.3 candidates) so each piece of work has an intent, a measure and a rubric before any lane is started. Documents only: write files under docs/ and one plan; do not change plugins/, scripts/ or any ticket status.

## Read first
- docs/specs/repo-onboarding/goals-and-kpi.md (the goals and kpi homes: front matter, sections, checks G-1 to G-5), docs/goals/001-fleet-load-without-gate-reds.md, docs/kpi/001-runs-without-cost-row.md (the seed files to copy the shape from).
- docs/specs/sdlc-lite/plan-verification.md (the outcome block: Outcome, Measured by, Rubric, Negative control) and plugins/sdlc-lite/skills/plan-verification/references/outcome-block.md.
- docs/reports/2026-10-09-fleet-retro-00.md, and the 12 hour retro answers: /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/fleet-retro-2026-10-09-12.md, /Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/fleet-retro-2026-10-09-12.md, /Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc/fleet-retro-2026-10-09-12.md (read only; do not edit those repos).
- plugins/sdlc-lite/scripts/run_lifecycle.py, dispatch.py (prepare, record, prune), steps.py (lint), fleet_collect.py (what the collector can measure).

## Work to cover (the seven candidates)
1. Auto-recover orphaned attempts after a host restart: `dispatch.py prepare` blocks re-dispatch until `run_lifecycle.py recover` runs (maison: about 2 hours; agent-ui: four crashed runs). First check what prepare already recovers.
2. `dispatch.py record` run before the role wrote its result file closes the attempt as failed with no retry.
3. Dispatch prompts name the stale primary checkout as Tree and Base sha (maison: three builders blocked). T-0381 fixed the base order, so find out what remains.
4. Unsatisfiable or circular criteria (a criterion that can only pass after the same verifier's pass report): a `steps.py lint` check.
5. Scope lists that miss test files a guard covers, and guards that cannot read 0 (agent-ui, ultimate-tokens): a `steps.py lint` check that evaluates guards and scope lists before build.
6. Prune safety: ultimate-tokens' recurring prune cron stopped agents that were only waiting on a background `npm test`. Check that `dispatch.py prune` only touches agents whose result is recorded, and say how conductors must use it.
7. Delta verifier: whole-ticket verifiers ran 43 to 56 minutes each (ultimate-tokens). Needs a measurement before any build.

## Deliverables
1. docs/goals/002-restart-and-blocked-run-cost.md: one goal (status proposed) in the shape of goal 001: "a host restart or a blocked run costs minutes, not hours", with its KPIs listed.
2. docs/kpi/002-restart-recovery-minutes.md, docs/kpi/003-blocked-builders-per-wave.md, docs/kpi/004-unsatisfiable-criteria-caught.md (status proposed, each with a runnable `measure:` command or, where the collector cannot measure it yet, an honest `measure:` that names the missing field and a ticket to add it; a baseline with its source or `baseline: unknown` plus how to get it). Use only numbers a file or command shows; label the rest unverified.
3. docs/specs/sdlc-lite/restart-and-blocked-run-plan.md: for each of the seven candidates, one section: Outcome and why, current behavior with file:line (read the code, do not guess), the change, the KPI it moves, the rubric (3 to 5 criteria), one negative control, size L1 to L3, files touched, dependencies and order. Say plainly where a candidate may already be fixed or needs a diagnosis first.
4. .sdlc/plan-reliability-docs/plan.md: ordered steps, one per ticket to file, each with a builder level and runnable acceptance criteria, in the handoff-format step shape, lint it with `python3 plugins/sdlc-lite/scripts/steps.py lint`.
Cross-link the goal, KPIs and spec. `python3 plugins/sdlc-lite/scripts/docs_check.py` must report 0 errors (G-1 to G-5 included). No em or en dashes. Do not file tickets or edit existing documents except adding the new files to the entry files docs_check requires.
