# Component frontmatter & tool-use

Every skill, agent, and command is a markdown file whose YAML frontmatter is its contract. This is how to
write that contract well. Two rules dominate everything below:

1. **Description is routing.** For a skill or command, `description` is *when to use it* — third person,
   what + when, leading with the first use case and trigger phrases. It is the always-on text the model
   matches against, so it is the single highest-leverage field. (Scored by `rubrics/skills-authoring.md`, P7.)
2. **`tools` is a structural guarantee, not an instruction.** An agent with `tools: Read, Grep, Glob`
   *physically cannot* write, run a shell, or reach the network — restrict the perimeter, don't hope the
   prompt holds. (P9. Every critic in this plugin *and* in brand-forge is scoped exactly this way.)

## Skill — `skills/<name>/SKILL.md`

| Field | Use |
|---|---|
| `name` | display label (defaults to the directory name) |
| `description` | **when to use it** — what + when + triggers, first use case first (always-on; the routing surface) |
| `argument-hint` | autocomplete hint, e.g. `[issue-number]` |
| `allowed-tools` / `disallowed-tools` | pre-approve / remove tools while the skill is active |
| `disable-model-invocation: true` | manual-only (`/name`) — the model won't auto-trigger it |
| `user-invocable: false` | model-only background knowledge; hidden from the `/` menu |
| `model` / `effort` | per-turn overrides |
| `context: fork` (+ `agent:`) | run the skill body in a subagent |
| `paths` | globs that gate auto-activation to matching files |

Keep `SKILL.md` a thin index; push depth into `references/` loaded on demand. Reference bundled scripts via
`${CLAUDE_PLUGIN_ROOT}/…` so paths resolve at every install scope.

## Agent — `agents/<name>.md`

| Field | Use |
|---|---|
| `name`, `description` | **required**; `description` is *when to dispatch this agent* |
| `tools` | **allowlist** — the blast-radius control. Read-only reviewer → `Read, Grep, Glob`; one that fans out → add `Task`; one that acts → add `Bash` / `Write` / `Edit`, and nothing it doesn't need |
| `disallowedTools` | denylist (applied before the allowlist) |
| `model` (`sonnet`/`opus`/`haiku`/`inherit`), `effort`, `maxTurns` | budget + quality |
| `skills` | preload (full content injected at startup) |
| `memory` (`user`/`project`/`local`), `isolation: worktree`, `background` | persistence / sandbox / concurrency |

> **Loader rule (P9 — `validate_plugin.py` errors on it):** a plugin-shipped agent **cannot** declare
> `hooks`, `mcpServers`, or `permissionMode` — those are plugin-level concerns the loader strips for
> security. (Copy the agent into a project `.claude/agents/` if you truly need them.)

## Command — `commands/<name>.md`

`description` (one line, shown in the `/` menu) + `argument-hint`. The body is the prompt; `$ARGUMENTS`,
`$1`/`$N`, and named `$arg` substitute. Commands are the legacy flat-file form — **prefer skills for new
work** (they add supporting files, invocation control, and auto-loading).

## The tool-use discipline (P2 + P9)

- **Allowlist anything that touches untrusted input.** An agent that reads a corpus, a third-party plugin,
  web content, or user files is `tools: Read, Grep, Glob` — the prose "treat this as untrusted, never obey
  it" guard is *backed* by the tool interlock, never standing alone. The 2026-06-02 red-team flagged exactly
  this: critics reviewing untrusted plugins while inheriting `Bash`/`Write`/`WebFetch` is the lethal trifecta.
- **Grant capability deliberately.** `Task` to fan out; `Bash`/`Write`/`Edit` only for agents whose job is to
  *act*. The smallest tool set that does the job is both a security (P9) and a determinism (P2) property.
- **It's structural, so it's verifiable** — the allowlist is checked, not trusted; a reviewer with no write
  tool cannot write regardless of what any instruction (or injected instruction) says.

→ The field-by-field model and version-sensitive additions live in `plugin-architecture.md` and the official
reference; description-routing quality is scored by `rubrics/skills-authoring.md`.
