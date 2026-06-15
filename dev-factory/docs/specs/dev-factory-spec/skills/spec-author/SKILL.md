---
name: spec-author
description: >
  Author, migrate, and improve specification cells, then decompose them into the typed
  constituent parts the factory operates on — cells, dependency edges, and a triaged
  ticket batch. Use at the factory's intake boundary: when a human intent, a PRD, a
  legacy document, or a pile of notes must become typed substrate; when an existing spec
  must be improved or re-validated; or when a validated spec must be broken down into the
  lattice slice and ticket set that drive its construction. Produces a spec cell graded
  against the spec-quality rubric, plus a lattice-seed delta and a ticket batch whose
  decomposition is entailment-checked. This is the root of the dependency partial order:
  fuzzy intent here multiplies downstream, so the capability is rubric-gated, not vibes.
---

# spec-author — The Intake Boundary

The factory advances cells; this skill creates them from intent. It is the front door:
the conversion of a principal's want — greenfield or brownfield — into a typed
specification cell and, from there, into the cells and tickets the operating loop runs on.
Because the spec layer is upstream of every other layer (`references/spec-layer.md`), a
weak intake is the highest-leverage failure point in the system; this capability is
therefore graded against a validated rubric like any other.

## Three Modes

| Mode | Trigger | Agent | Loop strategy |
|---|---|---|---|
| **author** (greenfield) | a new intent with no prior document | `spec-architect` | capture intent → draft → auto-research hill-climb against the spec-quality rubric |
| **migrate** (brownfield) | a legacy spec/PRD/doc/notes to bring into the typed form | `spec-architect` (migration methodology) | extract → re-type → fill boundary gaps → grade |
| **improve** (regeneration) | a validated spec corrected by operating evidence | `spec-architect` | the cell re-enters `regenerating`; ledgered, never silent |

All three terminate in the same place: a spec cell that **clears the spec-quality rubric**
(`rubric/spec-quality.rubric.json`) — which must itself be `validated` before any spec
binds to it. The verifier of specs is verified (meta-verification).

## The Decomposition Output Contract

Once a spec cell is validated, `spec-decomposer` turns it into the constituent parts the
factory operates on. The output is a **typed delta**, never prose:

1. **Lattice-seed delta** — child cells the spec implies, placed down the scope ladder
   (`fleet → system → workflow → task → call`) and across layers, each at honest maturity
   (`absent`/`defined`). Dependency edges respect the layer partial order.
2. **Ticket batch** — one `tkt-` per cell to advance, each with `target_cell`,
   `target_transition`, `acceptance` bound to a rubric cell, a budget, and declared
   dependencies. Tickets are emitted at `draft` for the triager to promote to `active`.
3. **Entailment proof** — the `_entailment_check.py` script confirms: every parent
   acceptance criterion is covered by ≥1 child cell; every child's acceptance binds to a
   rubric cell; no orphan criteria; edges respect the partial order. **Satisfying the child
   specs must entail satisfying the parent** (decomposition soundness). The check is
   deterministic — computation routes to code.

A spec that cannot be decomposed with a passing entailment proof is not validated; it is
returned to `regenerating`. This is `policy/spec-readiness.policy.json`.

## What This Skill Carries

This folder is self-contained substrate (the compound-skill pattern):

```
spec-author/
├── SKILL.md                         (this file)
├── agents/{spec-architect, spec-decomposer}.md
├── rubric/spec-quality.rubric.json  (the validated verifier; gate + review dims)
├── methodologies/spec-intake.md     (capture → author/migrate/improve → decompose)
├── policy/spec-readiness.policy.json (the doneness gate, incl. entailment)
├── scripts/_entailment_check.py     (deterministic decomposition check)
└── references/spec-layer.md         (the spec-layer summary it composes from)
```

## Routing Discipline

Authoring, migration, improvement, and the *judgment* of how to decompose are
multi-step judgment → agents. The entailment check, coverage computation, and partial-order
validation are deterministic → the script. Grading is the rubric, run by a critic that is
not the authoring agent. Selection of which mode applies is read from the ticket type, not
inferred at dispatch.

## Self-Application

This skill ingests exactly the kind of document the factory's own spec is. Pointed at
`TDD-01-nonoun-factory.md`, it produces the factory's own lattice slice and ticket
backlog — the system bootstrapping itself from its own specification.
