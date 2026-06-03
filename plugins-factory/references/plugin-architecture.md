---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# Claude Code Plugin Architecture — Technical Reference

The canonical technical model of a Claude Code plugin — manifest, component set, layout rules, path variables, marketplace, and security surface — that this skill's P4/P5 rubrics build against. Accurate to the official reference: <https://code.claude.com/docs/en/plugins-reference> (verified 2026-06-02).

**A plugin is a self-contained directory of components that extends Claude Code.** Components are skills, agents, commands, hooks, MCP servers, LSP servers, monitors, themes, output styles, and executables. A plugin is the unit you _install, toggle, version, and trust_ as one thing; a component is the unit of capability inside it.

Source pages cited throughout:

| Page | URL |
| --- | --- |
| Plugins reference (schemas, CLI, components) | <https://code.claude.com/docs/en/plugins-reference> |
| Plugins (tutorial / creation) | <https://code.claude.com/docs/en/plugins> |
| Plugin marketplaces (distribution) | <https://code.claude.com/docs/en/plugin-marketplaces> |
| Discover & install plugins | <https://code.claude.com/docs/en/discover-plugins> |
| Agent Skills (engineering) | <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills> |
| Writing tools for agents | <https://www.anthropic.com/engineering/writing-tools-for-agents> |

---

## 1. The manifest (`.claude-plugin/plugin.json`)

