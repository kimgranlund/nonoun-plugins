# Surface Mapping

Use the smallest row set needed by the plugin being authored.

| Surface | Shared core | Claude adapter | Codex adapter | Fidelity rule |
|---|---|---|---|---|
| Plugin identity | name/version/description/author/license | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | Identity fields match |
| Repository entry | Shared project instructions and routing | `CLAUDE.md`, commonly importing the shared authority | `AGENTS.md` shared authority | No duplicated behavioral rules; fresh clone resolves imports |
| Skill | `skills/<name>/SKILL.md`, references, scripts, assets | Shared tree when defaults suffice; generated `adapters/claude/skills/` when Claude-only frontmatter is needed | Root skill plus `agents/openai.yaml` for UI, implicit policy, MCP dependencies | Adapter body/resources match shared source |
| Agent | Plain instruction body | Claude frontmatter prepended directly on root `agents/<name>.md` (no manifest override exists — verified, CLI 2.1.250) | `agents/<name>.md` plain body | Bodies match after frontmatter removal |
| Optional native project subagent | Same role contract as the plugin agent | Existing plugin agent remains available | Project-installed `.codex/agents/<name>.toml` where supported; separate opt-in installation | Generated role instructions stay in parity; fresh-session discovery and fallback are checked |
| Main-session guidance | Shared conductor rules when the workflow needs them | Host-supported session or project instructions | Host-supported session or project instructions; top-level `developer_instructions` is guidance, not a named agent binding | Effective startup instructions and removal are observed before claiming activation |
| Command | Plain human-invoked workflow body | Shared `commands/` or adapter with Claude metadata | Root `commands/` | No `$ARGUMENTS` dependency in shared body |
| Hook | Event/matcher/action intent | Manifest points to adapter using Claude path substitution when needed | Root `hooks.json` is convention-discovered and uses a Codex-resolvable command | Event and side effect match |
| MCP | Server identity, tool contract, auth intent | Shared remote config or Claude local adapter | Shared remote config or root `.mcp.json` | Command, args, env, URL, and auth match |
| Script/asset/reference | Portable file | Same file | Same file | No copied behavioral fork |
| Marketplace | Plugin identity and source | Claude marketplace schema/location | `.agents/plugins/marketplace.json` | Same release/source intent; schemas stay separate |
| Native enhancement | Shared fallback workflow | Claude-native surface | Codex-native surface | Enhancement is optional; fallback is complete |

## Skills

Portable frontmatter is `name`, `description`, and when needed `license` and
string-valued `metadata`. Keep `description` at or under 1024 characters — the portable
validator rejects longer ones, and ([behavioral-fidelity.md](behavioral-fidelity.md) rule 2) only its FIRST sentence is
guaranteed visible at routing time, so front-load what gates routing and spend the budget there. Treat `allowed-tools` as experimental rather than a
cross-harness permission contract. Use only fields accepted by both target
validators; do not leave Claude-only fields in the shared `SKILL.md`.

When Claude invocation controls are needed, generate a Claude adapter skill
whose body and resources match the root skill. Put the controls there:

```yaml
disable-model-invocation: true
user-invocable: true
```

Put the matching human-only policy in the root skill's Codex metadata:

```yaml
policy:
  allow_implicit_invocation: false
```

Mapping:

| Intent | Claude | Codex |
|---|---|---|
| Human or model may invoke | `disable-model-invocation: false` | omit policy or set `true` |
| Human-only timing | `disable-model-invocation: true` | `allow_implicit_invocation: false` |
| Model-only knowledge | Claude adapter uses `user-invocable: false` | No exact published equivalent; document that explicit invocation remains possible |
| Forked skill | Claude adapter uses `context: fork` / `agent:` | No skill-frontmatter equivalent; write a self-sufficient inline/delegation fallback |

When both harnesses may invoke the skill implicitly, point both manifests at the
root `skills/` tree and do not generate a Claude skill adapter. When any
Claude-only field is required, point the Claude manifest at the complete
generated adapter tree and the Codex manifest at root `skills/`.

`allowed-tools` is a Claude permission grant. Codex
`dependencies.tools` declares availability; it is not the same control.

## Agents

The portable agent body defines purpose, inputs, decision rules, output, and
completion condition. Keep model selection, tool allowlists, preloaded skills,
background mode, memory, and worktree isolation in Claude-only frontmatter
unless a Codex-native field has been verified for the target version.

If a Claude agent preloads a skill, the shared body also names the required
skill and the serial fallback. Otherwise the Codex agent silently loses
required context.

**No separate adapter file: Claude Code has no manifest field for relocating
agents** (verified against CLI 2.1.250 — an `agents` key in `plugin.json` is
rejected outright, tried both as a string and an array). It always discovers
agents from the plugin's own root `agents/` directory. Unlike skills, hooks,
and commands, there is no `adapters/claude/agents/` tree — Claude-only
frontmatter goes directly on the same root file:

```markdown
---
name: release-review
description: Reviews a prepared release when the user asks for a release gate.
tools: Read, Grep, Glob, Bash
---

You are the release-review agent for this plugin.

Purpose:
- Verify the release without mutating it.

Output:
1. Findings
2. Evidence
3. Verdict
```

Codex reads the same file as its plain-body agent, tolerating the leading
frontmatter block as non-body content. The text after the closing `---` is
what Codex treats as its own root agent body — there is no second file to keep
in sync.

## Commands

Commands are human-timed entry points. A portable body reads the current user
request instead of depending on host argument interpolation. Put expected
inputs under an `Arguments` heading and define the missing-input branch.

Use a Claude adapter only when `argument-hint`, allowed tools, or another
Claude-only command field materially improves the surface. Otherwise one plain
file under `commands/` is the preferred shared form.

## Hooks

Both hook configs use an outer `hooks` object. Share the event contract, not an
unverified shell path. If the command differs, keep `hooks.json` for Codex and
`adapters/claude/hooks.json` for Claude. Point only the Claude manifest to its
adapter; the current Codex ingestion validator rejects a `hooks` manifest field
and discovers root `hooks.json` by convention.

Hook scripts are idempotent, narrowly scoped, and return nonzero only for a
real blocking condition. A hook that enforces essential workflow behavior also
needs an instruction-level fallback because a host or permission setting may
disable hooks.

## MCP

Remote HTTPS servers can usually share one config when URL, headers, and auth
are identical. Bundled local servers often need adapters because
`${CLAUDE_PLUGIN_ROOT}` is Claude-specific. Prefer an executable on `PATH` or
generate separate configs. Never copy a Claude token verbatim into the Codex
manifest and label the MCP surface portable.

## Host-only surfaces

For any surface without a verified equivalent:

1. Decide whether it is essential behavior or an enhancement.
2. Essential behavior moves into a shared skill/script workflow.
3. The native surface becomes an adapter over that workflow.
4. The absence and fallback are recorded in `HARNESS-NOTES.md`.
