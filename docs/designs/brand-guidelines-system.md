# Design: the brand-guidelines elicitation system (brand-forge)

**Status:** DRAFT for review — no implementation yet. **Owner:** Kim. **Date:** 2026-06-20.

A guided, choice-driven way to **build a high-quality brand-guidelines section in the corpus**, component by component: the system presents a **2×2 matrix of options** for each component of a brand design system, the designer picks (**A/B/C/D + comments/corrections**), and the choices **accumulate** into a coherent, provenance-traced, attributed guidelines corpus that `brand-evaluate` then scores against an explicit "high-quality" bar.

This document is the complete shape to approve before building. It is grounded in a review of the prior prototype (`~/Downloads/brand_guidelines_agentic_corpus`) and in brand-forge's existing architecture (the corpus model + the `00-sources`/provenance work shipped in 0.4.27–0.4.29).

---

## 1. What we're carrying forward (and what we're not)

The prior prototype is a mature **ingestion spec** — a pipeline for turning third-party brand-guideline *decks* into typed, evidence-cited JSONL records. It is all scaffolding, zero ingested content, and the **2×2 guided-build mechanism is not in it** — that is net-new. But five assets transplant directly:

| Salvaged asset | Role in this system |
|---|---|
| **100-point "High-Quality Brand Guidelines" rubric** (9 weighted areas + weak/strong fast-audit) | The explicit quality definition; becomes a `brand-evaluate` rubric the assembled output is scored against. *"A brand operating system, not a logo rulebook."* |
| **16-component ontology** + per-component capture specs | The list the loop **walks** — one elicitation track per component. |
| **7 exploration axes** | The raw material for the **2×2** — cross two → four quadrants → four option cards. |
| **Typed records** — `brand_rule` (rule_type × must/should/may × context), `brand_relationship` (10 edge types), the **design-move** object | What a quadrant *emits* and a pick *captures*; the relationship graph carries cross-component coherence. |
| **Evidence/provenance discipline** (`evidence_ref` + confidence + Observed/Inferred/Proposed) + the 17-brand annotated exemplar catalog | Maps onto `00-sources` + provenance; the exemplars seed option-generation. |

What we explicitly **drop**: the deck-scraping pipeline (wrong center of gravity — we *generate* via guided choice, not *ingest* decks; ingestion is optional later plumbing for seeding exemplars). We also reconcile the prior work's schema drift (`BrandToken`/`BrandRelationship` were in the TS but missing from the JSON Schema) into one source of truth.

---

## 2. Core concepts

### 2.1 The component ontology (what the loop walks)

The 16 `brand_domain` components, in a load-ordered walk (strategy first; governance closes):

`strategy · voice · logo · color · typography · layout · photography · illustration · iconography · motion · product-ui · dataviz · social · marketing · packaging/environmental · co-branding · governance`

Each component carries a **capture spec** — the sub-decisions a *complete* treatment of it must resolve (e.g. color: roles · meaning · ratios · light/dark · contrast/accessibility · product vs. marketing usage · misuse). The capture spec is both the **drill-down map** (what finer 2×2s a component spawns) and the **coverage checklist** (when is this component "done"). These map onto the corpus layers: identity→`03`, expression→`04`, voice→`05`, product→`06`, governance→`07`.

### 2.2 The 7 exploration axes + the 2×2 recipe

The seven polar axes: **functional↔expressive · product-led↔human-led · quiet↔loud · literal↔metaphorical · premium-restraint↔campaign-loud · institutional↔conversational · systematic↔organic**.

A **2×2** for a component = **two axes crossed** → four quadrants. Example (color): *functional↔expressive* × *restrained↔loud* →
- **A** functional+restrained — a tight semantic palette; color as UI role.
- **B** expressive+restrained — a signature accent on a neutral base.
- **C** functional+loud — high-energy but systematic; color-as-data.
- **D** expressive+loud — saturated brand-as-color, campaign-forward.

**Axis-selection** is a design decision (§7, Open Q1). Recommended: a **deterministic default axis-pair per component** (a code mapping — "computation routes to code"), which the model may swap with a stated reason and the designer may override. Deterministic-by-default keeps the experience predictable and resumable; the model adapts only with justification.

