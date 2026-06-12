# harness-forge

**Hydrate a project to run looping, latticed agentic workflows.** A kernel that scaffolds and operates a typed knowledge **lattice** — nine declarative layers × five scopes × a maturity state machine — and drives the engine, the compass, and the regeneration loop over it. A self-contained plugin with zero cross-plugin dependencies.

Where `agent-ops` *advises on and reviews* agentic systems (methodology + a named-practitioner council), harness-forge **is the running machine**: it installs the lattice state, the gates, and the operating agent roster into your project, and runs the loop. agent-ops is the coach and the reviewer; harness-forge is the harness.

---

## Quick start

```text
/plugin marketplace add kimgranlund/claude-plugins
/plugin install harness-forge@plugins-forge
```

```text
/harness-seed   "invoice-parser — turn a PDF invoice into a typed record"   # scaffold .harness/ + the first slice
/harness-scan                                                               # the open/stale gap set at the frontier
/harness-next                                                               # the next cell, ranked, dependency-ready
/harness-advance  spec.task.parse-invoice                                   # run define→create→validate on one cell
/harness-distill                                                            # ledger windows → patterns
/harness-audit                                                              # score the harness; read the earned autonomy tier
```

---

## The model — best-first search over a knowledge lattice

Developing an agentic system is converting uncertainty into **validated, typed knowledge assets**. The project's state at any moment is the state of those assets; "what should we work on next?" is a *selection function over a lattice of cells*, not a planning meeting.

- **The lattice** — layers × scopes. A **cell** is one layer at one scope (`{layer}.{scope}.{slug}`) carrying one **maturity** state. Canonical state in `.harness/lattice.json`; every other view is derived.
- **The engine** — `define → create → validate` on one cell at the smallest scope that yields signal. One pass is one closed loop: the cell is its scope, the rubric+harness its verifier, the signal its stop condition.
- **The compass** — *scan* (detect gaps across the modality axis) + *rank* (`(risk × unlock) ÷ probe-cost`, dependency-filtered). Two functions, never conflated.
- **The regeneration loop** — operating cells emit ledger entries → entries distill into patterns → patterns propose upstream revisions. A frozen lattice is drift in the costume of documentation.

The partial order the kernel enforces (a rubric before its spec scores vibes):

```
ontology + spec → rubric, policy, capability → methodology, protocol → ledger schema → (operate) → pattern ──feedback──▶ spec
```

The full theory is in `references/agentic-systems-foundations/` (the ontology, the nine layers, the lattice model, evals & verification, autonomous long-running systems, typed naming).

---

## The surface — five primitives over the kernel

```text
harness-forge/
├── bin/        the kernel (stdlib Python)   → lattice.py · ledger.py · naming.py · gate-signal · harness-hook · lattice-mcp.py
├── commands/   6 thin entry points          → seed · scan · next · advance · distill · audit
├── skills/     2 posture skills             → harness-build (operate) · harness-evaluate (audit + score)
├── agents/     4 operating actors           → harness-builder (orchestrator) · harness-advancer · harness-auditor · harness-distiller
├── hooks/ + bin/  advisory hook             → harness-hook flags naming/staleness on save (never blocks)
├── .mcp.json + bin/  read-only MCP          → lattice-query over the project's .harness/ state
├── schemas/    the typed data               → Cell · Lattice · Naming (self-hosting) · Signal
└── references/ the standard                 → the 14-file agentic-systems foundations + the harness rubric + the operating procedure
```

- **The one law that makes it real** — *computation routes to code, never to inference.* Selection, ranking, dependency readiness, and staleness propagation are deterministic scripts (`bin/lattice.py`), because a model-predicted computation is a hallucination surface. The model supplies the *judgment inside a cell*; the *bookkeeping between cells* is the kernel's. Every `bin/` script ships a `selftest`.
- **Gates block, feedback injects** — the plugin's session hook (`harness-hook`) is **advisory** (it flags plural layer-dir drift and staleness, and always exits 0). The **blocking** protected-verifier gate (`gate-signal`) is shipped for *your* worker loop, where a worker writing its own signal/rubric/test is a reward-hacking surface — verifier assets become deny-on-write to workers **once you wire `gate-signal` into that loop's PreToolUse** (see [Honest scope](#honest-scope); the auto-installer is on the ROADMAP).
- **The MCP is a curated read perimeter** — `lattice-query` surfaces the lattice cells, the frontier gap-set, the ledger, and the signals read-only; the engine that writes them stays in `bin/`.

---

## Honest scope

- **The kernel mechanizes the mechanizable** — the lattice graph, the partial order, typed naming, staleness, the ledger, the false-pass metric. These are scripts with selftests, not taste.
- **The judgment stays the model's** — defining what *done* means (the spec), writing a cell's asset, calibrating a rubric. No regex decides those; the engine routes them to the worker, and the rubric scores them.
- **Autonomy is earned, not declared** — the trust trajectory advances a loop family by a *measured* false-pass rate (< ~5%) and zero reward-hacking incidents, read from the ledger. `ledger.py false-pass` returns **`unmeasured`** (not a misleading 0%) until an independent refuter exists — the absence of bad news is not evidence. The harness's own claim of "production-ready" is a finding, never a verdict.
- **The protected-verifier gate is *shipped*, not yet *auto-wired* (the headline v0.1 limitation).** `gate-signal` is a real, selftested deny-on-write gate, and `validate.py` mints signals from an external command's exit status — so the loop genuinely closes. But the plugin's *session* hook is deliberately advisory-only (a blocking gate in a shared session would be hostile), and the **blocking** gate must be wired into *your* worker loop's PreToolUse config. Until you wire it (the auto-installer is on the ROADMAP), "the worker cannot write its own verifier" is enforced by the worker carrying no signal-write tools **plus your discipline** — not yet purely mechanically. Every "deny-on-write" claim in this plugin is scoped to "when `gate-signal` is wired."
- **v0.1 is the kernel + the operating roster, validated and selftested.** The seed-into-loop gate installer, the structural-critic council, verifier-adapter library, calibration fixtures, and family **kits** are on the [ROADMAP](ROADMAP.md).

---

## Provenance

harness-forge is an **instance of the system it describes**: its own foundations are a lattice (documents are cells; they carry maturity; they go stale when upstream changes). It was authored and is red-teamed against the catalog's plugin standard with **plugins-factory** — its `bin/` selftests, manifest, and trust boundaries pass the harness gates. Self-contained by design: zero `../` cross-plugin paths, zero dependencies.
