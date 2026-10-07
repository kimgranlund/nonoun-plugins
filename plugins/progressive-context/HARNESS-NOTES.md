# Host compatibility

One skill and its references serve Codex and Claude Code. Both manifests share identity and version. No hooks, MCP services, native agents, model selection, or CLI backend are required.

Invoke `$progressive-context` in Codex or `/progressive-context:progressive-context` in Claude Code. The skill uses the host's available file, shell, and question tools. It does not assume automatic AGENTS.md loading, native delegation, or host argument interpolation.

The shipped feature is a filesystem-oriented authoring workflow. Browser record storage, automated lifecycle calculation, and A2UI runtime integration remain design guidance, not implemented runtime components. Validation is recorded in [the repository compatibility report](../../docs/references/plugin-compatibility.md).
