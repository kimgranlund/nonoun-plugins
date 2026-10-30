---
id: K-001
title: Share of runs with no cost row
status: active
owner: maintainer
created: 2026-10-08
unit: percent
direction: down
target: "<= 5"
baseline: {value: 29.2, date: 2026-10-08, source: docs/reports/2026-10-08-fleet-retro-06.md, verified: false}
measure: python3 plugins/sdlc/scripts/fleet_collect.py collect <repo> --since <date>
read: runs.unmetered / runs.total * 100
cadence: per retro
goals: [G-001]
---
## Definition
The share of deduplicated runs in the window whose `cost_usd` is null, from the collector's `runs` object. A repository with no `.sdlc` reports `runs: "none"` and is skipped, not counted as zero.

## Reading it
- The collector windows by `--since`; compare the same window length across retros.
- The baseline is unverified: 29.2 is the sum of the report's per-repo unmetered counts (43, 6, 33, 3 and 5) over its run counts (150, 6, 33, 75 and 44), 90 of 308, worked out by hand and not re-run. The collector windows have since moved.
- One run of the measure on this repository, 2026-10-08, `--since 2026-10-07`: 12 unmetered of 144 runs, 8.3 percent. That is one repository, not the fleet.
- Both numbers are floors for spend: an unmetered run has no cost row at all.

## History
- 2026-10-08: first seed KPI of the kpi home (T-0392).
