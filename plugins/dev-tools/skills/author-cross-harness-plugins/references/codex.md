# Codex Adapter

## Manifest

Codex reads `.codex-plugin/plugin.json`:

```json
{
  "name": "example-plugin",
  "version": "1.0.0",
  "description": "Example cross-harness workflows",
  "skills": "./skills/",
  "mcpServers": "./.mcp.json",
  "interface": {
    "displayName": "Example Plugin",
    "shortDescription": "Example cross-harness workflows",
    "longDescription": "Reusable workflows packaged for Claude Code and Codex.",
    "developerName": "Example Team",
    "category": "Developer Tools",
    "capabilities": ["Read", "Write"],
    "defaultPrompt": ["Run an example cross-harness workflow"]
  }
}
```

Omit absent component fields. Codex discovers plugin-level `agents/` and
`commands/` from their root convention. Keep plugin UI metadata in the
manifest or plugin-level `agents/openai.yaml`; keep skill UI and invocation
policy in each skill's `agents/openai.yaml`.

Keep root `SKILL.md` frontmatter within the fields accepted by Codex's Agent
Skills validator. Put Claude-only invocation, fork, or agent fields in the
Claude adapter tree, never in the root skill.

## Skill metadata

```yaml
interface:
  display_name: "Release Review"
  short_description: "Review a release across both harnesses"
  default_prompt: "Use $release-review to review this prepared release."

policy:
  allow_implicit_invocation: false

dependencies:
  tools:
    - type: "mcp"
      value: "example"
      description: "Example MCP server"
      transport: "streamable_http"
      url: "https://example.com/mcp"
```

Quote strings. `default_prompt` explicitly mentions `$skill-name`.
`dependencies.tools` advertises a dependency; it does not grant permission.

## Agents and commands

Codex plugin-level agents use root `agents/<name>.md` bodies. Keep host-neutral
behavior there. Plugin UI metadata can coexist as `agents/openai.yaml`.

Keep three mechanisms distinct:

| Mechanism | Scope | Authoring implication |
|---|---|---|
| Plugin-provided agent | Plugin root `agents/<name>.md` | Preserve the shared body and Claude frontmatter arrangement described in [surface-matrix.md](surface-matrix.md). |
| Optional native Codex subagent | Project `.codex/agents/<name>.toml`, where supported by the target Codex version | Generate from the same role contract if it adds useful native role settings. Installation is a separate, opt-in project step; verify discovery in a fresh session. Keep generated definitions in parity with their source. |
| Main-session conductor guidance | Session or project instruction mechanism supported by the target host | This is instruction guidance for the top-level session, not a named agent binding. A TOML `developer_instructions` field in an agent definition describes that agent; a top-level config field does not select a named conductor. |

Native project agents are an optional enhancement, not a correction to plugin-level
agents. If offered, document the install and removal path, project trust requirements,
and a complete plugin or serial fallback. Check the target host's actual support and
effective discovery before promising the native route.

When an opt-in installer edits an existing Codex `config.toml`, treat it as user-owned
configuration. Accept arbitrary valid TOML rather than a narrow generated subset;
preserve existing keys, instruction text, comments, newline style, and permissions.
Mark only the bytes the installer owns, make repeated install a no-op, and remove only
unchanged owned content. Refuse to overwrite or remove an edited managed block or a
conflicting user setting. Do not add config editing merely to install plugin agents;
use it only when the requested feature needs top-level instruction wiring and the
target host supports that mechanism.

Codex commands use root `commands/<name>.md`. Keep the command self-contained,
human-timed, and independent of Claude argument-expansion tokens. If it asks a
Codex agent to take substantial work, name the agent; the same command still
defines a serial fallback when delegation is unavailable.

## Hooks

Keep Codex hooks at root `hooks.json` with the outer `hooks` wrapper. Do not add
`hooks` to the Codex manifest: the current ingestion validator rejects that
field and root hooks are discovered by convention. Use commands that Codex can
resolve in the installed plugin; do not use `${CLAUDE_PLUGIN_ROOT}`.

## Marketplace

Repository and personal marketplaces use `.agents/plugins/marketplace.json`.
Each entry includes a relative `source.path`, installation policy,
authentication policy, and category. This file is not interchangeable with a
Claude marketplace catalog.

```json
{
  "name": "example-marketplace",
  "interface": { "displayName": "Example Marketplace" },
  "plugins": [
    {
      "name": "example-plugin",
      "source": { "source": "local", "path": "./plugins/example-plugin" },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

After marketplace or plugin changes, use a fresh Codex task or restart when
the new surfaces are not detected. Verify selection plus actual behavior.

For live CLI examples, pass a deliberately selected available model and reasoning
effort (for example, `codex exec --model <chosen-model> -c
'model_reasoning_effort="<chosen-effort>"' ...`) and record observed identity when
the host exposes it. Do not let a test silently inherit an expensive default.

## Installing from GitHub (verified 2026-08-31, adiahealth/adia-harness)

Two separate steps, not one — registering the marketplace does not itself enable the plugin:

```
codex plugin marketplace add owner/repo
codex plugin add <plugin-name>@<marketplace-name>
```

The first reads that repo's `.agents/plugins/marketplace.json` straight from GitHub, no clone
needed, and exposes `<plugin-name>@<marketplace-name>` as installable. The second actually
enables it — `codex plugin install` does not exist on at least one observed CLI version; the
real subcommand is `codex plugin add`. `codex plugin marketplace list` shows only marketplace
roots — verify the INSTALL with `codex plugin list` (plugin, enabled state, version);
`codex plugin list` (or equivalent) confirms the plugin's enabled version. A read-only ephemeral
run against an untrusted-git-repo working directory hits a trust check before routing —
`--skip-git-repo-check` on `codex exec` is the documented bypass for that case.

## Agent/hook parity statement (ticket adiahealth/adia-harness#109)

A plugin's README Codex section states agent/hook parity explicitly — never leaves a Codex
reader to discover by omission that an agent or hook silently isn't there. When Codex drops
agents and/or hooks (no `agents`/`hooks` key in `.codex-plugin/plugin.json`), the Codex section
names, for EACH dropped agent and EACH dropped hook, the manual equivalent: what a human (or a
second Codex session, for a fresh-context reviewer agent) does by hand instead. "Codex ships
fewer agents/hooks than Claude" alone is not a parity statement — a reader needs the substitute,
not just the gap. Repo-adapter-wins-class filesystem checks (ticket-88/#109) carry the same
discipline: a defer-check keyed to Claude's own `.claude/skills/<name>/SKILL.md` also checks
Codex's own repo-local convention, `.agents/skills/<name>/SKILL.md` — Claude's location wins
when both exist (unchanged precedence), Codex's location isn't silently skipped.
