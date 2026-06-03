---
name: adia-ui-llm
description: >
  Wire LLM-powered features into an adia-ui app — the @adia-ai/llm client (Anthropic/OpenAI/Gemini), streaming chat, the chat-shell, the browser proxy — and generate UI via the a2ui MCP. Use for chat/AI features and A2UI generation.
---

# adia-ui-llm

> **Stub — scaffolded in phase (a); content authored in phase (c).**

This skill will own:

- the @adia-ai/llm client: chat() / streamChat(), provider adapters, the browser proxy
- wiring the chat-shell + streaming UI
- A2UI generation via the a2ui MCP (generate_ui) and validation (validate_schema / check_anti_patterns)

Source (to vendor/synthesize): the `app-authoring-best-practices` methodology (SPA) and `adia-ui-kit/rendering-model` (SSR) from the framework, plus the a2ui MCP tool surface.
