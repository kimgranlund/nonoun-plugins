# corpus-reader — changelog

The reader's own evolution. It is **gated against staleness**: `sync-corpus-reader.py --check`
(a CI gate) hashes the reader's code and fails if it differs from the `source-fingerprint`
marker below — so any code change trips CI until it is logged. Add entries with
`python3 plugins-factory/bin/sync-corpus-reader.py --changelog "<summary>"` (it prepends a
dated entry and refreshes the marker); don't hand-edit the marker. Dates are `YYYY-MM-DD`.

<!-- source-fingerprint: b44a912a0cbc2438575727340a8451eb55a958c78c1808ff9653aee4256dbfd2 -->

## 2026-06-10 — Baked single-file mode: build-sitemap.py --bake emits one self-contained reader.html that works on file:// (inline module + inlined sitemap/markdown/CSS+theme; CDN pins + SRI lifted verbatim from index.html); cr-shell/cr-ui-page read inlined window.CORPUS/CORPUS_FILES when present, fetch otherwise — served layouts unchanged (refactor proven byte-identical)

## 2026-06-10 — Per-corpus theme hook: reader.config.json "theme" names a stylesheet inside the corpus; build-sitemap emits it (containment-checked) and the shell injects it after corpus-reader.css — token overrides only by contract; demo-corpus ships a worked theme.css

## 2026-06-10 — Wordmark drops a leading separator from the subtitle; sidebar search also matches page summaries; provenance stats count prose only (not code spans/fences); --init drops a root index.html redirect → site/ when the corpus root has none

## 2026-06-10 — Committed demo-corpus/ — a tiny synthetic example a fresh clone renders out of the box; doubles as the CI smoke fixture (build + --init each push); CI also gains a JS parse gate over the components

## 2026-06-08 — Home section cards gain optional one-line descriptions + a title override via <corpus>/reader.config.json (graceful — no config needed)

## 2026-06-08 — Adopt the new reader's patterns + layouts (web components kept): sidebar search + layer-label nav, mobile drawer, home hero + section cards + maturity/provenance stats bar + minibars, doc kicker + badges, inline provenance tags + path.md xrefs

## 2026-06-08 — Add README + a staleness-gated CHANGELOG; sidebar wordmark now derives from the corpus title (no hardcoded brand)

- New `README.md` (rewritten for the sidebar-nav layout) and this `CHANGELOG.md`. `sync-corpus-reader.py --check` now also fails when the reader's code changed without a new CHANGELOG entry — it records + verifies a `source-fingerprint` — and `--changelog "…"` is the maintained way to log one. Also fixed `cr-ui-header` to take the sidebar wordmark from the corpus title instead of a hardcoded "BZZR".

## 2026-06-08 — sidebar-nav layout + system-sans hero

- Replaced the top nav bar (a `[ name | menu ]` dropdown over a `toc | content` grid) with a **persistent left sidebar** — the corpus wordmark over an always-visible sections → pages nav — beside a main column (a sticky breadcrumb topbar over `content | toc`). The per-page ToC stays as the right rail; the home route remains the section-tile dashboard. The home hero is set in system-sans.

## 2026-06-07 — one common `<corpus>/site/` convention

- `build-sitemap.py --init <corpus>` scaffolds the standard `site/` viewer (machinery only, never the example) and builds its sitemap in one command — the single layout every plugin's `*-corpus-export` command uses.

## 2026-06-06 — export to a clean corpus root + `site/` viewer

- `build-sitemap.py ..` (run from a `site/` inside the corpus) emits `../<section>/…` paths and excludes the viewer's own dir, so an exported corpus keeps its root as clean, browsable Markdown with the app tucked into `site/`. The export copies the viewer machinery only — never the bundled example.

## 2026-06-06 — the home uses the width; graceful `file://`

- The section-tile home spans a wider track (90rem vs the 51rem prose measure) with `align-items: start` — more columns on wide viewports, no stretched tiles.
- Opening `index.html` from `file://` now shows a "serve over HTTP" message (an inline classic script that runs even when the modules can't load) instead of a blank page + CORS errors.

## 2026-06-06 — security hardening (untrusted markdown) + vendoring

- Corpus markdown is treated as untrusted: **DOMPurify** sanitizes the rendered HTML (marked doesn't), mermaid runs `securityLevel: "strict"`, and the CDN libraries are pinned with **Subresource-Integrity** (sha384); marked/DOMPurify failing their integrity check degrades prose to escaped text.
- The reader is vendored into brand-forge + product-forge (cross-plugin symlinks don't survive plugin install). `sync-corpus-reader.py` keeps the copies byte-identical and CI-gates both drift and the XSS wiring.

## 2026-06-05 — initial buildless reader

- A static reader for a folder of Markdown, as a small `<cr-*>` custom-element tree (a `UIElement` base with signal-style reactive properties) over a stdlib `build-sitemap.py` generator: hash router, markdown + GFM + highlighted code + mermaid via CDN, a per-page ToC, a section-tile home, light/dark by OS preference. No build step.
