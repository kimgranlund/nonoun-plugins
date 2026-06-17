---
description: Brand Stack — condense a brand corpus into a one-page reading (six load-bearing tiers).
argument-hint: "[corpus-dir — default ./brand-corpus]"
---

You are entering **Brand Stack mode**: produce the one-page reading of a brand — six load-bearing tiers (Root · Position · Point of View · Expression · Product · Stewardship), each condensed from a corpus layer. Posture is _editor_: condense ruthlessly to a single sheet; cite the corpus, never invent. This is the executive summary, distinct from `/brand-stamp` (which exports the *whole* corpus as a distributable artifact).

Corpus directory from the user (default `./brand-corpus`): **$ARGUMENTS**

1. **Inventory the corpus.** Invoke the **`brand-corpus`** skill (and the corpus MCP if `corpus_dir` is configured) to read the real layers (`01-foundation` … `08-evaluation`) — work from what's on disk, not memory.
2. **Build the Stack** following the model in the **`brand-methodology`** skill (`skills/brand-methodology/references/brand-stack.md`): the six tiers, the tier↦layer map, and the per-tier *guards-against* bullshit filter. For each tier, extract **one thesis sentence + a ≤50-word elaboration** from its source layer(s).
3. **Render** into `templates/brand-stack-one-pager.md` — monochrome, text-only, one sheet. Any tier whose layer the corpus hasn't reached: render as `— not yet defined (layer NN missing)` and name what's missing (maturity is shown, never faked). Polish (colour, logo, PDF) happens downstream, never in the template.

A tier that can only be written by *asserting* rather than *citing* the corpus has surfaced an undone layer — say so; fix the corpus, then re-render.
