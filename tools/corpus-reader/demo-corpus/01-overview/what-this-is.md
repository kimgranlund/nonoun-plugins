---
title: What this is
status: active
version: 1.0
date: 2026-06-10
type: overview
---

# What this is

This corpus exists so the reader has something [KNOWN] to render on a fresh clone — synthetic content, no licensed assets, each page exercising a feature. The rendering pipeline is described in `architecture.md`, and the sanitizer probe lives in [the security model](../02-architecture/security-model.md).

| Feature | Exercised by |
| --- | --- |
| Status badges | every page's frontmatter `status` |
| Provenance tags + stats bar | inline `[KNOWN]` / `[INFERRED]` / `[OPEN]` / `[SEEDED]` markers |
| Cross-reference links | the `architecture.md` code-span above |
| Section descriptions | `reader.config.json` at the corpus root |
| Diagram + code | architecture.md |
| Sanitizer probe | security-model.md |
