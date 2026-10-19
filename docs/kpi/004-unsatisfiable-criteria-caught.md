---
id: K-004
title: Share of unsatisfiable criteria caught before a builder runs
status: proposed
owner: maintainer
created: 2026-10-09
unit: percent
direction: up
target: ">= 50"
baseline: unknown
measure: python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --since <date>
read: plan_defects.early / (plan_defects.early + plan_defects.late) * 100 (early stays 0 until plan step 5 records refusals)
cadence: per retro
goals: [G-002]
---
## Definition
A criterion defect is an acceptance criterion or guard that cannot pass together with its step: one that does not parse or cannot fail, one that passes only after the same step's verifier passes (circular), a guard the intended change must turn red, or a scope list that forbids a file the change must edit. Early means a check refused it before any builder ran (`steps.py lint` or `steps.py split`). Late means a builder or verifier result reported it on a line starting `plan defect:`. The KPI is the early share.

## Reading it
- `fleet_collect.py` reads it. Late: `plan_defects.late` counts builder and verifier rows whose result holds a `plan defect:` line. Early: `plan_defects.early` counts the lines of `refusals.jsonl` files in the window, but `steps.py` keeps no refusal record yet; plan step 5 makes `steps.py lint` and `split` append each refusal to `refusals.jsonl` in the task dir. Until step 5 lands, early reads 0 and the KPI reads 0.
- Baseline unknown because the early side is unrecorded. The late side alone, unverified: 11 of 149 builder and verifier rows on or after 2026-10-09 held a `plan defect:` line (ui-kit-maison 6, agent-ui 2, ultimate-tokens 3, sdlc-lite 0), from one run of `python3 docs/work/plan-reliability-docs/kpi-baseline-probe.py 2026-10-09 <four repo paths>`. To get the baseline, land steps 1 and 5 and read one retro window.
- `specgate.py` refusals and plan review findings that reject a criterion are early too. They are left out: specgate keeps no refusal record either, and review findings are prose. Both are undercounts of early, so the KPI is a floor.
- Not every defect can be caught before build. A guard that reads green at base and red only after the change (ultimate-tokens `report-compute-neutral`) is found late by design; see candidate 5 of [the plan](../specs/sdlc-lite/restart-and-blocked-run-plan.md).

## History
- 2026-10-09: proposed with G-002 (planner-L3 of task plan-reliability-docs).
