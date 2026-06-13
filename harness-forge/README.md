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
/harness-seed   "invoice-parser — turn a PDF invoice into a typed record"   # scaffold .harness/ + the first slice + offer to wire the gates (consent-gated)
/harness-scan                                                               # the open/stale gap set at the frontier
/harness-next                                                               # the next cell, ranked, dependency-ready
/harness-advance  spec.task.parse-invoice                                   # run define→create→validate on one cell
/harness-run      --max-cells 8 --max-iterations 12                         # the BOUNDED autonomous loop (halts on caps / no-progress)
/harness-distill                                                            # ledger windows → patterns
/harness-audit                                                              # score the harness; read the earned autonomy tier
/harness-council                                                            # the 7-critic structural panel (parallel isolated)
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
├── bin/        the kernel (stdlib Python)   → lattice.py · ledger.py · naming.py · validate.py · wire.py · council-precheck.py · gate-signal · gate-budget · emit-ledger · propagate-staleness · harness-hook · lattice-mcp.py
├── commands/   8 thin entry points          → seed · scan · next · advance · run · distill · audit · council
├── skills/     2 posture skills             → harness-build (operate) · harness-evaluate (audit + score)
├── agents/     4 operators + the council    → harness-builder (the bounded /harness-run loop) · harness-advancer · harness-auditor · harness-distiller · harness-council + 7 critic-* structural critics (one per rubric dimension, parallel isolated)
├── hooks/ + bin/  advisory hook             → harness-hook flags naming/staleness on save (never blocks)
├── .mcp.json + bin/  read-only MCP          → lattice-query over the project's .harness/ state
├── schemas/    the typed data               → Cell · Lattice · Naming (self-hosting) · Signal
├── evals/      the behavioral evidence      → calibration fixtures (4 planted defects, gate-caught + judge-baselined) · the first-slice walkthrough · the stop-gate (the wired circuit breaker halts a runaway loop) — all CI-replayed
└── references/ the standard                 → the 14-file agentic-systems foundations + the harness rubric + the operating procedure
```

- **The one law that makes it real** — *computation routes to code, never to inference.* Selection, ranking, dependency readiness, and staleness propagation are deterministic scripts (`bin/lattice.py`), because a model-predicted computation is a hallucination surface. The model supplies the *judgment inside a cell*; the *bookkeeping between cells* is the kernel's. Every `bin/` script ships a `selftest`.
- **Gates block, feedback injects, propagation cascades** — the gateverb hook species from the typed grammar, all shipped. The plugin's *session* hook (`harness-hook`) is **advisory** (flags plural layer-dir drift and staleness, always exits 0). For *your worker loop*, `bin/wire.py apply` (offered by `/harness-seed`, **consent-gated, never silent**) installs into the project's own `.claude/settings.json`: `gate-signal` (PreToolUse **deny** on signals, rubrics, schemas, the ledger, the hooks, and the wiring itself — a worker cannot unwire the gate it runs under), **`gate-budget`** (PreToolUse **deny** on a write to a `blocked` cell — the wired circuit breaker that bounds even a runaway worker), `emit-ledger` (PostToolUse audit trail), and `propagate-staleness` (PostToolUse staleness cascade). `wire.py check` proves the wiring (exit 0 = wired, and **fails on a drifted kernel copy**); `wire.py unwire` reverses it exactly.
- **The loop is bounded** — `/harness-run` dispatches the `harness-builder` orchestrator to advance the frontier automatically under hard caps (max-cells · max-iterations · wall-clock). The no-progress detector (`ledger.py no-progress`, code) flags a cell stuck on repeated failures; the orchestrator blocks it; `gate-budget` enforces the block. Attended by design — it reports at every stop and never raises its own caps. Autonomy is **earned, not declared** (run attended until `ledger.py false-pass` shows a track record).
- **The MCP is a curated read perimeter** — `lattice-query` surfaces the lattice cells, the frontier gap-set, the ledger, and the signals read-only; the engine that writes them stays in `bin/`.
- **The council is structural, not named-practitioner** — `/harness-council` convenes 7 critics keyed to the model's failure-mode clusters (partial-order · verifier-integrity · reward-hacking · naming · budget · autonomy · staleness), each owning a rubric dimension, each `Read/Grep/Glob`-only (they review *untrusted* harnesses, so they cannot execute), fanned out **in parallel isolated contexts** by the `harness-council` orchestrator — which first runs the kernel's read-only gates as the deterministic anchor block, then synthesizes convergence, caps, and the **earned autonomy tier**. Named-practitioner critique stays in `agent-ops`; this panel judges *structure*.

---

## Honest scope

- **The kernel mechanizes the mechanizable** — the lattice graph, the partial order, typed naming, staleness, the ledger, the false-pass metric. These are scripts with selftests, not taste.
- **The judgment stays the model's** — defining what *done* means (the spec), writing a cell's asset, calibrating a rubric. No regex decides those; the engine routes them to the worker, and the rubric scores them.
- **Autonomy is earned, not declared** — the trust trajectory advances a loop family by a *measured* false-pass rate (< ~5%) and zero reward-hacking incidents, read from the ledger. `ledger.py false-pass` returns **`unmeasured`** (not a misleading 0%) until an independent refuter exists — the absence of bad news is not evidence. The harness's own claim of "production-ready" is a finding, never a verdict.
- **The protected-verifier gate is wired by consent, never silently.** `gate-signal` is a real, selftested deny-on-write gate, `validate.py` mints signals from an external command's exit status, and `bin/wire.py apply` installs the blocking enforcement into *your* loop — but only after `wire.py plan` shows you exactly what changes and you say yes (the plugin's own session hook stays advisory by design; a blocking gate in a shared session would be hostile). The wiring state is **checked, not assumed**: `wire.py check` exit 0 is the mechanical claim "the worker cannot write its own verifier — or unwire the gate"; before that, the protection is the worker's narrow tool scope plus your discipline, and the plugin says so rather than overclaiming. The wired kernel is **version-stamped** — `wire.py check` fails (not warns) when the copy has drifted from an updated plugin, so a stale loop can't read as healthy.
- **The kernel is mechanically verified; the council is model judgment, and the difference is disclosed.** Every `bin/` script selftests and the first-slice walkthrough replays the whole loop in CI — that half is behaviorally proven. The **structural council** (`/harness-council`) is the model half: no script can verify a critic *found the right thing*, so its committed run records are **expected-output specifications** (recall-gated for the concepts a correct panel must name), not captured transcripts. Don't read "judge-baselined" as "judge-verified." A real, dispatch-ID'd council run lives in `reviews/`.
- **The council carries a standing context cost** — its 7 critics + orchestrator are eagerly-loaded agent descriptions, part of a ~1.6K-token always-on tax this plugin charges every session whether or not you convene a panel (run `plugins-factory/bin/context-cost.py plugin harness-forge` for the live number). It is the price of bundling the reviewer with the machine; trimming that, or splitting the council into its own plugin, is on the [ROADMAP](ROADMAP.md).
- **v0.4 is the kernel + the operating roster + the wired loop + the bounded autonomous loop + the structural council, validated, selftested, and behaviorally evidenced.** CI replays the whole engine loop (`evals/first-slice-walkthrough/`), proves the wired stop-gate halts a runaway loop (`evals/stop-gate/`), and proves the gates catch the planted defect classes while a clean control passes (`evals/calibration/`, recall-gated). The council-as-separate-plugin, the discriminated-union schema (evidence-less validation made unrepresentable), verifier adapters, and family **kits** are on the [ROADMAP](ROADMAP.md).

---

## Provenance

harness-forge is an **instance of the system it describes**: its own foundations are a lattice (documents are cells; they carry maturity; they go stale when upstream changes). It was authored and is red-teamed against the catalog's plugin standard with **plugins-factory** — its `bin/` selftests, manifest, and trust boundaries pass the harness gates. Self-contained by design: zero `../` cross-plugin paths, zero dependencies.
