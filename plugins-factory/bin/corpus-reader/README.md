# corpus-reader

A tiny **buildless** static reader for a folder of Markdown — the kind some plugins generate as a "corpus." Point it at a corpus, build a sitemap, serve the folder, and read it as a navigable site: a persistent sidebar nav, a per-page table of contents, a section-tile home, GFM tables, syntax-highlighted code, and `mermaid` diagrams — all rendered client-side. No build step, stdlib-only generator.

## Use it

**The common way — a `site/` viewer beside your corpus** (one command):

```sh
python3 build-sitemap.py --init <corpus-root>   # scaffold <corpus-root>/site/ + build the sitemap
cd <corpus-root> && python3 -m http.server      # then open http://localhost:8000/site/
```

`--init` copies this reader (machinery only — never the bundled example) into `<corpus-root>/site/` and builds its sitemap, so the corpus root stays clean, shareable Markdown with the app tucked into `site/`. This is the single layout every plugin's `*-corpus-export` command produces. Re-run `--init` (or `build-sitemap.py ..` from inside `site/`) after editing the corpus.

**Standalone — the reader and corpus together:**

```sh
python3 build-sitemap.py            # auto-detects a single sibling corpus folder
python3 build-sitemap.py my-corpus  # …or name it
python3 -m http.server              # then open http://localhost:8000/
```

The reader uses ES modules + `fetch()`, so it must be **served over HTTP** — opening `index.html` from `file://` shows a "serve over HTTP" notice instead of rendering.

## Layout

A sticky left **sidebar** | a **main column**:

- **Sidebar** (`<cr-ui-header>`) — the corpus wordmark (derived from the sitemap title; no hardcoded brand) over a persistent **sections → pages** nav (`<cr-ui-nav>`, always visible, active page highlighted).
- **Main** (`<cr-ui-body>`) — a sticky breadcrumb topbar over the `content | toc` grid: `<cr-ui-page>` renders the route, `<cr-ui-toc>` is the right-rail per-page table of contents. The home route (`#/`) is a grid of section tiles; a page route (`#/<path-to.md>`) renders that file.

## Architecture

The whole reader is a small custom-element tree — `<cr-shell>` loads `lib/sitemap.json`, owns the `#/<path>` hash route, and pushes `sitemap` + `route` down to the header and body.

| File | Role |
| --- | --- |
| `index.html` | the page shell — loads the reader + the render libraries (pinned + SRI) + a `file://` guard |
| `lib/corpus-reader.js` | entry module — imports and registers the `<cr-*>` components |
| `lib/components/` | the tree: `base.js` (a `UIElement` base with signal-style reactive properties) · `cr-shell` · `cr-ui-header` (sidebar) · `cr-ui-nav` · `cr-ui-body` (main) · `cr-ui-page` · `cr-ui-toc` · `cr-ui-diagram-viewer` · `util.js` |
| `lib/corpus-reader.css` | one token layer (OKLCH hue + chroma axes → semantic tokens), light/dark by OS preference |
| `lib/sitemap.json` | generated — the index the reader loads |
| `build-sitemap.py` | the generator + `--init` scaffolder (Python 3.8+, stdlib only) |

## Pointing at any corpus

Page titles come from frontmatter `title:`, else the first `# H1`, else the filename; sections are the top-level subfolders (a leading `NN-` orders them and is stripped from the display name); the corpus title (and the sidebar wordmark) come from the root `README` heading. Cross-document `.md` links and relative images are rewritten to work inside the router, inline provenance tags (`[KNOWN]/[INFERRED]/[OPEN]/[SEEDED]`) are styled, and a frontmatter `status` feeds the home maturity bar.

An optional `<corpus>/reader.config.json` adds polish without touching the reader:

```json
{ "title": "…", "sections": { "01-foundation": "one-line description shown on the home card" } }
```

## Security — untrusted markdown

Rendering uses marked + **DOMPurify** + highlight.js + mermaid, pinned via CDN in `index.html` with **Subresource-Integrity** (SRI) hashes. Corpus markdown is treated as **untrusted**: marked doesn't sanitize, so DOMPurify scrubs the rendered HTML, and mermaid runs `securityLevel: "strict"`. marked + DOMPurify are required — if either fails its integrity check, prose degrades to escaped text; highlight + mermaid are progressive enhancement. (Swap the CDN tags for vendored copies in `lib/` for a fully offline reader.) The XSS wiring is CI-guarded — see _Maintenance_.

## Maintenance

This reader is the single source of truth at `plugins-factory/bin/corpus-reader/`; brand-forge and product-forge ship **vendored copies** (cross-plugin symlinks don't survive plugin install). `plugins-factory/bin/sync-corpus-reader.py` keeps the copies byte-identical and, as a CI gate (`--check`), also asserts the DOMPurify/SRI wiring is intact **and that the [CHANGELOG](CHANGELOG.md) hasn't gone stale** (a source fingerprint must match the latest `CHANGELOG.md` entry). After any code change, log it:

```sh
python3 plugins-factory/bin/sync-corpus-reader.py --changelog "<what changed>"   # dated entry + refresh
python3 plugins-factory/bin/sync-corpus-reader.py                                # re-sync the copies
```

## Note

The committed **`demo-corpus/`** is a tiny synthetic example — a fresh clone renders it out of the box (`python3 build-sitemap.py demo-corpus`), it exercises the reader's features (statuses, provenance tags, xrefs, mermaid, the sanitizer probe), and CI smoke-builds it on every push. A larger local-only corpus may also sit beside the reader for development (e.g. a gitignored `brand-corpus/` — never committed; it can carry licensed assets). With more than one sibling corpus present, auto-detect refuses to guess — name the corpus explicitly.