### 2.3 The design-move object (what a quadrant is, what a pick captures)

Each quadrant renders as a concrete **design-move card**, grounded in the brand's `01-foundation` and a cited exemplar:

```json
{
  "move": "A signature accent on a near-neutral base — one hot color, used sparingly as the brand's 'tell'",
  "domain": "color",
  "quadrant": "B",
  "axes": ["functional↔expressive", "restrained↔loud"],
  "rationale": "Lets the foundation's 'quiet confidence' read while still owning one ownable color",
  "expected_effect": "Recognition at a glance without shouting; high contrast headroom for accessibility",
  "exemplar_evidence": [{"brand": "Stripe", "what": "blurple accent on white", "why_cited": "restrained-expressive done at scale"}],
  "confidence": 0.8
}
```

A **choice** wraps the chosen move with the designer's input:

```json
{
  "component": "color", "round": 1,
  "presented": ["A","B","C","D"], "chosen": "B",
  "comment": "yes, but warmer — terracotta not blue",
  "move": { /* the chosen design-move, amended by the comment */ },
  "contributors": [{"who": "designer", "role": "chooser", "date": "2026-06-20"},
                   {"who": "brand-guidelines", "role": "proposer", "date": "2026-06-20"}],
  "supersedes": null
}
```

### 2.4 Cross-component coherence (the relationship graph)

