# SDLC pillars

Status: v0.1, 2026-10-06. Decided by the maintainer. This file is the one statement of what improvements to SDLC are for. It does not set model or effort values.

Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction.

## The four pillars

| Pillar | Goal | Measure | In flight |
|---|---|---|---|
| Performance | The shortest safe path from ticket to verified-done | Wall minutes per closed ticket by lane; planner, reviewer and verifier time; tickets stuck over 2 hours | Solo-first lane, lane gate, plan review only for L4 and L5 steps, parallel lanes within machine limits |
| Cost | Spend reasoning, effort and compute in proportion to risk | Dollars per closed ticket; planning and plan-review share of spend; CI minutes and dollars; CPU and browser use | `solo_run` metering, budget gate, gate lock and reaper, CI cuts |
| Quality | Standards-conforming output, a smooth CI, simple and focused structures | Verifier first-pass rate; post-publish corrections; CI reds that were not code; concepts and tables that must agree | Independent verifier, the actionability rubric, per-level agents from one table, shellcheck in `check.sh` |
| Resilience | Work survives interruption and recovers on its own | Runs lost or restarted per week; time to resume; orphan processes | Sub-agent mode, `.limit` markers, process-group kill, supervisor |

Cost covers everything that costs: model dollars, CI minutes, CPU, memory, disk. Quality includes claims bound to evidence: independent verification and unverified items labelled.

## When pillars collide

1. Resilience first. It is never traded for speed or cost; surviving an account switch is a requirement.
2. Quality gates stay. Independent verification is not weakened to save a minute or a dollar.
3. Past that gate, speed beats polish.
4. Cost never overrides evidence. Cut effort that data shows buys nothing (plan review on small steps), not a check.

## Guardrail

The maintainer decides policy, model and effort values, and publishing. An improvement that changes any of those needs that approval first.

## Filter for any proposal

It moves a named measure in one pillar, passes the actionability gates (evidence, mechanism, right owner, reproducible, not already fixed), and does not worsen another pillar's measure without saying so. Otherwise it goes to the idea backlog.

## Evidence behind the current order

- agent-ui, 193 deduplicated runs, $787: planning and plan review were 55 percent of spend, verifiers 7.5 percent.
- maison, agent-ui and gen-ui-kit root-cause reports (2026-10-06): stalls came from dead parents, session limits and wrapper deaths; load came from gates and browsers, not lanes.
- Hook slowdown: a 4 KB heredoc command took 8.8 s per hook before the fix and under 0.2 s after (`docs/reports/hook-perf.md`).
