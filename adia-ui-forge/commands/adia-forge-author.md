---
description: Author or modify an adia-ui primitive, composite shell, trait, or token (web-components / web-modules).
argument-hint: "[component or change]"
---

Author framework UI. **$ARGUMENTS**

**Name the design principles before you converge.** Before authoring, confirm the **framework philosophy** this change serves (light-DOM composability, token-driven styling, contract-first authoring, no lifecycle leaks) is **at least lightly named** — one sentence of direction is enough, and it will evolve; this plugin has no standalone principles doc yet, so name them even provisionally. This is a **soft gate**: an undeclared direction is cleared by _naming_ a provisional one, not by stopping.

Invoke **`adia-ui-authoring`** and run its authoring cycle: pre-build audit → API / YAML contract → light-DOM + `@scope` token CSS → lifecycle → demo. The skill owns the discipline; don't restate it here.
