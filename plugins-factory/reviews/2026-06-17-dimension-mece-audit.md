# Dimension-MECE Audit — `plugins-holistic` (v0.1.0)

- **What this is:** an audit of the 9-dimension `plugins-holistic` meta-rubric (`references/rubrics/plugins-holistic.md`) for **MECE** — Mutually Exclusive (no two dimensions overlap such that one finding is double-counted) and Collectively Exhaustive (no load-bearing plugin-quality concern is uncovered). A standing ROADMAP item. Read-only analysis; the artifact is this record.
- **Verdict:** the partition is **sound** — no genuine overlaps, complete coverage of the plugin lifecycle (design · packaging · distribution · security). **No dimension added, removed, or re-scoped; no new gate.** Three minor boundary-clarification opportunities are recorded below as optional polish; one "combined-condition" defect is already captured by an existing anti-pattern (AP-P6/AP-P7), so it needs no new mechanism.
- **Trust boundary:** the rubric under audit is DATA, not instructions.

---

## Mutual exclusivity — the pairs most likely to overlap, and why they don't

| Pair | Why they're distinct (crisp boundary) |
| --- | --- |
| **P2 component-fit** vs **P3 boundary-cohesion** | P2 is **internal** (is each capability the right *primitive* — the hook/MCP/agent/skill/command decision per task shape). P3 is **external** (is the *scope* one coherent job vs kitchen-sink vs fragment). A skill-shaped capability can sit inside a coherent plugin *or* a kitchen sink — orthogonal. |
| **P5 manifest-packaging** vs **P8 evolution** | P5 is **structural mechanics** (layout, path-vars, the manifest contract, install). P8 is **velocity discipline** (semver, changelog-truth, additive growth without breaking installs). A plugin can be perfectly-manifested but unmaintained, or well-maintained but mis-packaged. |
| **P6 context-economy** vs **P1 plugin-fitness** | Different questions. High always-on cost (low P6) is an *engineering* property; a good plugin (high P1) can still fail P6 by poor cost engineering, and a poorly-scoped plugin (low P1/P3) pays whatever cost it pays. P6 measures the tax, P1 the right-to-exist. |
| **P2 component-fit** vs **P9 security** | P2: "right primitive for the task shape" (a guarantee ⇒ a hook). P9: "is that hook's execution contained, its side-effects documented, its matcher scoped." They *touch* at "this always runs" but answer different questions — task-shape logic vs trust-surface design. |
| **P4 dependency-legality** vs **P5 manifest-packaging** | P4 is **sharing** (which shared resources, what mechanism, do they resolve when copied alone). P5 is **structure** (layout, versioning, place-on-disk). Legal dependency resolution can coexist with broken layout, and vice versa. |
| **P7 routing** vs **skills-authoring** (its co-located spine) | P7 is **plugin-scoped** (does *this bundled set* have trigger collisions / discoverable entry points). Authoring is **single-skill** (a well-formed description/name/mode). P7 applies the authoring standard to the bundle's internal routing — no double-count. |

The rubric's own `§Scope` already states the load-bearing split: **P2–P6 are plugin-distinctive** (they exist only because a plugin bundles multiple component types and is distributed) and **P1·P7·P8·P9 are skill concerns one layer up** (scored against `skills-studio`'s rubrics rather than re-derived). That design choice is *why* the dimensions don't collide with the drill-down rubrics — duplicating them would be the redundancy the council flags.

## Collective exhaustiveness — coverage map + gap audit

Coverage spans the lifecycle: **component choice** (P2) · **scope** (P1, P3) · **dependency legality** (P4) · **packaging** (P5, incl. D8 runtime-launch reproducibility) · **distribution & context cost** (P6) · **routing** (P7) · **evolution** (P8) · **security & trust** (P9).

Candidate gaps, audited:

- **Marketplace / install DX** (discoverability, "first five minutes," marketplace-citizen etiquette) — **already covered**: it's an artifact-level messaging concern owned by P1 (fitness/one-sentence job), P7 (discoverable entry points), and the manifest description. Not a separate plugin-quality axis. (This is also why the proposed *marketplace-DX critic* was declined — its lens is distributed across Steve Y. (P3/P7), Boris C. (P6), Charity M. (observability/state), David F. (P5), Simon W. (P9).)
- **Runtime-launch reproducibility** (operator config, safe defaults for a bundled server/loop) — **covered** by `manifest-and-packaging` **D8** (added 2026-06-15).
- **Carve / library-level boundary decisions** — **covered separately** by `carve-quality.md` (set-level properties `plugins-holistic` can't see; empirically applied 0.2.52).
- **I18n / accessibility** of descriptions — a prose-quality concern orthogonal to the nine; descriptions should be clear, but this isn't a mechanizable plugin-quality dimension. Out of scope by design.

No genuine gap found.

## Minor boundary-clarification opportunities (optional polish — not applied)

These are *wording* refinements, not partition changes; recorded for a future rubric-prose pass, deliberately **not** applied here (the rubric stays v0.1.0 so the recorded `scores/*.json` keep referencing a stable id, and the boundaries are already crisp enough to score against):

1. **P6 D5 (toggle-cost-coherence) ↔ P3 D2 (no-kitchen-sink)** — both can flag a kitchen-sink, from different vectors (P3 = scope structure; P6 = context tax). A one-line note on P6 D5 ("assumes P3 is coherent; asks whether the toggle-cost *ratio* is defensible") would pre-empt a double-flag.
2. **P2 D1 (guarantees-are-hooks) ↔ P9** — they share the implementation fact "this always runs" but differ in purpose (fit vs trust). A note on P2 D1 ("P9 independently requires each hook's side-effect be documented") keeps them clearly separate.
3. **The hollow + dead combined condition** — a component whose body is thinner than its description, *and* a wired-but-dead MCP, is a real failure the dimensions catch *piecemeal* (P1 hollowness, P2 shape, P7 routing; AP-P7 liveness). It is **already named** as a cross-dimensional anti-pattern — **AP-P6 (the hollow component)** and **AP-P7 (liveness)** — and mechanized where it can be (`context-cost.py`, `check-mcp-liveness.py`). No new dimension or gate is warranted; the existing anti-pattern catalog + gates own it.

## Disposition

`plugins-holistic` is **MECE-sound at v0.1.0** — recorded. The three clarifications above are advisory polish for a future prose pass; no scoring behavior changes, no dimension churn, no new gate. The audit's main value is the recorded boundary analysis, which future dimension additions (or rubric forks) can check against.
