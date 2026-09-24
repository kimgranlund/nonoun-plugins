# Domain: <NAME>

> Source: `decompose` domain-reference template. Method depth in `method.md`. Set a real `· YYYY-MM-DD` freshness marker when you copy.
>
> Copy this file to `references/<name>.md`, fill the axes + stop rule, add a worked manifest, and add a row to the SKILL.md domain table.
>
> **Canon check first:** if another installed skill owns this domain's method, declare it canon in
> this header and write ONLY the manifest adapter below — never restate its ladders, formulas, or
> rubric. With no owner installed, this file IS the canon: carry the axes, stop rule, and worked
> pass in full.

## OUTSIDE-IN axis (structure)

`<whole> → <…> → <…> → <atom>`

State the 3–4 levels from the whole down to the smallest part. One line each defining the level. (Canon owned elsewhere → replace this section with **Mapping to the manifest**: which canon levels become `nodes`/`actions`/`hosts`, and this domain's `justify` vocabulary.)

## INSIDE-OUT axis (behavior)

`<atom/need> → <…> → <surface> → <coherence>`

State the 3–4 levels from the irreducible unit up to a coherent whole. One line each.

## Stop rule

State when a structural part is atomic (one responsibility / one owner / one contract) and when an action is atomic (one intent / one check), in this domain's terms. Note any mode this domain defaults to (e.g. `goals` naturally runs PLAN — `"plan": true`).

## Cross-check (defect quadrant)

- Every action must host on a node → else `UNHOSTED`.
- Every leaf node must host an action **or** carry a `justify` → else `UNJUSTIFIED-LEAF`. Name the legitimate `justify` values for this domain.
- Note any domain-specific invariant (e.g. dependency direction, feedback requirement) and any altitude boundary where this domain stops (as `ux-architecture` stops at screen/state existence, handing cross-screen journeys off).

## Worked pass (<short example>)

OUTSIDE-IN: … INSIDE-OUT: … Map: surface one `UNHOSTED`, fix it, re-check → clean. End with a `coverage_check.py`-shaped manifest that EXITS 0 — run it, don't assume it:

```json
{ "domain": "<name>", "nodes": [], "actions": [], "hosts": [] }
```

---

A domain file is **done** when: both axes (or the canon pointer + manifest mapping), the stop rule, the `justify` vocabulary, and a worked manifest that passes `coverage_check.py` are present, and the SKILL.md domain table has its row. **NOT done** when it restates a ladder/formula a canon skill owns, or ships a worked manifest that was never run.
