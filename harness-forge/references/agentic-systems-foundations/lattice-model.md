# The Lattice Model (Completion Frontier)

`Cell: methodology.fleet.lattice-model · Status: defined · Register: synthesis; component lineages established`

## Thesis

Developing an agentic system is best-first search over a knowledge lattice: scan
broadly for missing knowledge modalities, validate narrowly at the smallest scope that
yields decisive signal, and scale only from validated cells — with the ledger closing
the loop back into the lattice. Completeness tells you what is missing. Validation
tells you what is real. Prioritization is the ratio between them.

## Reduction

Building an agentic system is converting uncertainty into validated, typed knowledge
assets. The project's state at any moment is the state of those assets. "What should
we work on next?" is a selection function over a lattice of cells, not a planning
meeting.

## The Five Components

**1 · The Lattice (map).** Layers × scopes (see `agentic-systems-ontology.md` for both
axes). A cell is one layer at one scope. Canonical state lives in `lattice.json`;
cells carry `(layer, scope, slug, maturity, asset_ref, signal_refs,
validated_against_hashes, budget, attempts)`.

**2 · Maturity (state).** Each cell carries one state from the maturity enum.
Validation is scope-relative, and its output is a signal artifact.

**3 · The Engine (operator).** The inner loop advancing one cell:
`define → create → validate` at the smallest scope that yields signal. Lineage: PDCA,
red–green–refactor, build–measure–learn, tracer bullets, eval-driven development. The
probe is sized to the assumption, not the ambition. One engine pass is one closed
loop in the loop-engineering sense; the cell is the loop's scope, the rubric+harness
is its verifier, the signal is its stop condition.

**4 · The Compass (selector).** Two distinct functions, never conflated:

- *Scan* — sweep the modality axis at the frontier scope for absent, stale, or
  unvalidated cells. Scanning detects gaps; it does not rank them.
- *Rank* — order the gap set:
  `priority ≈ (risk concentration × unlock value) / probe cost`,
  subject to dependency readiness. Probe cost is read from ledger data (tokens and
  iterations per prior signal), not estimated, once history exists.

The layer partial order constrains readiness:

```
ontology + spec → rubric, policy, capability → methodology, protocol
              → ledger schema → (operate) → pattern ──feedback──▶ spec
```

A rubric before its spec scores vibes. The ledger's schema sits early even though its
content arrives last: provenance cannot be retrofitted.

**5 · The Loop (regeneration).** Operating cells emit ledger entries; entries distill
into patterns; patterns and anomalies propose upstream revisions. Cells re-enter
`regenerating` deliberately and ledgered — never by silent edit. A cell that stops
regenerating while its environment moves is stale, and stale assets actively
misdirect every consumer that trusts them.

## The Trajectory Rule

Advance depth-first along one thin vertical slice until validated. Widen — new layers,
larger scope — only from validated footholds. Rescan the full modality axis at every
widening.

| Trajectory | Culture | Outcome |
|---|---|---|
| Breadth-first at `defined` | Enterprise-architecture pathology | Everything specified, nothing real |
| Depth-first, never scanning | Hacker pathology | Working demo, missing whole modalities |
| Slice-to-validated, scan-at-widening | Frontier-lab practice | Frontier expansion from evidence |

## Operating Procedure

1. Scan the modality axis at the frontier scope → open/stale cell set.
2. Filter by dependency readiness (partial order).
3. Rank by risk × unlock ÷ probe cost.
4. Run the engine on the top cell at the smallest signal-yielding grain.
5. On signal: mark validated; rescan (validation reveals new gaps).
6. Widen scope only when the slice's load-bearing cells carry signal; rescan all
   modalities at the new scope.
7. Operate; route ledger output back into steps 1–3.

## Loop-Engineering Integration

The lattice is what loop engineering becomes at population scale. A feature-list JSON
with `"passes": false` flags is a degenerate lattice (one layer, two states); this
model generalizes it to nine layers and a full state machine, with transitions gated
mechanically. Four obligations imported from loop practice:

- **Budgets and no-progress detection** are cell-schema fields; exhaustion flips the
  `blocked` condition and surfaces the cell to the compass instead of burning tokens.
- **Verifier maturity is a binding precondition**: a cell advances only against a
  `validated` rubric cell. Flakiness is a maturity violation, not a runtime mystery.
- **Anti-reward-hacking is mechanical**: verifier assets are deny-on-write to worker
  agents; signals are written only by the validation path.
- **Probe cost is measured**, not guessed, once the ledger has history.

## Failure Modes

| Pathology | Corrective |
|---|---|
| Grid-filling (breadth at `defined`) | No second cell at `defined` while the first slice lacks signal |
| Slice-tunneling (no modality scan) | Mandatory rescan at every widening |
| Premature scaling | Signal as the only currency at scope boundaries |
| Rubric-without-spec | Partial order enforced in the dependency filter |
| Retrofitted provenance | Ledger schema in the first slice |
| Frozen lattice | Regeneration loop; staleness as a first-class state |
