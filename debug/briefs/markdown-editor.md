# Markdown Editor — a live split-pane writing tool

Build a browser Markdown editor with a live preview, local persistence, and export. No build step (vanilla JS +
a tiny dependency-free Markdown parser you write, or a tiny Vite app).

## What a good version does

- A **split pane**: Markdown source on the left, **live-rendered HTML** preview on the right (debounced), with
  synchronized scrolling.
- A **dependency-free Markdown renderer** covering the common subset: headings, bold/italic/code, links, lists
  (ordered/unordered, nested), blockquotes, fenced code blocks, horizontal rules — and it **escapes HTML so
  user input can't inject script** (no XSS).
- **Local persistence** (localStorage autosave), a document list / new-doc, a word + character count, and
  **export** (download `.md`, copy rendered HTML).
- Clean keyboard ergonomics (tab inserts, a bold/italic shortcut) and a light/dark toggle.

## Non-goals

- No real-time collaboration, no cloud sync in the first cut.
- No full CommonMark/GFM completeness (tables/footnotes optional); the common subset is enough.

## Acceptance signal

Typing Markdown renders it live and safely (a `<script>` in the source shows as text, never executes), a
document autosaves + survives a reload, and export downloads the source. **Build the Markdown parser + the
(de)serializer as pure ES modules** (`renderMarkdown(src) → htmlString` with escaping, `saveDoc`/`loadDoc`) a
`verify.mjs` drives headlessly to assert each markup rule, the XSS escaping, and the persistence round-trip —
the DOM/editor wiring stays in the shell.
