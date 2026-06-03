---
name: adia-ui-compose
description: >
  Construct adia-ui UI (mode-independent) — audit the component catalog via the a2ui MCP, compose screens from light-DOM primitives + shells, author project-specific light-DOM components (render/style split, token-only CSS, size-agnostic), and apply theming/tokens. Shared across SPA and SSR.
---

# adia-ui-compose

> **Stub — scaffolded in phase (a); content authored in phase (b).**

This skill will own:

- catalog literacy via the a2ui MCP (get_component_map / lookup_component / search_chunks / search_patterns)
- light-DOM component authoring: the self-booting container, render/style split, @scope token-only CSS, size-agnostic chrome
- theming + tokens + registers (verse/prose)
- UI generation via the MCP's generate_ui

Source (to vendor/synthesize): the `app-authoring-best-practices` methodology (SPA) and `adia-ui-kit/rendering-model` (SSR) from the framework, plus the a2ui MCP tool surface.
