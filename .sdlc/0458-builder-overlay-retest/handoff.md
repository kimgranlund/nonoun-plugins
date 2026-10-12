---
id: T-0458
title: "Retest the builder overlays on tasks where builders actually block, plus one L5 pair"
type: spike           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0450]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
budget_usd: 20
---

## Question
Do the builder L1 and L5 overlays change blocked rate, first-pass rate or cost on tasks where builders actually block, which the first A/B (zero blocks in both arms) could not show?

## Goal
A dated report with a keep, extend or drop verdict for the builder overlays from a replay on tasks that make builders block, and at least one priced L5 pair.

## Intent
- Do: pick 4 to 6 replay tasks from real blocked builder notes and first-round verifier non-passes (the T-0450 report names them; use its sample and cause classes), each with a base sha and a handoff that exist on this machine (the first A/B could not run `button-geometry-model` and `svelte-icon-component` because their repos and shas are missing; choose only reproducible ones); run the same A and B arms as T-0442 (`docs/reports/2026-10-11-builder-overlay-ab.md` Method) at builder L1 for blocking-prone tasks and one L5 pair on the costliest task, two repetitions where the budget allows, every run priced through `dispatch.py record` (T-0446 now finds the transcript without a flag). Keep the hidden-check grade per run. Apply the drop rules of the first A/B again, and add a measured-block rule: the overlay must not raise the blocked rate and should lower it on the blocking-prone tasks.
- Also record the first A/B's miss: `figma-stale-skip-report` failed its hidden check `staleskipnotice` in all four runs while both verifier levels passed it each time (a verifier miss, same in both arms): note it for the verifier prompt work, do not fix it here.
- Non-goals: editing overlays during the run; extending overlays to other roles (T-0443); a model or effort change.
- Done when: `docs/reports/<date>-builder-overlay-retest.md` exists with per-run rows (cost, minutes, blocked, hidden check, verifier verdict), the per-arm table, the rule outcomes, a verdict line (`Verdict: keep | extend | drop`) and what was not run; spend stated and under the cap.
- outcome metric: builder blocked rate on the replay tasks, arm A versus arm B, before: 0 of 5 versus 0 of 5 on the first A/B tasks

## Context
First A/B: `docs/reports/2026-10-11-builder-overlay-ab.md` (L1 verdict drop on a rule that could not bite; L5 unverified; spend $7.94). Overlays: `plugins/sdlc-lite/overlays/builder.md`. Maintainer decision 2026-10-11: keep the overlays and retest harder. T-0443 (more overlays) stays gated on this ticket's verdict.

## Constraints
No model or effort change. Budget cap $20; stop at it and report what was run. The tmp arm clones are removed by `dispatch.py record`, so keep the grade and minutes columns in the run log as you go (the first A/B's claims could not be re-observed).
