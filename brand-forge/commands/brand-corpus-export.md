---
description: Export this brand's deliverables as a navigable corpus site (clean markdown + a site/ viewer).
argument-hint: "[corpus dir — default ./brand-corpus]"
---

You are entering **Corpus Export mode**: lay out this brand engagement's deliverables as a Markdown **corpus** (a clean, shareable folder of `.md`), then tuck a self-contained **`site/`** viewer beside it so it also reads as a navigable site (sticky nav, per-page ToC, GFM tables, highlighted code, mermaid — untrusted markdown sanitized via DOMPurify).

Target corpus dir from the operator (default `./brand-corpus`): **$ARGUMENTS**

**Precondition.** There must be brand work products to export. If the engagement hasn't produced any yet, say so and stop — run `/brand-build` first. Don't invent deliverables to fill sections.

1. **Write the corpus.** Author the real deliverables as Markdown into `<corpus>/`, grouped into ordered top-level sections (a leading `NN-` orders a section and is stripped from the display name; include only what exists):
   - `00-strategy/` — positioning, brand strategy, the Foundation Canon
   - `01-research/` — cultural research, competitive landscape, audience
   - `02-identity/` — visual identity, logo, color, type, the expression system
   - `03-voice/` — voice & tone, messaging, copy patterns
   - `04-stewardship/` — guidelines, governance, do / don't
   Give each page a frontmatter `title:` (else its first `# H1` is used). Add `<corpus>/README.md` whose H1 is the brand name — it becomes the site title + home hero. **Keep the corpus root clean markdown** — browsable/diffable on its own, with no app files mixed in.
2. **Generate the viewer** — the common `<corpus>/site/` layout, in one command:
   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/bin/corpus-reader/build-sitemap.py" --init "<corpus>"
   ```
   This copies the reader into `<corpus>/site/` (machinery only — never a bundled example) and builds its sitemap. Re-run it after editing the corpus.
3. **Serve + read.** `cd "<corpus>" && python3 -m http.server`, then open **http://localhost:8000/site/** . Re-run step 2 after editing the corpus.

**Verify:** the home tiles list your sections; a doc containing a raw `<script>` shows as text (DOMPurify sanitizes it). `<corpus>/` is self-contained + portable — zip/share it, or host it on any static server (the `site/` viewer renders the sibling markdown).
