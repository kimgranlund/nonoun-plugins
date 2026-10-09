---
id: G-001
title: Fleet runs are metered and stay inside the load stop line without gate reds
status: active
owner: maintainer
created: 2026-10-08
horizon: 2026-Q4
kpis: [K-001]
---
## Outcome
Every run in the fleet leaves a cost row, and the fleet holds 60 to 80 percent of the machine stop line without a gate going red from contention.

## Why
The [fleet retro of 2026-10-08](../reports/2026-10-08-fleet-retro-06.md) counted 90 runs of 308 with no cost row, so spend and load cannot be sized from the records. A red gate under load is noise that hides a real regression.

## Scope
In: cost rows on solo and chain runs in every adopting repository. Out: changing model or effort rows, and the load limit itself. Gate reds from contention need their own KPI, which does not exist yet; until it does, this goal is measured by K-001 alone.

## Done when
- [K-001](../kpi/001-runs-without-cost-row.md) reads 5 or below in the retro that follows 0.22.1.

## History
- 2026-10-08: proposed and activated as the first seed goal of the goals home (T-0392).
