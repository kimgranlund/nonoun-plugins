# Domain: Goals

> `decompose` domain reference. Method depth in `method.md`. · 2026-06-26

## OUTSIDE-IN axis (structure)

`mission → outcomes → milestones → tasks`

- **mission** — the why; the durable intent.
- **outcomes** — the measurable changes that mean the mission advanced (not outputs).
- **milestones** — bounded deliverables that each produce an outcome.
- **tasks** — single assignable units within a milestone.

## INSIDE-OUT axis (behavior)

`intent → acceptance criteria → checks`

- **intent** — what a unit of work must achieve, in one sentence.
- **acceptance criteria** — the checkable predicates that prove the intent (given/when/then or measurable).
- **checks** — the executable form of each criterion (a test, a script exit, a metric threshold).

## Stop rule

Stop dividing when a **task is one assignable unit with at least one check**, and an **acceptance criterion is one checkable predicate**. A task with no check is unverifiable; a criterion testing two things is two criteria.

## Cross-check (defect quadrant)

- Every acceptance criterion must map to a task/milestone that delivers it → else `UNHOSTED` (a promised check no work produces).
- Every leaf task must satisfy a criterion **or** carry a `justify` (`enabling`, `spike`) → else `UNJUSTIFIED-LEAF` (busywork with no outcome).
- This is the same coherence the PRD→SPEC→LLD family enforces: outcomes ↔ goal IDs, criteria ↔ acceptance tests. Decomposing goals here feeds those IDs directly.

## Worked pass (milestone A1 — A2UI runtime foundation)

OUTSIDE-IN: `ship A2UI runtime` (outcome) → `A1` (milestone) → tasks `{validator, surface model, renderer tree, default catalog}`.
INSIDE-OUT criteria: `payload validates identically at runtime+admission`, `surface teardown leaves zero subscribers`, `streamed payload renders on root`, `default-catalog payload renders 0 CATALOG errors`.
Map: `bind data` criterion finds no task → `UNHOSTED` → add a `data-binding` task. Re-check → clean.

```json
{
  "domain": "goals",
  "nodes": [
    {"id":"validator","label":"validator task","leaf":true},
    {"id":"surface","label":"surface-model task","leaf":true},
    {"id":"tree","label":"renderer-tree task","leaf":true},
    {"id":"binding","label":"data-binding task","leaf":true},
    {"id":"catalog","label":"default-catalog task","leaf":true}
  ],
  "actions": [
    {"id":"parity","label":"validate identically runtime+admission"},
    {"id":"teardown","label":"teardown leaves zero subscribers"},
    {"id":"onroot","label":"render on root"},
    {"id":"bind","label":"resolve data bindings"},
    {"id":"nocaterr","label":"default-catalog 0 CATALOG errors"}
  ],
  "hosts": [
    {"action":"parity","node":"validator"},{"action":"teardown","node":"surface"},
    {"action":"onroot","node":"tree"},{"action":"bind","node":"binding"},
    {"action":"nocaterr","node":"catalog"}
  ]
}
```
