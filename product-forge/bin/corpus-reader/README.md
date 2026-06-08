# corpus-reader

A tiny static documentation reader for a folder of Markdown — the kind some plugins generate as a "corpus." Point it at a corpus, generate a sitemap, serve the folder, and read it as a navigable site: a sticky nav, a per-page table of contents, and a tile-grid index. Markdown, GFM tables, fenced code (syntax-highlighted), and `mermaid` diagrams all render client-side. No build step.

## Use it

1. **Generate the sitemap** for your corpus (a sibling folder of `.md` files):

   ```sh
   python3 build-sitemap.py            # auto-detects a single corpus folder
   python3 build-sitemap.py my-corpus  # or name it explicitly
   ```

   This writes `lib/sitemap.json` — sections grouped by top-level folder, with a title + one-line summary per page.

2. **Serve the folder** (the reader uses `fetch()`, which browsers block on `file://`):

   ```sh
   python3 -m http.server
   ```

   Open http://localhost:8000/ . Re-run step 1 whenever the corpus changes.

## Layout

| File | Role |
| --- | --- |
| `index.html` | the shell — loads the reader + the rendering libraries |
| `lib/corpus-reader.css` | styles (light / dark by OS preference) |
| `lib/corpus-reader.js` | hash router, markdown render, ToC + scrollspy, the tile home |
| `lib/sitemap.json` | generated — the index the reader loads |
| `build-sitemap.py` | the generator (Python 3.8+, stdlib only) |

The page is a sticky `nav` (`[ name | menu ]`) over a `toc | content` grid. The home route (`#/`) is a grid of section tiles, each listing its pages; a page route (`#/<path-to.md>`) renders that file with its own table of contents.

## Pointing at any corpus

Put the corpus folder beside `index.html` and run `build-sitemap.py <folder>`. Page titles come from frontmatter `title:`, else the first `# H1`, else the filename; sections are the top-level subfolders (a leading `NN-` orders them and is stripped from the display name); the corpus title is the root `README` heading. Cross-document `.md` links and relative images are rewritten to work inside the router.

**Viewer in a `site/` subfolder (the common layout).** To keep the corpus root as clean, shareable markdown with the app tucked away, run `python3 build-sitemap.py --init <corpus-root>` — it copies this reader into `<corpus-root>/site/` (machinery only, never an example) and builds the sitemap (`../<section>/…` paths, the `site/` dir excluded from the scan). Then serve the corpus root and open `/site/`. This single convention is what every plugin's `*-corpus-export` command uses, so generated corpus sites share an identical layout. (The lower-level `build-sitemap.py ..`, run from inside an existing `site/`, does just the sitemap step.)

Rendering uses marked + **DOMPurify** + highlight.js + mermaid, pinned via CDN in `index.html` with Subresource-Integrity (SRI) hashes. Corpus markdown is treated as **untrusted**: marked doesn't sanitize, so DOMPurify scrubs the rendered HTML (and mermaid runs `securityLevel: "strict"`). marked + DOMPurify are required — if either fails its integrity check, prose degrades to escaped text; highlight + mermaid are progressive enhancement. Swap the CDN tags for vendored copies in `lib/` if you need a fully offline reader.

## Note

The bundled `brand-corpus/` is only an example to develop against — it is gitignored (it carries licensed fonts and is not part of this repo). Drop in your own corpus the same way.