Choices are not independent. A loud-expressive color choice should *constrain* the type and imagery options offered later. The prior work's `brand_relationship` edges (`supports · expresses · constrains · contradicts · exemplifies · prohibits · …`) are the substrate: each accepted choice writes edges into a small graph the loop reads when generating the *next* component's 2×2, so later options stay coherent with earlier commitments (and the system can flag a `contradicts` before it's baked).

---

## 3. The elicitation loop (the heart)

For each component in the walk:

1. **Frame** — read `01-foundation` + the accumulated choice-ledger + the coherence graph; select the 2×2 axis-pair (default mapping, model may adapt with reason).
2. **Generate** — four design-move cards (A/B/C/D), each grounded in the foundation + a cited exemplar + the rubric's bar for this component. No generic options — every card names a causal mechanism (never "on-brand").
3. **Present** — the 2×2 + the four cards, and ask for **A/B/C/D + free-text comments/corrections**.
4. **Capture** — write a typed choice record to the ledger (chosen move, amended by the comment, with contributors + exemplar evidence).
5. **Drill or advance** — if the component's capture spec has unresolved sub-decisions, spawn a **finer 2×2** within the chosen quadrant (e.g. B → warm↔cool × single↔family accent); else advance to the next component. Earlier choices constrain the finer ones.
6. **Repeat** until coverage (every component's capture spec resolved, or explicitly deferred).

**Resumability:** the ledger *is* the state. `/brand-guidelines` with no args resumes at the frontier; the loop is a pure function of `(foundation, ledger, graph)`.

**Anti-reward-hacking:** the loop *proposes and records*; it never grades its own output. Quality comes from the independent `brand-evaluate` rubric + the council (the same generation/verification split the rest of the catalog enforces).

---

## 4. Data model & assembly

### 4.1 The choice-ledger (mechanized state)

A typed, append-only ledger of choices + the coherence edges, validated by a schema (well-formed by construction, like `score-record`/`assess-record`). Append-only with `supersedes` for revisions (never rewrite a decision — the corpus write-discipline). **Location** is Open Q3; leading candidate: a working area the assembler reads and the assembled docs `sources:`-cite.

### 4.2 The assembler (deterministic: ledger → corpus)

A `bin/` script compiles the ledger into corpus documents — **no inference in the compile step**:
- Each component's resolved choices → a `04-expression--color.md` / `05-voice--*.md` / etc., with each rule **typed** (`must`/`should`/`may`) and written as a causal mechanism.
- A `07-guidelines` section assembled from the typed rules + the do/don't + the coherence graph.
- Every assembled doc carries **`sources:`** (the choices + exemplars it was built from) and **`contributors:`** (designer + system) frontmatter — so `corpus-provenance` gates the trace and `brand-evaluate` scores the result. **The build loop closes into the evaluate loop.**

### 4.3 Coverage (mechanized)

A coverage check reports, per component, `resolved / partial / absent` against its capture spec — the frontier the loop walks and the "is this guidelines section complete" signal that feeds `08-evaluation`.

---

## 5. Five-primitive mapping

| Primitive | Piece | Mechanized? |
|---|---|---|
| **Command** | `/brand-guidelines [component]` — start/resume the guided build | thin router |
| **Skill** | `brand-guidelines` — the loop methodology + ontology + axes + rubric pointers (references on demand) | the model's judgment |
| **bin + schema** | choice-ledger schema + validator · coverage check · the assembler | **yes — state, coverage, assembly are code** |
| **Rubric** | `brand-evaluate/references/rubric-brand-guidelines.md` (the 100-point bar) | scored |
| **Agents** | option-generation grounded in foundation+exemplars; council/evaluate judge the assembled output | the model's judgment |

**The line:** the model supplies the option *content* and the designer supplies *taste*; **code owns the state, the coverage, the assembly, and the scoring.** (The catalog law: structure is mechanized, taste is not.)

---

## 6. Build increments (after this design is approved)

1. **Knowledge layer** — `rubric-brand-guidelines.md` (lift the 100-pt rubric into brand-evaluate) + the `brand-guidelines` skill with `component-ontology.md`, `exploration-axes.md`, `exemplars.md` (the 17-brand catalog, link-only). *Useful immediately (scores guidelines); foundational for the loop.*
2. **The loop + ledger** — `/brand-guidelines` command + the loop methodology + `schemas/choice-ledger.schema.json` + validator; one component end-to-end (2 axes → 4 cards → pick+comment → ledger entry → drill-down).
3. **The assembler + coverage** — ledger → corpus docs (with `sources:`/`contributors:`); the coverage check; close into `corpus-provenance` + `brand-evaluate`.
4. **Coherence graph** — cross-component constraint + contradiction-flagging.
5. **Exemplar enrichment** — per-component "what good looks like," rights-respecting.

Each increment ships with its selftest/gate and a CHANGELOG/version bump, per the catalog discipline.

---

## 7. Open decisions (resolve before / during build)

1. **Axis selection** — deterministic default pair per component (recommended), full model choice, or designer-driven? (Trade-off: predictability/resumability vs. flexibility.)
2. **2×2 in a text medium** — the matrix + cards render as a Markdown table + lettered cards; the pick is `A/B/C/D + comment`. Confirm this is the intended surface (vs. a future richer UI). Is multi-select / "blend B and C" allowed, or strictly one quadrant + comments?
3. **Choice-ledger location** — `00-sources/` (it is evidence), a dedicated `_elicitation/` working dir, or `.agents/`-style state? Must be `sources:`-citable by the assembled docs.
4. **Drill-down depth** — bounded by the capture spec, or open-ended until the designer says "enough"? A cap keeps rounds finite.
5. **Comments that reshape a move** — when the designer picks B "but warmer," does the system (a) record the amended move verbatim, (b) re-generate a refined card for confirmation, or (c) both? Affects how faithfully the ledger reflects intent.
6. **Exemplar rights** — the 17-brand catalog is link-only/reference-only; how much exemplar *description* can ship in `exemplars.md` vs. live as pointers? (Likely: our own prose describing the *mechanism*, citing the brand, not reproducing their assets.)
7. **Relationship to existing seats** — does option-generation reuse the **Muse** (aspiration) / **methodology** seats, or is there a new `brand-elicitor` agent? (Lean: methodology drives the loop; the Muse can seed the "expressive/loud" end of an axis.)

---

## 8. Risks

- **Net-new interaction UX** — the 2×2 loop has no precedent in the prior work; the text-medium rendering + resumable state is the main build risk. Mitigated by increment 2 prototyping one component end-to-end before scaling.
- **Reward-hacking** — a system that both generates options and assembles output must not also grade it; quality stays with the independent rubric + council.
- **Scope** — 16 components × drill-downs is large; the increment plan delivers value at each step (the knowledge layer + rubric alone are useful without the loop).
- **Coherence vs. freedom** — over-constraining later options from earlier choices can railroad the designer; the graph should *flag* contradictions, not silently forbid quadrants.

---

*Review notes / decisions go inline or in `08`-style append below. Once the shape is approved, increment 1 begins.*
