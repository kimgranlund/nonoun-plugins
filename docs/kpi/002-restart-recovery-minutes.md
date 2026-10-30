---
id: K-002
title: Minutes of work lost per interrupted run
status: proposed
owner: maintainer
created: 2026-10-09
unit: minutes
direction: down
target: "<= 15"
baseline: {value: 34.3, date: 2026-10-09, source: docs/work/plan-reliability-docs/kpi-baseline-probe.py, verified: false}
measure: python3 plugins/sdlc/scripts/fleet_collect.py collect <repo> --since <date>
read: runs.interrupted.lost_min_median
cadence: per retro
goals: [G-002]
---
## Definition
For each attempt record with status `interrupted` in the window, the minutes from its `started_at` to the `started_at` of the next attempt of the same role in the same handoff dir (to its own `finished_at` when no next attempt exists). The KPI is the median over the window. It counts the work a restart threw away plus the time until the run was dispatched again, which is what "a restart costs minutes, not hours" means for one run.

Excluded: an interrupted record whose result file (`<stem>.md` beside `<stem>.attempt.json`) already holds a verdict, because the run finished and reported (T-0445); and attempts still `running` whose parent session is dead (orphans nobody recovered). They have no next attempt and no recovery stamp, so they are counted apart as `runs.orphaned.count`.

## Reading it
- `fleet_collect.py` reads it: each interrupted attempt carries `lost_min`, and `runs.interrupted` carries `lost_min_median` and `lost_min_total` (null and 0 with no interrupted attempt); `runs.orphaned` holds the count and list of orphans.
- The baseline is unverified: 34.3 is the median of 8 interrupted attempts started on or after 2026-10-09 (ui-kit-maison 5: 5.3, 5.3, 27.6, 41.0, 68.9; sdlc-lite 3: 10.7, 56.9, 71.4), from one run of `python3 docs/work/plan-reliability-docs/kpi-baseline-probe.py 2026-10-09 <four repo paths>` on 2026-10-09 by the planner. agent-ui and ultimate-tokens had none in that window. The same run found 13 orphaned attempts never recovered (maison 3, ultimate-tokens 1, sdlc-lite 9) that the median leaves out. That count tests each parent pid with `kill(pid, 0)` alone, so a pid the host reused reads as alive and the count can be low; plan step 4 adds the start-time test to `dispatch.py`.
- The number holds the lost work before the crash as well as the gap after it. Faster detection shrinks only the gap; a long verifier that dies near its end still costs its full length until roles can resume partial work. If the KPI stays above target after the plan lands, that is the next design, not a reason to change the target.
- A small window has few interrupted runs, so one long run moves the median. Read it beside the count.

## History
- 2026-10-09: proposed with G-002 (planner-L3 of task plan-reliability-docs).
