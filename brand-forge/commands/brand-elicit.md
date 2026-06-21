---
description: Brand Guidelines — build a guidelines section by guided 2×2 choice, accumulating into the corpus.
argument-hint: "[domain — mark|voice|color|type|expression|governance; default: resume the frontier]"
---

You are entering **Brand Guidelines mode**: build a high-quality brand-guidelines section by **guided choice** — present a 2×2 of concrete options for a brand domain, let the designer pick a quadrant (A/B/C/D) + comments, and accumulate the choices into a provenance-traced corpus. Posture is _maker_: you propose grounded options; the **designer supplies the taste**; you never grade your own output. This MAKES guidelines — scoring is `/brand-score` (`brand-evaluate`), not here.

Domain to work (or resume the frontier if empty): **$ARGUMENTS**

1. **Load the loop.** Invoke the **`brand-guidelines`** skill — the six-domain walk, the seven axes + the default 2×2 pair per domain, the design-move card, the pick model, drill-down, and coherence (`skills/brand-guidelines/references/the-loop.md`).
2. **Read the ground truth first.** Invoke the **`brand-corpus`** skill (+ the corpus MCP if `corpus_dir` is set) to read `01-foundation` and the existing choice-ledger (`00-sources/guidelines-elicitation.json`) under the default corpus root **`./brand-corpus`** (the same default `/brand-corpus-export` and `/brand-stack` use; pass a path to override) — every option must trace to the decided foundation; resume at the uncovered frontier.
3. **Run one 2×2 round.** First **`bin/guidelines-ledger coherence --domain <d>`** to surface prior commitments + contradictions; then frame the domain's two axes → generate four design-move cards grounded in the foundation + prior commitments + a cited exemplar (name the brand + mechanism, never copy assets) + the quality bar → present the 2×2 + cards → capture the pick + comments as a typed choice → drill down or advance.
4. **Append + validate the ledger.** Write the choice and run **`bin/guidelines-ledger validate <ledger>`** (well-formed by construction) after every write; append-only, `supersedes` for revisions.

5. **Coverage + assembly.** Check progress with **`bin/guidelines-ledger coverage`** (per-domain frontier). When domains are covered, **`bin/guidelines-ledger assemble [--out <corpus>] [--apply]`** (defaults to `./brand-corpus`) compiles the live ledger into corpus docs in their layers (`mark`→03, `color`/`type`/`expression`→04, `voice`→05, `governance`→07) — dry-run first; matches the corpus's flat/folder convention; refuses a mixed corpus. **Non-destructive:** a hand-authored layer doc is never clobbered (the elicited version goes to a flagged `.elicited.md` sibling; re-assembly of our own output is idempotent; `--force` to replace). Each rule is typed `must/should/may`, `sources:`/`contributors:`-stamped, so `corpus-provenance` gates the trace and `/brand-score` (`brand-evaluate`) scores it.

6. **Grade it (optional seam).** `bin/guidelines-ledger card <ledger> --idea "<from 01-foundation>" -o card.json` projects a `*.brand.json` card that `design-skills:brand-decomposer` GRADES + operability-checks (`brand-spec-check.py lint card.json`) when installed — the make→grade handoff.

A card you can only write by *asserting* rather than tracing it to `01-foundation` has surfaced an undone foundation: say so, and fix the foundation (`/brand-build`) first.
