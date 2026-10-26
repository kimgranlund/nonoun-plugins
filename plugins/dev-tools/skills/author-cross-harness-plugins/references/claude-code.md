# Claude Code Adapter

## Manifest

Claude reads `.claude-plugin/plugin.json`. Only the manifest belongs inside
`.claude-plugin/`; component directories remain at plugin root or at explicit
relative paths.

```json
{
  "name": "example-plugin",
  "version": "1.0.0",
  "description": "Example cross-harness workflows",
  "skills": "./adapters/claude/skills/",
  "commands": "./commands/",
  "hooks": "./adapters/claude/hooks.json",
  "mcpServers": "./adapters/claude/.mcp.json"
}
```

This example assumes at least one skill needs Claude-only frontmatter. When all
skills use default invocation behavior, point `skills` at `./skills/` and omit
the Claude skill adapter tree. Paths are relative to the plugin root and begin
with `./`. Omit absent component fields and bump the version when publishing.
**No `agents` field exists in this manifest** — see Agent adapter below;
`claude plugin validate` (verified against CLI 2.1.250) rejects an `agents` key
outright, tried both as a string and an array.

## Skill adapter

Codex-strict shared skills do not carry `disable-model-invocation`,
`user-invocable`, `context`, `agent`, or other Claude-only fields. When one is
needed, create the same skill path under `adapters/claude/skills/`, add only the
required Claude fields, and keep the body plus referenced resources identical
to the root skill. Generate and verify this tree; do not edit both copies by
hand.

## Agent adapter — no manifest override exists (verified, CLI 2.1.250)

Unlike skills, hooks, commands, and MCP, **Claude Code has no manifest field
for relocating agents.** It always discovers them from the plugin's own root
`agents/` directory by fixed convention — there is no `adapters/claude/agents/`
tree Claude will ever read, regardless of what the manifest says. This means
the adapter-tree pattern used for skills does not extend to agents: any
Claude-only agent frontmatter must live directly on the same root
`agents/<name>.md` file Codex also reads as its plain-body agent (per
`codex.md`'s "Codex plugin-level agents use root `agents/<name>.md` bodies").

Practically: keep Claude agents as Markdown with YAML frontmatter, on the root
`agents/<name>.md` file, body equal to what a Codex-only agent would read
(Codex tolerates the leading frontmatter block; it is not itself Codex syntax,
just ignored as non-body content by convention). Common frontmatter fields
include `name`, `description`, `model`, `effort`, `maxTurns`, `tools`,
`disallowedTools`, `skills`, `memory`, `background`, and `isolation`. Add only
fields with a deliberate effect.

Do not put `hooks`, `mcpServers`, or `permissionMode` in a plugin-shipped Claude
agent. A forked or background workflow includes a complete inline fallback in
the shared skill because those execution modes are not portable contracts.

## Command adapter

Claude command metadata can include `description` and `argument-hint`. Shared
command bodies do not require `$ARGUMENTS`; they read the human's current
request and branch when required inputs are missing.

## Hooks and local executables

Claude hook config retains the outer `hooks` wrapper. Use
`${CLAUDE_PLUGIN_ROOT}` for bundled executables inside the Claude adapter:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/check.sh"
          }
        ]
      }
    ]
  }
}
```

Persistent mutable plugin state belongs outside the installed plugin root. Do
not make shared behavior depend on Claude-specific state variables unless the
Codex adapter provides an equivalent store and lifecycle.

## Validation

Run Claude's plugin validator against the plugin root when the CLI is
available, then load with `--plugin-dir` or the intended marketplace. Test in a
fresh session; a previously loaded skill body can mask a bad edit.
