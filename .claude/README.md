# Project `.claude/`

Project-scoped Claude Code config for **working in this repo** — authoring and red-teaming the plugins that live under `*/` (currently `brand-studio/`). These components load for anyone running Claude Code from this repo; they are **not** shipped to plugin users.

> **Don't confuse these with a plugin's own components.** `brand-studio/{skills,agents,commands,hooks}/` are *distributed* — they ship when someone installs the plugin. The identically-named folders under `.claude/` are *repo-local dev tools* that never leave this repo. Same file format, different audience.

## What goes where

| Path | One per | Becomes | Frontmatter | Shape to copy |
|---|---|---|---|---|
| `skills/<name>/SKILL.md` | skill (a folder) | a loadable skill | `name`, `description` (+ trigger phrases) | `brand-studio/skills/brand-methodology/SKILL.md` |
| `agents/<name>.md` | subagent | a dispatchable agent | `name`, `description` | `brand-studio/agents/critic-john-h.md` |
| `commands/<name>.md` | command | `/<name>` | `description`, `argument-hint` | `brand-studio/commands/brand-orient.md` |

Skills may carry supporting docs in `<name>/references/`, loaded on demand — keep `SKILL.md` a table of contents (the pattern the brand-studio skills follow).

## Settings

- `settings.json` — shared project settings (checked in). Add it when there's something to share.
- `settings.local.json` — your personal settings/permissions (git-ignored).
