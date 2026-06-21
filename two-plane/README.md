# two-plane — the two-plane orchestrator

Plan or review a system on **two planes** in isolated contexts, cross-check the seam, and maintain both
docs over time. The OUTSIDE-IN **Charter** (goals: *what are we trying to do, how will we know it's
good?*) and the INSIDE-OUT **Blueprint** (structure: *what holds it up?*) — reasoned separately so
neither pollutes the other, then checked where they meet.

Design + rationale: [`../docs/designs/two-plane-orchestrator.md`](../docs/designs/two-plane-orchestrator.md).

## Why it exists

Holding both planes in one context corrupts the analysis — an elegant structure bends your read of the
goals; the goals' narrative narrows the structural exploration. But the planes are *dependent* (the
structure serves the goals), so blind isolation yields "an elegant solution to the wrong problem." This
orchestrator enforces **staged isolation**: goals first/alone → structure given only the goals'
*constraints extract* → a fresh-context cross-check of the seam.

## Layout

```
two-plane/
  bin/two-plane.py        deterministic core — extract · crosscheck · staleness · hash · lattice · record · selftest
  bin/two-plane-mcp.py    read-only MCP query surface over a project (get_charter · get_blueprint · lattice_status · crosscheck · read_ledger)
  lattice.json            the durable 4-cell graph (spec.charter → capability.blueprint → rubric.cross-check + ledger)
  .mcp.json               template MCP config (set absolute paths — two-plane is a harness dir, not a plugin)
  agents/
    charter-author.md     Stage A — authors the Charter (loads goals-decomposer), no architecture in scope
    blueprint-author.md   Stage B — authors the Blueprint (loads architecture-decomposer), gets ONLY the extract
    critic-coverage.md    Stage C council — is each ranked goal really served (not just named)?
    critic-contradiction.md  Stage C council — does the structure honor the principles in spirit?
    critic-feasibility.md    Stage C council — can any structure meet this, and does this one?
  commands/two-plane.md   the bounded, attended loop (intake → charter → extract → blueprint → cross-check → commit → maintain)
```

## How it maps onto the harness (`.agents/harness`)

It **extends the harness conventions** rather than adding a new plugin: the two planes are a small
lattice —

```
spec.workflow.charter      → capability.workflow.blueprint  → rubric.workflow.cross-check
(goals-decomposer GOVERNABLE)  (architecture-decomposer holds)   (the gated seam)
ledger.workflow.events     every produce / grade / extract / cross-check / regeneration
```

A Charter change stales the Blueprint sections that cite the changed characteristic (section-level), via
`two-plane.py staleness`, and triggers a scoped regeneration.

## Run

```sh
python3 bin/two-plane.py selftest                          # prove the core
python3 bin/two-plane.py extract charter.json              # the Blueprint agent's ONLY view of the charter
python3 bin/two-plane.py crosscheck charter.json blueprint.json   # the seam gate
python3 bin/two-plane.py staleness charter.json blueprint.json    # which mechanisms went stale (section-level)
python3 bin/two-plane.py lattice lattice.json charter.json blueprint.json --update  # propagate drift across the cells
python3 bin/two-plane.py record ledger.jsonl '{"event":"crosscheck.pass",...}'      # append to the ledger
```

The durable state is `lattice.json` (the 4-cell graph + maturities) + a `ledger.jsonl` (gitignored
runtime, append-only). `lattice … --update` flips the blueprint + cross-check cells to `stale` when the
charter drifts; the orchestrator then regenerates only the stale sections and re-runs the cross-check.

The loop itself is the `/two-plane` command (or dispatch the agents directly). The deterministic gate is
necessary, not sufficient — the council judges whether coverage is *real*, principles are honored *in
spirit*, and thresholds are *feasible*; the irreducible tensions it surfaces are decisions for a human.

## The MCP query surface (optional, read-only)

So *other* agents can read the current two-plane state as shared, citable context without re-deriving it,
`bin/two-plane-mcp.py` exposes a small read-only MCP server (`get_charter` — with `extract:true` for the
prose-stripped view · `get_blueprint` · `lattice_status` · `crosscheck` · `read_ledger`). Wire it via the
`.mcp.json` **template** — two-plane is a harness-convention dir, not a plugin, so set the absolute path
to `bin/two-plane-mcp.py` and point `TWO_PLANE_DIR` at your project's folder. Prove it with
`python3 bin/two-plane-mcp.py selftest`.
