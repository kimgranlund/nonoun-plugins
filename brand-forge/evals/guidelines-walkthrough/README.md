# Guidelines walkthrough — a worked example + an end-to-end behavioral proof

This eval drives the whole `/brand-elicit` machinery on a recorded, realistic brand and asserts the loop closes. It is both the **worked example** a reader learns the system from and the **CI-replayable proof** (no model agent) that the deterministic half holds — the catalog's behavioral-evidence discipline (cf. harness-forge's `first-slice-walkthrough`).

## The brand — Meridian

A fictional independent bookbinder/stationery brand whose idea is *"the pleasure of permanence in a disposable age."* `meridian.ledger.json` is what an interactive `/brand-elicit` session *produced*: one chosen design-move per domain, written as a coherent system.

What the recorded ledger deliberately exercises:

- **All six domains** — mark · voice · color · type · expression · governance, each a real 2×2 choice with axes, a design-move (rationale · effect · severity), a cited exemplar (by mechanism), and contributors.
- **A supersession** — `color-r1` was a first pass (a *loud* jewel-tone palette, confidence 0.6) that **`color-r2` supersedes** with the restrained ink-on-cream + one gold "tell." The assembler must drop the superseded loud choice and keep the live restrained one.
- **A coherence edge** — `color-r2 --constrains--> expression` (and `voice-r1 --supports--> expression`): the restrained palette + spare voice constrain the quiet-premium expression grammar.

It is a *clean, coherent* example (the "what good looks like" reference) — the choices cohere, and the one early misstep is resolved by supersession rather than left as a contradiction.

## What `replay.py` proves

Driven with no model agent — the ledger is the recorded output of the (model + designer) interaction; this replays the **deterministic** machinery the catalog gates:

1. `guidelines-ledger validate` — the ledger is well-formed.
2. `guidelines-ledger coverage` — **6/6 domains resolved** (proves supersession is honored: `color` resolves via the live `color-r2`).
3. `guidelines-ledger coherence` — surfaces the `constrains` edge.
4. `guidelines-ledger assemble --apply` — writes the six per-domain corpus docs in their layers; the **superseded loud color is dropped, the restrained choice kept**.
5. `corpus-provenance` — the assembled corpus is **clean** (every `sources:` resolves to the ledger; `contributors:` present): the build loop closes into the provenance gate.
6. `guidelines-ledger card` — projects a `*.brand.json` card (≥6 rules, the idea embedded) for the optional brand-decomposer grading seam.

Run it: `python3 replay.py` (exit 0 = the loop closes). CI runs it on every push.
