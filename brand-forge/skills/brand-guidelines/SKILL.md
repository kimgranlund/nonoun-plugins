---
name: brand-guidelines
description: >
  Build a high-quality brand-guidelines section in the corpus by GUIDED CHOICE — the system presents a 2×2
  of options for each brand domain (mark · voice · color · type · expression · governance), you pick a
  quadrant (A/B/C/D) + comments/corrections, and the choices accumulate into a provenance-traced, attributed
  guidelines corpus. Use when building, eliciting, or structuring a brand's guidelines, design system, or
  expression rules through an interactive multiple-choice loop. Triggers on "build brand guidelines", "brand
  design system", "guide me through the brand system", "2x2 options for the brand", "elicit the color/type/
  voice system", "help me decide the brand expression", "assemble a brand guidelines section". This skill
  MAKES guidelines (the guided maker); it does NOT grade them — scoring is brand-evaluate (in-plugin) and the
  parallel design-skills:brand-decomposer (deeper operability check, when installed). NOT for strategy /
  positioning (brand-methodology) or naming / copy (brand-copywriter).
---

# Brand Guidelines — the guided 2×2 elicitation loop

Most brand-guidelines docs are written by one person guessing, then policed. This skill **builds them by guided choice**: for each brand domain the system proposes a **2×2 of concrete options**, you pick a quadrant and comment, and the choices **accumulate** into a coherent, evidence-traced guidelines section in the corpus. The model proposes the options; **you supply the taste**; code owns the accumulating state and (later) the assembly.

This file is the table of contents; the full mechanism is in [`references/the-loop.md`](references/the-loop.md).

## The loop (per domain)

The loop walks **six domains** — `mark · voice · color · type · expression · governance` — with the **brand idea** (from `01-foundation`) sitting above them as what every option must trace to. For each domain:

1. **Frame** — read `01-foundation` + the accumulated choice-ledger; pick the domain's **two axes** (a default pair, below; the model may swap with a stated reason; you may override) → a 2×2.
2. **Generate** — four **design-move cards** (A/B/C/D), one per quadrant, each a concrete move grounded in the foundation + a cited exemplar + the quality bar. Never generic, never "on-brand" — each names a causal mechanism.
3. **Present** — the 2×2 as a Markdown grid + the four lettered cards; ask for **A/B/C/D + free-text comments/corrections**.
4. **Capture** — append a typed **choice** to the ledger (the chosen move, amended by your comment, with contributors + exemplar evidence). A comment like *"B but warmer"* records the amended move **and** re-renders a refined card for confirmation.
5. **Drill or advance** — if the domain's capture spec has unresolved sub-decisions, spawn a **finer 2×2** within the chosen quadrant; else advance. Earlier choices **constrain** later domains (coherence).

The ledger is the state — the loop resumes at the frontier. It MAKES; it never grades its own output (that split is below).

## The seven axes (cross two → a 2×2)

`functional↔expressive · product-led↔human-led · quiet↔loud · literal↔metaphorical · premium-restraint↔campaign-loudness · institutional↔conversational · systematic↔organic`

Default axis pair per domain (the model may swap with a reason): **mark** literal↔metaphorical × systematic↔organic · **voice** institutional↔conversational × functional↔expressive · **color** functional↔expressive × restraint↔loudness · **type** systematic↔organic × functional↔expressive · **expression** quiet↔loud × premium-restraint↔campaign-loudness · **governance** systematic↔organic × product-led↔human-led.

## The choice-ledger (mechanized state)

Each pick appends a typed entry to a **choice-ledger** (the cumulative knowledge), kept in the corpus and **validated by `bin/guidelines-ledger`** (well-formed by construction — the score-record/assess-record discipline). Append-only with `supersedes` for revisions (never rewrite a decision). → the entry shape + enums: `bin/guidelines-ledger schema`, and [`references/the-loop.md`](references/the-loop.md).

## Assembly + scoring (the loop closes)

When the domains are covered, the **assembler** (a later increment) compiles the ledger into corpus docs — each rule typed `must/should/may`, written as a causal mechanism, carrying **`sources:`** (the choices + exemplars) and **`contributors:`** (you + the system) frontmatter — so `corpus-provenance` gates the trace and **`brand-evaluate` scores** the result against the brand-guidelines bar. The build loop closes into the evaluate loop.

## Relationship to brand-decomposer (parallel, not a dependency)

`design-skills:brand-decomposer` (the `nonoun-skills` marketplace) is the **grader/operability lens** for a brand spec — the 100-pt rubric, the typed schema, the WCAG/provenance checker, the six domains + seven axes this skill mirrors. The split is **by verb: brand-decomposer GRADES/decomposes/critiques; brand-guidelines MAKES.** They are **parallel** (brand-forge is self-contained; brand-decomposer is a different marketplace) joined by an **optional seam**: the assembler can project a `*.brand.json` card that brand-decomposer grades when installed. We mirror its vocabulary; we do not depend on it.

## Boundaries

- **Makes, doesn't grade** — scoring is `brand-evaluate` (in-plugin) + `brand-decomposer` (when installed).
- **Guidelines, not strategy** — the position/POV is `brand-methodology` (this loop *descends from* `01-foundation`, it doesn't decide it).
- **Structure, not copy** — voice *behavior* here; the actual words are `brand-copywriter`.
- → Full mechanism, the design-move card, drill-down, coherence graph, assembly, the seam: [`references/the-loop.md`](references/the-loop.md).
