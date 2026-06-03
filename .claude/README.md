# Project `.claude/`

Project-scoped Claude Code config for **working in this repo** — authoring and red-teaming the plugins that live under `*/` (currently `brand-forge/`). These components load for anyone running Claude Code from this repo; they are **not** shipped to plugin users.

> **Don't confuse these with a plugin's own components.** `brand-forge/{skills,agents,commands,hooks}/` are *distributed* — they ship when someone installs the plugin. The identically-named folders under `.claude/` are *repo-local dev tools* that never leave this repo. Same file format, different audience.

## The harness lives here: `skills/plugins-factory/`

The repo's plugin-lifecycle harness, **`plugins-factory`**, lives at `skills/plugins-factory/` — a full plugin (it keeps its own `.claude-plugin/plugin.json`) that auto-loads as a **project-scope `@skills-dir` plugin** whenever you work here, in-place (no install, no marketplace entry). It is the main inhabitant of this directory and the tool used to build and red-team the catalog plugins. Because it's a real plugin, it's also shareable. The loose `skills/` · `agents/` · `commands/` slots below remain for any *other* ad-hoc repo tooling.

## What goes where

| Path | One per | Becomes | Frontmatter | Shape to copy |
|---|---|---|---|---|
| `skills/<name>/SKILL.md` | skill (a folder) | a loadable skill | `name`, `description` (+ trigger phrases) | `brand-forge/skills/brand-methodology/SKILL.md` |
| `agents/<name>.md` | subagent | a dispatchable agent | `name`, `description` | `brand-forge/agents/critic-john-h.md` |
| `commands/<name>.md` | command | `/<name>` | `description`, `argument-hint` | `brand-forge/commands/brand-orient.md` |

Skills may carry supporting docs in `<name>/references/`, loaded on demand — keep `SKILL.md` a table of contents (the pattern the brand-forge skills follow).

## Settings

- `settings.json` — shared project settings (checked in). Add it when there's something to share.
- `settings.local.json` — your personal settings/permissions (git-ignored).
