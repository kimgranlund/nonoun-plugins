---
description: Export this brand's deliverables as a navigable corpus site and read it in the corpus-reader.
argument-hint: "[target dir — default ./brand-corpus-site]"
---

You are entering **Corpus Export mode**: lay out this brand engagement's deliverables as a Markdown **corpus**, then build + serve it with the bundled **corpus-reader** so the operator reads the brand as a navigable site (sticky nav, per-page ToC, GFM tables, highlighted code, mermaid — untrusted markdown sanitized via DOMPurify).

Target dir from the operator (default `./brand-corpus-site`): **$ARGUMENTS**

**Precondition.** There must be brand work products to export (strategy, identity, voice, …). If the engagement hasn't produced any yet, say so and stop — run `/brand-build` first. Don't invent deliverables to fill sections.

1. **Stage the reader** (self-contained + portable):
   `mkdir -p "<target>" && cp -R "${CLAUDE_PLUGIN_ROOT}/bin/corpus-reader/." "<target>/"`
2. **Write the corpus.** Author the brand's real deliverables as Markdown into `<target>/corpus/`, grouped into ordered top-level sections (the reader groups by top-level folder; a leading `NN-` orders it and is stripped from the display name). Sensible default — include only what exists:
   - `00-strategy/` — positioning, brand strategy, the Foundation Canon
   - `01-research/` — cultural research, competitive landscape, audience
   - `02-identity/` — visual identity, logo, color, type, the expression system
   - `03-voice/` — voice & tone, messaging, copy patterns
   - `04-stewardship/` — guidelines, governance, do / don't
   Give each page a frontmatter `title:` (else its first `# H1` is used). Add `<target>/corpus/README.md` whose H1 is the brand name — it becomes the site title + home hero.
3. **Build the index.** `cd "<target>" && python3 build-sitemap.py corpus` — writes `lib/sitemap.json`.
4. **Serve + read.** `python3 -m http.server` from `<target>`, then open http://localhost:8000/ . Re-run step 3 whenever the corpus changes.

**Verify:** the home tiles list the sections you wrote, each page renders, and a doc containing a raw `<script>` shows as text (DOMPurify sanitizes it). The `<target>` folder is self-contained — zip/share it or host it on any static server.
