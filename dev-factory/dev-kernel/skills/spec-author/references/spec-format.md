# The SKILL-format spec

A dev-factory spec is **a mini-skill**. It wears the same shape as a `SKILL.md` — a routable frontmatter
surface, a brief body that reads top-to-bottom, an embedded machine-readable contract, and optional
`references/` depth and bundled `agents/`. That shape is what makes a spec navigable, lazy-loaded, and
reviewable instead of a flat wall of prose — and it is what the spec-quality gate reads.

## The two shapes (both valid)

A spec cell's `asset_ref` points to either:

```
spec/color-mode.md                      # MINIMAL — a single SKILL-format file (the default)

spec/color-mode/                        # RICH — a folder, for a spec that earns depth
├── SKILL.md                            #   the brief + the contract (what the gate reads)
├── references/
│   ├── acceptance.md                   #   the deep checkable predicates
│   ├── invariants.md                   #   pre/postconditions, invariants, edge cases
│   └── decomposition.md                #   the lattice slice + ticket batch, in full
└── agents/                             #   (optional) a spec-specific reviewer
```

The gate reads the file directly, or `<dir>/SKILL.md` if `asset_ref` is a folder. Everything below is the
same for both; the folder form just moves the depth out of the brief into `references/`.

## The `SKILL.md` — frontmatter + brief + contract

```markdown
---
name: color-mode                                    # == the cell slug
description: >                                       # the INTENT + scope — the routable surface
  System-wide light/dark color mode a user can toggle and that persists across reloads, applied
  before first paint so there is no flash. Scope: the global theme; NOT per-component overrides.
---

# color-mode — a persisted, flash-free light/dark theme

**Intent.** <the principal's actual want, captured in prose — what changes for the user, and why.>

**Acceptance criteria.** <a readable summary; the machine-checkable form is the contract block below,
the depth is `references/acceptance.md`.>

**Non-goals.** <what this spec explicitly does NOT cover — the boundary the scope critic checks.>

**Decomposition.** <the cells this spec implies + the ticket batch that builds it — summary; full in
`references/decomposition.md`.>

​```json
{
  "title": "System color mode",
  "cell": "spec.system.color-mode",
  "binds_rubric": "rubric.system.spec-quality",
  "acceptance_criteria": [
    { "id": "cm-01", "check": "documentElement carries data-theme matching the chosen mode" },
    { "id": "cm-02", "check": "the choice survives a reload (persisted in localStorage)" },
    { "id": "cm-03", "rubric_cell": "rubric.system.color-contrast" }
  ],
  "non_goals": [ "per-component theme overrides", "server-rendered theme negotiation" ],
  "decomposition": {
    "parent": { "criteria": [ "cm-01", "cm-02", "cm-03" ] },
    "cells": [ { "id": "capability.system.theme-store" }, { "id": "methodology.task.apply-theme" } ],
    "tickets": [
      { "target_cell": "capability.system.theme-store", "acceptance": { "rubric_cell": "rubric.system.theme-store" }, "covers": [ "cm-02", "cm-03" ] },
      { "target_cell": "methodology.task.apply-theme", "acceptance": { "rubric_cell": "rubric.task.apply-theme" }, "covers": [ "cm-01" ] }
    ]
  }
}
​```

> `decomposition` is **optional** — omit it until the spec is actually decomposed (the entailment gate is
> "not applicable" when absent). When present it is the exact shape `_entailment_check.py` consumes: `cells`
> are objects with an `id`, `tickets` is a **list** each declaring a `target_cell` + an `acceptance.rubric_cell`
> + the `covers` criteria it satisfies, and every parent criterion must be covered (the example above entails
> 3/3). Cells-as-bare-strings or a ticket *count* will fail the gate.

## References
- `references/acceptance.md` — every criterion as an executable check or a rubric binding
- `references/decomposition.md` — the entailment-checked carving into cells + tickets
```

## The contract block — what the gate actually reads

The fenced ` ```json ` block is the **machine-readable contract**, and it is the single source of truth the
spec-quality gate consumes (the verifier reads the first json block in the file — so the contract is
embedded in the skill, not a parallel artifact). It carries exactly the fields the gate checks:

| Field | Required | Gate dimension |
|---|---|---|
| `cell` | yes | `schema-valid` — `{layer}.{scope}.{slug}`, layer == `spec`, excludes maturity |
| `acceptance_criteria` | yes, ≥1 | `criteria-checkable` — every item has an `id` AND **either** `check` (an executable predicate) **or** `rubric_cell` (a validated rubric binding). **Zero prose-only criteria.** |
| `binds_rubric` | yes | `rubric-binds` — names a `rubric.*` cell. **The spec gate checks only the *binding*** (that it points at a `rubric.*` cell). That the bound rubric is itself **`validated`** is enforced *not by this gate* (it runs standalone, with no lattice) but by the **lattice partial order** — `lattice.py` validity refuses a cell that advances against a non-validated verifier rubric (`lattice.py:157`), and `gate-ticket-ready` denies an unvalidated-rubric ticket (`lifecycle.py:108`). Binding here, maturity there. |
| `non_goals` | yes, ≥1 | `non-goals-present` — the boundary is declared, not implied |
| `decomposition` | when the spec is decomposed | `decomposition-entailment` — `_entailment_check.py` proves the carving **covers** every parent criterion under the partial order (each parent criterion bound to ≥1 child that itself binds a rubric); a deeper "does the child *entail* (not merely cover) the parent" judgment is the `critic-spec-entailment` lens, not the script |

The contract `cell`'s **slug** must equal the frontmatter `name`, and its **layer must be `spec`** — the skill
surface and the machine contract cannot disagree (the `skill-shape` + `schema-valid` checks). (`scope` lives
only in the contract `cell`; the gate does not cross-check it against the frontmatter.)

## The skill-shape rule

A spec authored in this format MUST carry:
1. **frontmatter** with `name` (== the slug) and a `description` that states the intent + scope (not "a spec for X" — the actual want and boundary);
2. a **brief body** — at minimum the Intent / Non-goals it elaborates beyond the contract;
3. the **contract block** above.

A legacy spec that is *only* a json contract (no frontmatter, no brief) still passes the hard gates — it is a
valid-but-minimal spec — but it does not clear the **spec-authoring** guidance rubric's `skill-shape`
dimension, so AUTHOR and UPDATE always produce the full form. The skill wrapper is the advance; the contract
is the floor.

## Why a spec is a skill (not just a doc)

- **Routable surface.** The `description` is the spec's intent in one breath — the same trigger-surface
  discipline a skill's description carries. You can scan a `spec/` dir and know what each cell *wants*.
- **Lazy depth.** The brief reads in 30 seconds; `references/` holds the predicates, invariants, and
  decomposition only when you need them — the spec doesn't force its full weight into every reader's context.
- **Reviewable in place.** A bundled `agents/` reviewer, or the skill's `spec-council`, reviews the artifact
  in its own shape — the spec carries the means of its own scrutiny.
- **Composable.** Specs reference specs the way skills reference skills; the decomposition section is a typed
  edge to the cells it implies, not a prose aside.
