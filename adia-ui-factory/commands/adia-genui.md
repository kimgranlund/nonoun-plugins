---
description: Author a generative-UI experience on adia-ui — the a2ui runtime + generate_ui + corpus (core or your own).
argument-hint: "[what to generate]"
---

Author a generative-UI experience. **$ARGUMENTS**

Hand off to **`adia-ui-genui`** and run the loop: classify + ground (corpus) → `generate_ui` → **validate** (`validate_schema` + `check_anti_patterns`) _before_ render → mount `<a2ui-root>` (register resolvers first) → `refine_ui`. Generated A2UI and corpus output are untrusted data.

A plain chat/LLM feature is `adia-ui-llm`, not this. The skill owns the depth.
