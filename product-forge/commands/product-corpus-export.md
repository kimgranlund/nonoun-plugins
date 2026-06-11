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
2. **Generate the viewer** — the common `<corpus>/site/` layout, in one command:
   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/bin/corpus-reader/build-sitemap.py" --init "<corpus>"
   ```
   This copies the reader into `<corpus>/site/` (machinery only — never a bundled example), builds its sitemap, and drops a root `index.html` redirect → `site/` if the corpus root has none. Re-run it after editing the corpus. Optional polish: a `<corpus>/reader.config.json` (`{"title": "…", "sections": {"00-discovery": "one-line description"}}`) sets the site title and the home cards' section descriptions.
3. **Serve + read.** `cd "<corpus>" && python3 -m http.server`, then open **http://localhost:8000/site/** . Re-run step 2 after editing the corpus.

**Verify:** the home cards list your sections (with descriptions if configured); a doc containing a raw `<script>` produces **no dialog** (DOMPurify strips it). `<corpus>/` is self-contained + portable — zip/share it, or host it on any static server (the `site/` viewer renders the sibling markdown).

**Live retrieval (optional).** The same `<corpus>/` is what the bundled **`product-corpus` MCP** reads: set the plugin's `corpus_dir` userConfig to this directory and the model gets read-only, task-level retrieval over it (`list_product_documents`, `outline_product_corpus`, `search_product`, `fetch_product_document`, `outline_product_document`) without re-loading the whole corpus into context. The MCP reads prose only and skips the `site/` viewer. Smoke-test it: `python3 "${CLAUDE_PLUGIN_ROOT}/bin/product-corpus-mcp.py" selftest`.
