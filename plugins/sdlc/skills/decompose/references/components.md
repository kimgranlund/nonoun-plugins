# Domain: Components — manifest adapter

> `decompose` domain reference — **canon for this domain in this pack**: the tier ladder
> (module → component → primitive), the COMPOSE × REALIZE axes, the justify values, and the
> manifest mapping below. The geometry law and per-domain grading of the retired sibling pack are
> not carried here — grade against the generic `rubric.md`. Method depth in `method.md`
> (`scripts/coverage_check.py` runs the gate). · 2026-07-06

## Mapping to the manifest

- **nodes** (OUTSIDE-IN = the COMPOSE axis) — module, component, primitive and,
  within a component, its parts/slots/seams become nodes; irreducible parts are `leaf: true`.
- **actions** (INSIDE-OUT = the REALIZE axis) — the interactions and semantic
  obligations the piece must serve (open, navigate options, commit, light-dismiss…).
- **hosts** — each interaction → the part/element/slot that binds it.
- **justify** values for an action-free leaf: `structural`, `decorative-token`, `affordance`.

## Cross-check (defect quadrant)

- Every interaction must land on a part (an element/slot) → else `UNHOSTED` (a behavior with no
  element to bind).
- Every leaf part must carry an interaction **or** a `justify` → else `UNJUSTIFIED-LEAF` — the
  "clean API hiding an inert build" failure: a part that exists in the anatomy but does nothing.

## Worked manifest (`ui-select`, abbreviated)

Map: `caret` hosts no action → tag `justify:"affordance"` (it signals openability). `light-dismiss`
hosts on the `listbox` overlay. Re-check → clean.

```json
{
  "domain": "components",
  "nodes": [
    {"id":"trigger","label":"trigger-button"},
    {"id":"listbox","label":"listbox"},
    {"id":"caret","label":"caret","leaf":true,"justify":"affordance"}
  ],
  "actions": [
    {"id":"open","label":"open"},{"id":"nav","label":"navigate options"},
    {"id":"commit","label":"commit selection"},{"id":"dismiss","label":"light-dismiss"}
  ],
  "hosts": [
    {"action":"open","node":"trigger"},{"action":"nav","node":"listbox"},
    {"action":"commit","node":"listbox"},{"action":"dismiss","node":"listbox"}
  ]
}
```
