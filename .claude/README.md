# Project `.claude/`

Project-scoped Claude Code config for **working in this repo** — building and red-teaming the catalog plugins (`brand-forge/`, `plugins-factory/`). Nothing here ships to plugin users; it's repo-local.

## `settings.json` — auto-enables the lifecycle tool

This repo's `settings.json` declares the `nonoun-plugins` marketplace (`extraKnownMarketplaces`) and enables **`plugins-factory`** by default (`enabledPlugins`), so the plugin-lifecycle tool loads whenever you — or a collaborator who trusts the project — work here. That's why its `/plugin-*` commands and critic council are available against the catalog plugins without a manual install. (Working in the repo installs the **published** version from GitHub; for live local edits to the tool itself, test with `claude --plugin-dir plugins-factory` or bump + `/plugin marketplace update`.)

- `settings.json` — shared project settings (checked in → every collaborator). Holds the `extraKnownMarketplaces` + `enabledPlugins` above.
- `settings.local.json` — personal settings/permissions (git-ignored).

## `skills/` · `agents/` · `commands/` — ad-hoc repo tooling

Empty slots for any _repo-local_ dev tools you want to add — distinct from a distributed plugin's own components (those live inside `brand-forge/` / `plugins-factory/` and ship on install). One file/folder per component:

| Path | One per | Becomes | Frontmatter | Shape to copy |
| --- | --- | --- | --- | --- |
| `skills/<name>/SKILL.md` | skill (a folder) | a loadable skill | `name`, `description` (+ triggers) | `brand-forge/skills/brand-methodology/SKILL.md` |
| `agents/<name>.md` | subagent | a dispatchable agent | `name`, `description` | `brand-forge/agents/critic-john-h.md` |
| `commands/<name>.md` | command | `/<name>` | `description`, `argument-hint` | `brand-forge/commands/brand-orient.md` |