**The manifest is the only file that can live in `.claude-plugin/` — and it is itself optional.** If omitted, Claude Code auto-discovers components in their [default locations](#2-the-component-set--the-critical-layout-rule) and derives the plugin name from the directory name. Use a manifest when you need metadata or custom component paths. _If present, `name` is the only required field._

The `name` is used for **namespacing** components: for plugin `plugin-dev`, the agent `agent-creator` appears as `plugin-dev:agent-creator`.

### Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | string | **yes** (if manifest present) | kebab-case, no spaces. The namespace key. |
| `displayName` | string | no | Human-readable UI label; may contain spaces/any casing. Falls back to `name`. Not used for lookup. (≥ v2.1.143) |
| `version` | string | no | Semver. See §4 version resolution. If omitted → git SHA mode. |
| `description` | string | no | Brief purpose. |
| `author` | object | no | `{name, email, url}`. |
| `homepage` | string | no | Docs URL. |
| `repository` | string | no | Source URL. |
| `license` | string | no | e.g. `"MIT"`, `"Apache-2.0"`. |
| `keywords` | array | no | Discovery tags. |
| `defaultEnabled` | boolean | no | Defaults `true`; set `false` to install disabled (opt-in cost/scope). User's `enabledPlugins` and dependency requirements both override it. (≥ v2.1.154) |
| `$schema` | string | no | Editor autocomplete hint; ignored at load time. |
| `skills` | string\|array | no | Custom skill dirs — **ADDS** to default `skills/`. |
| `commands` | string\|array | no | Flat `.md` skill files/dirs — **REPLACES** default `commands/`. |
| `agents` | string\|array | no | Agent files — **REPLACES** default `agents/`. |
| `hooks` | string\|array\|object | no | Hook config path(s) or inline — own merge rules. |
| `mcpServers` | string\|array\|object | no | MCP config path(s) or inline — own merge rules. |
| `outputStyles` | string\|array | no | **REPLACES** default `output-styles/`. |
| `lspServers` | string\|array\|object | no | LSP config path(s) or inline — own merge rules. |
| `experimental.themes` | string\|array | no | **REPLACES** default `themes/`. Experimental. |
| `experimental.monitors` | string\|array | no | **REPLACES** default `monitors/`. Experimental. |
| `userConfig` | object | no | Values prompted at enable time; exposed as `${user_config.KEY}`. |
| `channels` | array | no | Message-injection channels bound to a bundled MCP server. |
| `dependencies` | array | no | Other plugins required; optional semver constraints. |

### Unrecognized fields are ignored (foreign metadata is safe)

Claude Code **ignores top-level fields it does not recognize**, so one `plugin.json` can double as a VS Code/Cursor manifest, an npm `package.json`, or an MCPB/DXT bundle manifest. `claude plugin validate` reports unrecognized fields as **warnings** (and suggests a likely intended name when one is ~1–2 chars off) — the plugin still loads. **A recognized field with the wrong type is a hard error** (e.g. `keywords` as a string instead of an array). Pass `--strict` to treat warnings as errors (use in CI to catch a typo'd or leftover field).

### Minimal valid manifest

```json
{
  "name": "deployment-tools",
  "description": "Deployment automation tools",
  "version": "1.0.0",
  "author": { "name": "Dev Team", "email": "dev@company.com" }
}
```

`{ "name": "deployment-tools" }` alone is also valid.

---

## 2. The component set + the critical layout rule

A plugin can bundle:

| Component | Default location | Format | Notes |
| --- | --- | --- | --- |
| **Skills** | `skills/<name>/SKILL.md` | dir with `SKILL.md` | Model-auto-invoked; `/name` shortcut. Supporting files allowed alongside. |
| **Commands** | `commands/*.md` | flat `.md` file | Legacy flat-file skills. **"Use `skills/` for new plugins."** |
| **Agents** | `agents/*.md` | `.md` + frontmatter | Subagents; appear in `/agents`. |
| **Hooks** | `hooks/hooks.json` | JSON | Event matchers + actions; or inline in `plugin.json`. |
| **MCP servers** | `.mcp.json` | MCP server config | Or inline `mcpServers`. Start automatically when the plugin is enabled. |
| **LSP servers** | `.lsp.json` | JSON | Code intelligence; binary must be installed separately. Or inline. |
| **Monitors** | `monitors/monitors.json` | JSON array | **Experimental.** Background watchers; per-session stdout → notifications. |
| **Themes** | `themes/*.json` | JSON (`base` + `overrides`) | **Experimental.** Appear in `/theme`. |
| **Output styles** | `output-styles/*.md` | `.md` | — |
| **Executables** | `bin/` | any executable | **Added to the Bash tool `PATH`** — invokable as a bare command while enabled. |
| **Settings** | `settings.json` | JSON | Default settings. **Only the `agent` and `subagentStatusLine` keys are honored.** |
| **Manifest** | `.claude-plugin/plugin.json` | JSON | Metadata (optional). |

### THE #1 LAYOUT RULE

> **Only `plugin.json` goes in `.claude-plugin/`. ALL other component directories must be at the plugin ROOT.**

Components placed _inside_ `.claude-plugin/` **silently fail to load** — the plugin loads, the components just go missing. This is the single most common structural defect (docs list it under "Skills not appearing → wrong directory structure").

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json        ← ONLY the manifest here
├── skills/                ← at ROOT
├── commands/              ← at ROOT
├── agents/                ← at ROOT
├── hooks/hooks.json       ← at ROOT
├── .mcp.json              ← at ROOT
├── bin/                   ← at ROOT (joins PATH)
└── CHANGELOG.md
```

**A plugin-root `CLAUDE.md` is NOT loaded as context.** Plugins contribute context through skills, agents, and hooks — to ship instructions, put them in a **skill**, not `CLAUDE.md`.

### Path-field merge semantics

| Behavior | Fields |
| --- | --- |
| **REPLACE** the default dir | `commands`, `agents`, `outputStyles`, `experimental.themes`, `experimental.monitors` — naming the field stops the default dir from being scanned. To keep both, list it: `"commands": ["./commands/", "./extras/"]`. |
| **ADD** to the default dir | `skills` — default `skills/` is always scanned; listed dirs load alongside. |
| **Own merge rules** | `hooks`, `mcpServers`, `lspServers` — see each section for how multiple sources combine. |

When a default folder _and_ its matching manifest key both exist, the ignored folder is flagged in `/doctor`, `claude plugin list`, and the `/plugin` detail view (≥ v2.1.140); the plugin still loads using the manifest paths.

### Agent frontmatter (and the security carve-out)

Plugin agents support: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, and `isolation`. The only valid `isolation` value is `"worktree"`.

> **SECURITY:** plugin-shipped agents **CANNOT** declare `hooks`, `mcpServers`, or `permissionMode`. This is a loader-enforced restriction, not a convention — rely on it, not on model behavior.

### Hooks

`hooks/hooks.json` maps lifecycle events → matchers → hook actions (or inline in `plugin.json`).

- **Event names are case-sensitive** (`PostToolUse`, not `postToolUse`). Events include `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `SubagentStart`/`SubagentStop`, `PreCompact`/`PostCompact`, `SessionEnd`, and ~30 others.
- **Hook `type` ∈ `command` | `http` | `mcp_tool` | `prompt` | `agent`:** `command` runs a shell command/script; `http` POSTs the event JSON to a URL; `mcp_tool` calls a configured MCP tool; `prompt` evaluates a prompt with an LLM; `agent` runs an agentic verifier with tools.
- **A malformed `hooks/hooks.json` blocks the WHOLE plugin** — not just the hooks.
- Reference bundled scripts via `${CLAUDE_PLUGIN_ROOT}`; in shell-form, double-quote it: `"\"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.sh"`.

### MCP servers

`.mcp.json` (or inline `mcpServers`). **Servers start automatically when the plugin is enabled** and appear as standard MCP tools. This makes a bundled MCP the most expensive component to ship (its tool defs are always-on context) and the one with the largest trust surface.

### `@skills-dir` plugins (in-place, no install)

Any folder under a skills directory that contains a `.claude-plugin/plugin.json` is loaded as a plugin named `<name>@skills-dir` on the next session — **discovered in place, not copied into the cache** (so the §3 path-traversal limit does not apply to this mode). `~/.claude/skills/` loads personally in every project; `<cwd>/.claude/skills/` loads at project scope after the trust dialog, with MCP/LSP gated and background monitors disabled. Scaffold with `claude plugin init <name>`.

---

## 3. Path variables

Three variables are substituted inline anywhere they appear in skill/agent content, hook commands, monitor commands, and MCP/LSP configs — and are exported to hook and server subprocesses.

| Variable | Resolves to | Lifetime | Use for |
| --- | --- | --- | --- |
| `${CLAUDE_PLUGIN_ROOT}` | absolute path to the installed plugin dir | **EPHEMERAL** — changes on every update (old version dir lingers ~7 days then is cleaned up) | referencing bundled scripts, binaries, config. **Never write state here.** |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/{id}/` | **PERSISTENT** — survives updates | caches, `node_modules`, Python venvs, generated code, any state that must persist across versions. Created on first reference. |
| `${CLAUDE_PROJECT_DIR}` | the project root | per-project | project-local scripts/config. Quote it for paths with spaces. |

`{id}` is the plugin identifier with characters outside `[A-Za-z0-9_-]` replaced by `-` (e.g. `formatter@my-marketplace` → `~/.claude/plugins/data/formatter-my-marketplace/`). The data dir is deleted on uninstall from the last scope (pass `--keep-data` to preserve). Because it outlives any version, the recommended dependency-install pattern **diffs the bundled manifest against a copy in the data dir** and reinstalls only on change.

> When a plugin updates mid-session, hooks/monitors/MCP/LSP keep using the _previous_ version's `${CLAUDE_PLUGIN_ROOT}`. `/reload-plugins` switches hooks/MCP/LSP to the new path; monitors need a session restart.

### THE PATH-TRAVERSAL LIMIT (load-bearing)

For security and verification, marketplace plugins are **copied into a version-keyed cache** (`~/.claude/plugins/cache`), one directory per installed version, _not_ used in place.

> **Installed plugins CANNOT reference files outside their own directory.** A `../shared-utils` path does **not** resolve after install, because external files are never copied into the cache. A plugin can be correct on disk and broken in the cache.

**All component paths must be relative and start with `./`.** Absolute paths are a load error.

To share files **within the same marketplace**, use symlinks inside the plugin directory — handled at copy time by where the target resolves:

| Symlink target | Behavior |
| --- | --- |
| Within the plugin's **own** directory | **Preserved** as a relative symlink — keeps resolving to the copied target. |
| Elsewhere in the **same marketplace** | **Dereferenced** — the target's content is copied in its place (lets a meta-plugin's `skills/` link to skills defined by sibling plugins). |
| **Outside** the marketplace | **Skipped** for security — prevents pulling arbitrary host files into the cache. |

For `--plugin-dir` / local installs, only symlinks resolving within the plugin's own directory are preserved; all others are skipped. (For cross-plugin code reuse, prefer the manifest `dependencies` field over symlinks where possible.)

---

## 4. Marketplace & distribution (`.claude-plugin/marketplace.json`)

A marketplace is typically a git repo. (Details: <https://code.claude.com/docs/en/plugin-marketplaces>.)

### Required fields

| Field       | Notes                              |
| ----------- | ---------------------------------- |
| `name`      | kebab-case marketplace identifier. |
| `owner`     | `{name, email?}`.                  |
| `plugins[]` | array of plugin entries.           |

Each **plugin entry** carries `name` + `source` (plus any `plugin.json` field, `category`, `tags`, and `strict`).

### `source` forms

| Form | Shape | Notes |
| --- | --- | --- |
| relative path | `"./my-plugin"` | git-added marketplaces only. |
| github | `{ "source": "github", "repo": "...", "ref?": "..." }` | — |
| url | `{ "source": "url", "url": "...", "ref?": "..." }` | — |
| git-subdir | `{ "source": "git-subdir", "url": "...", "path": "..." }` | — |
| npm | `{ "source": "npm", "package": "..." }` | version → `unknown` (no SHA). |

> **A `source` containing `..` is a hard error.**

### `strict` (default `true`)

- **`true`** — `plugin.json` is the authority; the marketplace entry _supplements_ it.
- **`false`** — the marketplace entry is the _entire_ definition (no `plugin.json` needed). Specifying components in **both** with `strict: false` raises a conflicting-manifests error.

### Version resolution (first that is set wins)

1. `version` in `plugin.json`
2. `version` in the marketplace entry
3. git commit SHA (for `github` / `url` / `git-subdir` / relative-path sources in a git-hosted marketplace)
4. `unknown` (npm sources or local non-git directories)

> **Do NOT set `version` in both `plugin.json` and the marketplace entry — `plugin.json` wins silently.** Set explicit semver → users update only on a bump (`/plugin update` otherwise reports "already at the latest version"). Omit `version` everywhere → every commit is an update (SHA mode), best for fast-iterating internal/team plugins. If you set a `version`, you **must** bump it for users to receive changes; follow semver and keep a `CHANGELOG.md`.

### Install

```bash
/plugin marketplace add owner/repo
/plugin install name@marketplace          # or: claude plugin install name@marketplace
```

Reserved marketplace names exist (e.g. `anthropic-*`, `claude-*`). Install scopes: `--scope user|project|local` (see §6).

---

## 5. Skill vs Plugin vs MCP — the decision

These are not alternatives at the same level; they sit at different layers.

| Thing | What it is | Invoked by |
| --- | --- | --- |
| **Skill** | Teaches a _procedure_ via progressive disclosure (SKILL.md as a TOC, references loaded on demand). | The model, automatically, from its description. |
| **MCP server** | Connects to an _external/stateful system_. **A plugin _component type_, not an alternative to a plugin.** | The model, as tools. |
| **Plugin** | The shareable / versioned / toggleable **BUNDLE** that can carry skills, agents, commands, hooks, **and** MCP servers as one unit. | Installed & enabled; its components then fire. |

**Decision:**

- A **standalone `.claude/` skill** (short name `/hello`) for personal / project / experimental work.
- A **plugin** (namespaced `/plugin:hello`) when you need to **share, version, or reuse** across projects and people.

> **"Start standalone, convert to a plugin when ready to share."** An MCP wraps an _external system_; a skill teaches the _procedure_ — they are complementary, and an MCP that wraps API endpoints 1:1 is the field's most-cited anti-pattern (see _Writing tools for agents_).

---

## 6. Validation, namespacing, scopes, security

### Namespacing

Plugin skills are invoked as **`/plugin-name:skill-name`** — the `name` field is the namespace, which prevents collisions between plugins (two plugins can each ship a `review` skill without clashing).

### Validation & inspection

| Command | What it checks / shows |
| --- | --- |
| `claude plugin validate <path> [--strict]` | `plugin.json` + skill/agent/command frontmatter + `hooks/hooks.json` for syntax and schema errors. `--strict` promotes unrecognized-field warnings to errors. |
| `claude plugin details <name>` | Component inventory (Skills, Agents, Hooks, MCP, LSP) + a **token-cost breakdown**: **always-on** (listing text — descriptions, names — paid every session) vs **on-invoke** (paid per component when it fires). |
| `claude --debug` | Plugin loading details: which plugins load, manifest errors, skill/agent/hook registration, MCP init. |
| `/doctor`, `claude plugin list` | Surface ignored-folder warnings and enable status. |

The always-on / on-invoke split is the mechanical basis for the context-economy dimension: an MCP server's tool defs or verbose descriptions dominating _always-on_ is the signal a plugin is too expensive to leave enabled.

### Install scopes

| Scope | Settings file | Use |
| --- | --- | --- |
| `user` | `~/.claude/settings.json` | Personal, all projects (default). |
| `project` | `.claude/settings.json` | Team, shared via version control. |
| `local` | `.claude/settings.local.json` | Project-specific, gitignored. |
| `managed` | managed settings | Read-only, update-only. |

**Team distribution:** declare `extraKnownMarketplaces` + `enabledPlugins` so a repo ships its plugin set to every collaborator. **Managed lockdown:** `strictKnownMarketplaces` (and `blockedMarketplaces`) constrain which marketplaces — and the `@skills-dir` source — are allowed.

### Security posture

> **"Plugins and marketplaces are highly trusted components that can execute arbitrary code on your machine with your user privileges."**

The execution surface is real and mostly automatic:

- a **hook** fires on your events (and a `command`/`agent` hook runs code),
- a **bundled MCP server** starts the moment the plugin is enabled,
- a **`bin/`** executable joins your Bash `PATH`,
- a **monitor** runs a persistent unsandboxed command for the session.

Trust is _designed in_, never assumed from model behavior: document every hook's side-effect and matcher breadth, scope bundled MCP servers to the minimum perimeter, and rely on the loader rule that plugin-shipped agents cannot declare `hooks`/`mcpServers`/`permissionMode`. Watch for the **lethal trifecta** in any single bundled component — private-data access + untrusted-content exposure + external-action capability — and structurally separate those concerns. **Only install plugins and marketplaces from trusted sources.**

---

## Appendix — facts most often gotten wrong

| Claim | Reality |
| --- | --- |
| "The manifest is required." | No — it's optional; if present, only `name` is required. |
| "Put components in `.claude-plugin/`." | Only `plugin.json`. Everything else at root or it silently won't load. |
| "Ship instructions in `CLAUDE.md`." | A plugin-root `CLAUDE.md` is not loaded. Use a skill. |
| "`../shared` works, it does on disk." | Breaks after install (version-keyed cache copy). Co-locate, use `dependencies`, or same-marketplace symlink. |
| "Write cache/state next to my scripts." | `${CLAUDE_PLUGIN_ROOT}` is ephemeral. Persistent state → `${CLAUDE_PLUGIN_DATA}`. |
| "Set `version` in both manifest and marketplace entry." | `plugin.json` wins silently. Pick one place. |
| "`commands`/`agents` paths add to the defaults." | They REPLACE. Only `skills` adds. |
| "An agent in my plugin can add a hook/MCP." | Forbidden for plugin-shipped agents (loader-enforced). |
| "A bad `hooks.json` just disables hooks." | It blocks the whole plugin. |
| "MCP = an alternative to a plugin." | MCP is a _component type_ a plugin can bundle. |
