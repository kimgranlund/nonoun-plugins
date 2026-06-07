---
description: Export this product's deliverables as a navigable corpus site (clean markdown + a site/ viewer).
argument-hint: "[corpus dir — default ./product-corpus]"
---

You are entering **Corpus Export mode**: lay out this product engagement's deliverables as a Markdown **corpus** (a clean, shareable folder of `.md`), then tuck a self-contained **`site/`** viewer beside it so it also reads as a navigable site (sticky nav, per-page ToC, GFM tables, highlighted code, mermaid — untrusted markdown sanitized via DOMPurify).

Target corpus dir from the operator (default `./product-corpus`): **$ARGUMENTS**

**Precondition.** There must be product work products to export. If the engagement hasn't produced any yet, say so and stop — run `/product-discover` or `/product-strategy` first. Don't invent deliverables to fill sections.

1. **Write the corpus.** Author the real deliverables as Markdown into `<corpus>/`, grouped into ordered top-level sections (a leading `NN-` orders a section and is stripped from the display name; include only what exists):
   - `00-discovery/` — user research, JTBD, personas, opportunity assessment
   - `01-strategy/` — vision / north-star, positioning, product strategy
   - `02-definition/` — PRDs, specs, requirements, scope
   - `03-experience/` — information architecture, flows, UX patterns, wireframes
   - `04-operations/` — service design, metrics, governance, rollout
   Give each page a frontmatter `title:` (else its first `# H1` is used). Add `<corpus>/README.md` whose H1 is the product name — it becomes the site title + home hero. **Keep the corpus root clean markdown** — browsable/diffable on its own, with no app files mixed in.
2. **Add the viewer** (machinery only — never a bundled example corpus):
   ```sh
   mkdir -p "<corpus>/site"
   cp -R "${CLAUDE_PLUGIN_ROOT}/bin/corpus-reader/index.html" \
         "${CLAUDE_PLUGIN_ROOT}/bin/corpus-reader/lib" \
         "${CLAUDE_PLUGIN_ROOT}/bin/corpus-reader/build-sitemap.py" "<corpus>/site/"
   rm -f "<corpus>/site/lib/sitemap.json"   # regenerated next
   ```
3. **Build the index.** `cd "<corpus>/site" && python3 build-sitemap.py ..` — scans the parent corpus and writes `site/lib/sitemap.json` (paths resolve out to the sibling markdown).
4. **Serve + read.** `cd "<corpus>" && python3 -m http.server`, then open **http://localhost:8000/site/** . Re-run step 3 after editing the corpus.

**Verify:** the home tiles list your sections; a doc containing a raw `<script>` shows as text (DOMPurify sanitizes it). `<corpus>/` is self-contained + portable — zip/share it, or host it on any static server (the `site/` viewer renders the sibling markdown).
