---
id: K-003
title: Share of builder runs that end blocked, per wave
status: proposed
owner: maintainer
created: 2026-10-09
unit: percent
direction: down
target: "<= 5"
baseline: {value: 10.9, date: 2026-10-09, source: docs/work/plan-reliability-docs/kpi-baseline-probe.py, verified: false}
measure: python3 plugins/sdlc/scripts/fleet_collect.py collect <repo> --since <date>
read: results.builder.blocked / results.builder.total * 100
cadence: per retro
goals: [G-002]
---
## Definition
A wave is one retro window. Of the builder runs recorded in `runs.jsonl` in the window (deduplicated by `attempt_id`), the share whose result file holds a `## Status` whose first word is `blocked`. A blocked builder stopped on something outside its step: a stale tree, a scope list that forbids a file the change must touch, a guard that cannot pass, a missing dependency. Each one costs a replan or a re-dispatch.

Excluded: builders that end `failed` or `inherited red`; those are other outcomes with their own causes.

## Reading it
- `fleet_collect.py` reads it: `results.builder.total` counts the builder rows of the window and `results.builder.blocked` those whose result file reads `blocked` under `## Status`.
- The baseline is unverified: 10.9 is 5 blocked of 46 builder rows on or after 2026-10-09 (ui-kit-maison 1 of 23, agent-ui 2 of 12, ultimate-tokens 2 of 11; sdlc-lite had no builder rows), from one run of `python3 docs/work/plan-reliability-docs/kpi-baseline-probe.py 2026-10-09 <four repo paths>` on 2026-10-09.
- It is a floor. A builder that blocks and then writes a new report over the same file is read as its last status: maison's `.sdlc/tickets/0346-gap-buildout-wave-plan/step-2/builder-L3.md` says in its Notes that an earlier blocked report (stale lane) was superseded, and it now reads `done`.
- Compare windows of the same length; a wave with few builder runs swings widely.

## History
- 2026-10-09: proposed with G-002 (planner-L3 of task plan-reliability-docs).
