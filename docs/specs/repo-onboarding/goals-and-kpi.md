# Goals and KPIs: two homes under docs/

Built in 0.22.1, ticket T-0392, from a request of 2026-10-08. It extends the [docs schema](../../planning/docs-schema/design.md) with two homes and does not change the other nine. The first live examples are [G-001](../../goals/001-fleet-load-without-gate-reds.md) and [K-001](../../kpi/001-runs-without-cost-row.md).

## Why

Three things are scattered today:

- What a repository is steering toward lives in chat, in a ticket's `## Goal` line, or in a `/goal` block that is gone after the session. A ticket goal is one change; nothing records the outcome several tickets serve.
- How we know the steering worked lives in retro tickets as a line `outcome metric: <rule or command>, before: <value>`. The number is real, but no document defines the metric, its target or its owner, so each retro reinvents it.
- `specs/` says what the system is, `planning/` holds proposals, `decisions/` holds one choice with its reasons. None of them is the right home for "we want X" or "X is measured this way".

## The two homes

| Home | Holds | Never holds |
|---|---|---|
| `goals/` | One intended outcome per file: what, why, scope, owner, status, the KPIs that tell us it is met | A change plan (`planning/`), a ticket, a result value, a decision with reasons |
| `kpi/` | One measure per file: definition, how to run it, unit, direction, target, baseline, owner, the goals it serves | The current value over time (`reports/`), a goal, a threshold nobody can run |

A goal answers "what outcome, and when do we call it met". A KPI answers "what number, from which command, and what is good". A goal without a KPI is a wish. A KPI without a goal is a dashboard nobody acts on.

The name is `kpi/` as written in the request, an acronym kept singular. The docs schema names every other home in the plural; `kpi` is the one exception and is stated in the layout.

## File names

`goals/NNN-<slug>.md` and `kpi/NNN-<slug>.md`: three digits, then a kebab-case slug, numbered per folder, never reused. A file is never renumbered. A superseded or dropped file moves to `archive/` with `superseded-by:` and keeps its number.

Markdown only. The request offered `.json`; docs_check rule D-9 forbids non-Markdown files outside `assets/`, and one format keeps one reader. The front matter is the machine-readable part and is parsed by `docs_check.py`. A script that wants a JSON feed generates it into `.sdlc/` from the front matter.

## Goal file

```
---
id: G-001
title: Fleet runs at 60 to 80 percent of the stop line without gate reds
status: active            # proposed | active | achieved | dropped
owner: maintainer
created: 2026-10-08
horizon: 2026-Q4          # optional: a date or a quarter
kpis: [K-003, K-004]      # ids in kpi/; or `none: <reason>` for a goal not yet measurable
---
## Outcome
One or two sentences: the state of the world that means the goal is met.

## Why
What it protects or buys. Link a report or decision by path, a ticket by id (`T-0368`) as text.

## Scope
In and out. Non-goals.

## Done when
Checkable lines, each naming the KPI and the threshold that closes it.

## History
Dated one-line changes: status moves, retargeting, who decided.
```

## KPI file

```
---
id: K-003
title: Share of runs with no cost row
status: active            # proposed | active | retired
owner: sdlc-lite-author
created: 2026-10-08
unit: percent
direction: down           # up | down | hold
target: "<= 5"            # a number or a bounded expression the measure can be compared with
baseline: {value: 78, date: 2026-10-08, source: docs/reports/2026-10-08-fleet-retro-06.md}
measure: python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d
read: runs.unmetered / runs.total * 100     # how to turn the output into the number
cadence: weekly           # per retro, weekly, per release
goals: [G-001]
---
## Definition
What is counted, what is excluded, and why this is the right proxy.

## Reading it
Pitfalls: windows, unmetered runs, floors versus true values.

## History
Dated one-line changes to the definition or target.
```

The current value is not stored here. A KPI file is edited in place like a spec; the values over time are `reports/` (a retro, a release record) that cite the KPI id. A KPI whose `measure:` cannot be run by a reader is a claim, not a KPI.

## How they connect to the rest

- A ticket serving a goal cites it in its `## Context` as text (`G-001`), never by path. docs cite tickets by id too (rule B-3).
- A retro ticket's `outcome metric:` line cites a KPI id when one exists (`outcome metric: K-003, before: 78`); the next retro reads that KPI's `measure:` for the outcome check.
- `/plan-goal` blocks and `/plan-loop` lines may cite a goal id as their done-when source.
- A release record lists the KPI values it moved, from the reports, not from the KPI file.
- The fleet retro rubric criterion C5 (outcome metric) is met by a KPI with a runnable `measure:`.

## Checks (docs_check.py, each with a negative control)

| Rule | Fails when |
|---|---|
| G-1 | A file in `goals/` or `kpi/` is not `NNN-slug.md`, or its `id` does not match its number (`G-007` in `007-...`), or a number repeats in the folder |
| G-2 | Required front matter is missing: goals need `id`, `title`, `status`, `owner`, `created`, `kpis`; KPIs need `id`, `title`, `status`, `owner`, `created`, `unit`, `direction`, `target`, `measure`, `goals` |
| G-3 | A `kpis:` id has no file in `kpi/`, or a `goals:` id has no file in `goals/`, or a goal lists a KPI that does not list it back |
| G-4 | A goal with `status: active` has `kpis:` empty or missing, without `none: <reason>` |
| G-5 | A `status:` value is outside its set, or a `dropped`, `achieved` or `retired` file still sits outside `archive/` after 30 days (advice, warning not error; the age counts from an optional `date:` or the file's modification time, as D-8 does) |

The homes are added to `DEFAULT_HOMES` in `docs_check.py`, to `DOC_KINDS` in `onboard.py`, to the kinds table in `layout.md`, and to the managed Documents block that `onboard.py setup` writes under `docs/AGENTS.md`. As with every home, a repository creates a folder only when it has something to put in it; setup never creates an empty `goals/` or `kpi/`.

## Open choices, defaulted

- **Id letters.** `G-` and `K-` keep goal and KPI ids from colliding with tickets (`T-`) and decisions. (user may change)
- **Numbering width.** Three digits as requested; a repository past 999 goals has bigger problems.
- **No stored values.** A KPI file never holds a current value. If a repository wants a dashboard, it generates one from the `measure:` lines into `reports/`.

## Not covered

How a conductor picks work from goals, and any automatic goal-to-ticket generation. Both need a goal ledger in `.sdlc/` and are a separate design if they are wanted.
