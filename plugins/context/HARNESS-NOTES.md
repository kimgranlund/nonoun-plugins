# Host compatibility

Six skills and their references load in Codex and Claude Code. `system-atlas` builds an offline HTML page on either host and publishes it with Claude's Artifact tool, which Codex lacks. Both manifests share identity and version. No hooks, MCP services, native agents, model selection, or CLI backend are required.

Invoke `$progressive-context` in Codex or `/context:progressive-context` in Claude Code; the other skills follow the same pattern (`$system-atlas`, `/context:system-atlas`). The skill uses the host's available file, shell, and question tools. It does not assume automatic AGENTS.md loading, native delegation, or host argument interpolation.

The shipped feature is a filesystem-oriented authoring workflow. Browser record storage, automated lifecycle calculation, and A2UI runtime integration remain design guidance, not implemented runtime components. Validation is recorded in [the repository compatibility report](../../docs/references/plugin-compatibility.md).
