---
description: Carve a skill library into coherent plugin boundaries — what bundles, what shares, what stays separate.
argument-hint: [the skills/library to carve]
---

You are in **carve** mode: decide plugin boundaries across a set of skills. Carve produces a **proposal**, not a packaged plugin — it never silently moves or deletes a skill, it recommends.

Library / skills: **$ARGUMENTS**

1. **Invoke the `plugin-build` skill** and run its `carve` sub-mode (`references/carve-method.md`).
2. **Map the REAL composition graph, not the catalog.** Fan the graph-mapping out via the **`carve-analyst`** subagent — it reads each skill's declared peers, routing pointers, **and** the hidden shared-type/`$ref` wiring that no peer array mentions (the coupling that breaks carves).
3. **Cluster by job-to-be-done**, then for **each** shared-infra item decide the legal resolution — co-locate / `dependencies` / same-marketplace symlink — **never** a `../` path that breaks at install (P4).
4. **Account for every node** — name orphans, bridges, and dead components; no silent drops.

Emit the layered boundary proposal (plugin table + dependency graph + orphan/dead callouts + per-plugin P1/P3/P4 self-check). Then `/plugin-author` builds each proposed plugin; `skills-refactor` executes any rename/merge the carve implies.
