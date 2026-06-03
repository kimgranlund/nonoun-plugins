---
name: adia-ui-factory
description: >
  Cold-start orchestrator for authoring apps on the adia-ui (@adia-ai) framework — classify the rendering mode (SPA vs SSR-framework) and the task (scaffold / compose / wire / verify), then route to the right skill. Use first when building or extending an adia-ui app.
---

# adia-ui-factory

> **Stub — scaffolded in phase (a); content authored in phase (b).**

This skill will own:

- the SPA-vs-SSR decision tree (rendering-model)
- task classification + routing to compose/spa/ssr/llm/verify
- when to reach for the a2ui MCP vs hand-authoring

Source (to vendor/synthesize): the `app-authoring-best-practices` methodology (SPA) and `adia-ui-kit/rendering-model` (SSR) from the framework, plus the a2ui MCP tool surface.
