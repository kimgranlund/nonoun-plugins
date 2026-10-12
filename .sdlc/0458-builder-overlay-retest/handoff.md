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
budget_usd: 30
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

## Plan review
plan review: replan: dispatch.py prepare builder L3 refused step-1 (steps.py lint links gate): cited paths do not exist in this repo: .sdlc/native-dom-charts/step-2/handoff.md, .sdlc/0368-prune-flag/handoff.md, .sdlc/0373-codex-role-preflight/handoff.md, .sdlc/0378-red-checkpoint-builder/handoff.md, .sdlc/geometry-compound-insets/step-4.superseded-1/handoff.md, .sdlc/geometry-compound-insets/step-4/handoff.md. plan defect: cite paths in other repos or at a base sha in a form the links gate does not resolve against this tree (absolute path with repo root, or `<sha>:<path>` git object form), or as plain words rather than a backticked repo-relative path. Keep the rest of planner-L2.md unchanged.
plan review: replan: builder L3 blocked at step 1 (.sdlc/0458-builder-overlay-retest/step-1.superseded-2/builder-L3.md): plan defect: criterion 3 (four L1 rep-1 tasks both arms plus a balanced L5 pair) cannot hold with the $20 cap. Ticket spend so far: planners $3.85 + builder L3 $2.14 + replay cells $10.04 (rts-step10 L1 A/B done+pass, ndc-step2 L5 A blocked same defect, $8.54) = about $16.03. Remaining about $3.97 must cover this replan, one builder, its verifier and the filer. Conductor direction (unattended, ticket Constraint "stop at the cap and report what was run"): run no further cells; the builder writes the report from the evidence already in docs/reports/2026-10-12-builder-overlay-retest/ and run-log.md, marks L5 and the missing L1 pairs unverified under Not run, and states the stop at the cap; criteria must match what exists (3 rows: rts-step10 L1 A/B rep 1, ndc-step2 L5 A rep 1). Builder findings to carry: rts-step10 handoff on disk is the fixed version (hash 8974d49f, not the blocked fceea3cc), so it cannot test blocking; t0378 check is red at base b599114e, green at a8b39893 and e1fa6e04.
