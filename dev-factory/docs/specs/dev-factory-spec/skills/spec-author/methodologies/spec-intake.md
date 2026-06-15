# Spec Intake — From Intent to Constituent Parts

`Cell: methodology.fleet.spec-intake · Status: defined · Register: established lineage (DbC, GORE/KAOS/i*, HTN refinement, spec-authoring practice); the decomposition-to-cells+tickets morphism is house synthesis`

## The Pipeline

Intake is the factory's front door and the root of the dependency partial order. The
pipeline is the same regardless of mode; only the first step differs.

```
  CAPTURE ──▶ AUTHOR/MIGRATE/IMPROVE ──▶ GRADE ──▶ DECOMPOSE ──▶ SEED + EMIT
  intent      typed spec draft            spec-      spec → cells   lattice delta
  schema                                  quality    + tickets      + ticket batch
                                          rubric     (entailment)   (draft)
            ◀─────────────── hill-climb on grade failure ──────────┘
```

Capture intent first; it is the critical step — most downstream failures trace to fuzzy
intent here, and the loss is multiplicative across every hop beneath it.

## Step 1 — Capture (mode-specific)

- **Author (greenfield).** Elicit the principal's want into a typed intent schema: target
  state, the job-to-be-done, hard constraints (which become invariants), and explicit
  non-goals. Resolve ambiguity *before* drafting — a clarification is cheaper than a
  decomposition built on a guess.
- **Migrate (brownfield).** Extract from the legacy document: stated goals, implicit
  acceptance criteria, scattered constraints. Re-type into the intent schema. Mark every
  gap the legacy doc leaves (boundaries it never specified) as an open item to fill, not to
  paper over. The output of migration is the same typed intent schema as authoring.
- **Improve (regeneration).** A validated spec corrected by operating evidence re-enters
  `regenerating` — a deliberate, ledgered transition, never a silent edit. The capture step
  is the ledger delta + pattern that prompted the revision.

## Step 2 — Author the spec draft

Produce a spec cell with: target state, acceptance criteria as **checkable predicates**,
preconditions/postconditions, invariants, and explicit non-goals (Design-by-Contract).
Criteria that cannot be checked mechanically or by a calibrated reviewer are not criteria —
do not write them.

## Step 3 — Grade (auto-research hill-climb)

Score the draft against `spec-quality.rubric.json`; improve the **weakest dimension**;
re-score; repeat until gates pass and the review aggregate clears threshold. The grade is
run by a **critic that is not the authoring agent**, and the passing signal is written by
the validation path. The rubric must itself be validated before it gates here.

## Step 4 — Decompose (the morphism to constituent parts)

Once the spec cell is validated, produce the typed delta the factory operates on.

**Scope-ladder decomposition.** Intent exists at every rung: `fleet mission → system
product intent → workflow job-to-be-done → task acceptance criteria → call prompt`. Refine
the parent spec down the ladder (lineage: KAOS/i* goal refinement, HTN). For each unit the
spec implies, mint:

- a child **spec cell** (`spec.{childscope}.{slug}`) at `defined`,
- the **rubric cell** it binds to (`rubric.{scope}.{slug}`) — its acceptance,
- any **other-layer cells** the unit needs (policy, capability, protocol) at `absent`/`defined`,
- a **ticket** (`tkt-`) whose `target_cell` is the cell to advance, with `target_transition`,
  `acceptance` → the rubric cell, a budget, and declared dependencies — emitted at `draft`.

**Dependency edges** respect the layer partial order (a child rubric cell depends on its
child spec cell; nothing binds a rubric before its spec).

**Entailment proof (deterministic).** `_entailment_check.py` verifies decomposition
soundness: satisfying the child specs must entail satisfying the parent. It checks coverage
(every parent criterion → ≥1 child cell), binding (every child acceptance → a rubric cell),
orphans (no child criterion unmapped to the parent), and partial-order legality of the
edges. A decomposition without a passing proof is not done; the spec returns to
`regenerating`.

## Step 5 — Seed and emit

Apply the lattice-seed delta (new cells appear on the grid at honest maturity) and emit the
ticket batch into the coordination corpus at `draft`. The `ticket-triager` then promotes
each to `active` once the ready-gate passes (target cell exists, acceptance bound to a
*validated* rubric, budget set, deps declared) — at which point the outer loop can pick
them up. The intake capability hands off to the operating loop here.

## Migration Nuances

Brownfield intake is where most real adoption happens, and its failure mode is silent
under-specification: a legacy doc that *reads* complete but never named its boundaries.
Migration must surface those gaps as explicit open items and fill them through the same
grade loop — a migrated spec clears the identical rubric a greenfield spec does. Never
grandfather a legacy spec to `validated` on the strength of its prose; it earns validation
by signal like everything else.

## Spec-Intake Failure Modes

Drafting before capturing intent (building on a guess). Prose-only acceptance criteria
(uncheckable; the loop cannot converge). Decomposition that covers but does not entail
(ships gaps). Grandfathering legacy specs without a signal (drift wearing the costume of
documentation). The authoring agent grading its own spec (the split exists to prevent it).
Decomposition by inference where the entailment check should compute (a hallucination
surface dressed as flexibility).
