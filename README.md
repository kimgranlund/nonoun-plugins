# SDLC Lite agents and Progressive Context

Two independently installable plugins, with Codex and Claude Code manifests and marketplace catalogs.

| Plugin | Purpose | Codex invocation |
|---|---|---|
| Progressive Context | Durable capability contracts, selective context loading, evidence and reuse qualification | `$progressive-context` |
| SDLC Lite | Tickets, plans, execution, verification and work closure | `$sdlc-lite` |

Progressive Context works directly in either host. SDLC Lite supports native Codex execution and Claude execution, selected with `SDLC_BACKEND=codex|claude`. Its project setup installs predefined Codex subagents. See [compatibility and validation](docs/references/plugin-compatibility.md).

## Install

Codex: add this repository as a marketplace with `codex plugin marketplace add /absolute/path/to/sdlc-lite`, then select the plugins in the app. The catalog is `.agents/plugins/marketplace.json`.

Claude Code: `/plugin marketplace add /absolute/path/to/sdlc-lite`, then install `progressive-context@sdlc-lite` and/or `sdlc-lite@sdlc-lite`. Its catalog is `.claude-plugin/marketplace.json`.

Start a fresh chat after installation. No plugin installs itself or modifies your user configuration.

## Development

- Run `bash plugins/sdlc-lite/scripts/check.sh` for the SDLC Lite regression suite, or `check.sh --fast` for its quick tier.
- Run `python3 scripts/check-packaging.py` for both catalogs, manifest parity, skill discovery and local links.
- Read [specifications](docs/README.md) for design scope and deferred runtime work.

Native setup, model mappings, and examples: [Codex role execution](docs/references/codex-role-execution.md).
