---
title: Reader architecture
status: draft
date: 2026-06-10
type: reference
---

# Reader architecture

The reader is a small custom-element tree [KNOWN]: a shell owns the hash route and pushes `sitemap` + `route` down to the sidebar and the main column. Rendering happens client-side [INFERRED] to stay buildless — marked parses, DOMPurify sanitizes, highlight.js and mermaid progressively enhance.

```mermaid
graph TD
  shell[cr-shell] --> header[cr-ui-header]
  shell --> body[cr-ui-body]
  body --> page[cr-ui-page]
  body --> toc[cr-ui-toc]
```

```js
// fenced code, syntax-highlighted
const route = location.hash.replace(/^#\/?/, "");
```
