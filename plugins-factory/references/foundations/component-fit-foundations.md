---
date: 2026-06-02
status: draft
coverage: canonical
version: "0.1.0"
primary_sources:
  - "Anthropic. Claude Code Plugins reference. code.claude.com/docs/en/plugins-reference"
  - "Anthropic. Claude Code Hooks reference. code.claude.com/docs/en/hooks"
  - "Anthropic (2025). Equipping agents for the real world with Agent Skills. anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills"
  - "Anthropic (2025). Writing tools for agents. anthropic.com/engineering/writing-tools-for-agents"
  - "A Mental Model for Claude Code: Skills, Subagents, and Plugins. levelup.gitconnected.com"
  - "Why MCP Shouldn't Wrap an API One-to-One. nordicapis.com"
  - "Your MCP Servers Are Eating Your Context. blog.lakshminp.com"
---

# Component Fit — Foundational Knowledge Document

The theory behind P2: a plugin bundles five kinds of component, and each capability has a *right* one determined by the shape of its task — not by taste, and not by the default of "make everything a skill."

## The Core Claim

A plugin is not a pile of skills. It is a bundle that can carry **five distinct primitives** — hooks, MCP servers, agents, skills, and commands — and the single highest-frequency plugin defect is putting a capability in the wrong one. Component fit is the discipline of reading a capability's task-shape and assigning the primitive that shape determines.

The field has converged on a clean split. Two of the primitives are **knowledge** (what the model knows or does *in* context — skills and commands); three are **control / workers** (things that run deterministically or in isolation — hooks, agents, and MCP servers). The decisive properties:

- **A hook guarantees execution; a prompt does not.** This is the load-bearing distinction. Anything that *must* run on an event — a formatter, a lint gate, a policy check, a notification — is a hook, because "hooks guarantee execution; prompts do not." A skill or instruction that says "always run the linter" runs *usually*; one day the model is under context pressure and skips it.
- **An MCP connects to external systems; a skill teaches the procedure.** They are complementary, not alternatives. The MCP is the action perimeter (live tools, auth, external state); the skill is the procedural knowledge of how to use it. An MCP that 1:1-wraps API endpoints is the field's most-cited anti-pattern.
- **An agent isolates context and parallelizes.** A subagent runs in its own context window with its own tools and permissions — use it when a task would pollute or blow the main context, or when you want parallel fan-out.
- **A skill is model-auto-invoked knowledge** loaded by progressive disclosure — the default home for "a repeatable, knowledge-rich workflow that only matters sometimes."
- **A command is a user-named action** — an explicit, manual entry point the *user* fires by name.

## The decision ladder

Read the capability's task-shape top to bottom; take the first match.

1. **Must it run deterministically on an event, regardless of model behavior?** → **Hook** (`hooks/hooks.json`). Cheapest on context (harness-only, no model-context cost), and the only primitive that *guarantees*. Signals: "auto-format every file written", "block `rm -rf` before it executes", "validate on commit", "notify on completion".
2. **Does it reach an external / stateful system (a DB, a SaaS API, a service with auth)?** → **MCP server** (`.mcp.json`). The costliest primitive (tool definitions are *always-on* context), so it must clear the highest bar: intent-level tools, not endpoint wraps. Signals: live integration, authenticated services, real-time/stateful data.
3. **Will it consume or produce large context, or benefit from isolation / parallelism?** → **Agent** (`agents/*.md`). Signals: "research 50 files", a parallel fan-out (the official `code-review` plugin runs five review agents at once), a narrowed/locked-down tool perimeter.
4. **Is it a repeatable, knowledge-rich workflow the *model* should auto-trigger?** → **Skill** (`skills/<name>/SKILL.md`). The default. Signals: a PR-review checklist, a changelog generator, a domain playbook the model should reach for when relevant.
5. **Is it a discrete action the *user* wants to fire by name?** → **Command** (`commands/*.md`). Signals: muscle-memory entry points, `/deploy`, `/status`.

The meta-advice the sources repeat: **start with skills (+ hooks), add MCP and agents only when the job genuinely demands them.** "Skills + MCP cover ~80% of workflows… don't try to use all six on day one. Layer up."

## Why the MCP bar is highest

An MCP server's tool definitions are paid on *every* session the plugin is enabled, before any work begins. Measured setups show standard MCP configurations consuming a majority of the context window with tool definitions alone; a five-server setup can burn tens of thousands of tokens before the conversation starts. So an MCP earns its place only when:

- The capability genuinely needs *external* state or actions (not just structured knowledge).
- Its tools are **task-level**, not endpoint-level. `schedule_event` (which internally searches availability *and* books) beats `search_availability` + `create_booking` + `get_calendar` chained by the model ("token arson").
- The tool count is bounded (≈≤25) and prefix-namespaced so the model can pick among them.
- Output is high-signal (the agent doesn't drown in raw API dumps).

A bundled MCP that exposes 30 endpoint-shaped tools fails component fit *and* context economy simultaneously — it is the AP-P4 "API-wrapper MCP" anti-pattern.

**Worked exemplar — the inverse of the wrapper.** The `brand-corpus` MCP in the sibling **brand-forge** plugin is a clean reference for the *good* shape: five **task-level, read-only** tools (`list_brand_documents`, `search_brand`, `fetch_brand_section`, `outline_brand_document`, `get_brand_tokens`) scoped to **one directory** via an env var and path-guarded against `..`/symlink escape. It is intent-level (`search_brand`, not `open`+`read`+`stat`), not endpoint-shaped — and it shows that an MCP need not wrap an *external* service: a curated, read-only perimeter over a **local document set** is a legitimate MCP when *retrieval is the intent*. Its language-agnostic contract is documented in `brand-forge/skills/brand-corpus/references/mcp-wiring.md`.

## Why "everything a skill" is the silent default failure

The path of least resistance is to make every capability a skill, because skills are the most flexible primitive and the recommended starting point. But two task-shapes are actively *wrong* as skills:

- **A required guarantee as a skill** — the formatter/linter/policy that "should always run" but now depends on the model remembering to invoke it. The correct shape is a hook. (AP-P3, "the hopeful guarantee.")
- **An external integration as a skill** — procedural prose that pretends to reach a live system it can't actually touch. The correct shape is an MCP (the perimeter) *plus* a skill (the procedure).

The fix is a **fit table written before the manifest**: `capability → primitive → why`. That table is both the evidence P2 scores and the skeleton the `plugin.json` follows.

## When the choice is genuinely ambiguous

Two boundaries are soft and shift with the harness version:

- **Skill vs Command.** In current Claude Code both are markdown that produces a `/name` shortcut and both can be model- or user-invoked; `commands/` is the legacy flat-file form ("use `skills/` for new plugins"). The meaningful distinction is *intended trigger*: model-decides (lean skill, rich description) vs user-types (lean command, memorable name). Pick by who should decide when it fires.
- **Hook vs Agent for verification.** A cheap deterministic check is a hook; a check that needs reasoning or tool use is a hook of `type: agent` or `type: prompt`, or a subagent. Reserve the agentic forms for genuine judgment; keep the pass/fail mechanical checks as `command`-type hooks.

## When not to over-fit

Component fit is not an excuse to use all five primitives in every plugin. A plugin that ships a hook, an MCP, two agents, six skills, and three commands "because it can" is a complexity liability (Elon's lens). Use the *fewest* primitives that the capabilities' shapes require. A pure knowledge plugin is correctly all-skills; a pure enforcement plugin is correctly all-hooks. The defect is *mismatch*, not *minimalism*.

## Implications for plugins-factory

- The `author` workflow's **first move** is the component-fit pass — the `capability → primitive → why` table — *before* the manifest, because the manifest shape follows from it (`build-against-the-standard.md` §"The component-fit decision is the first move").
- P2 in `plugins-holistic.md` carries two mechanical tests: the **guarantee test** (every must-run capability not a hook is a defect) and the **wrapper test** (a bundled MCP with >~25 tools or 1:1-endpoint shape is a wrapper).
- The critic who owns this dimension is **Huyen** (the determinism boundary: workflow vs agent, tool contracts) with **Elon** as the delete-first second lens.

## Source Citations

1. Anthropic. *Claude Code Plugins reference.* https://code.claude.com/docs/en/plugins-reference
2. Anthropic. *Claude Code Hooks reference.* https://code.claude.com/docs/en/hooks
3. Anthropic (2025). *Equipping agents for the real world with Agent Skills.* https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
4. Anthropic (2025). *Writing tools for agents.* https://www.anthropic.com/engineering/writing-tools-for-agents
5. *A Mental Model for Claude Code: Skills, Subagents, and Plugins.* https://levelup.gitconnected.com/a-mental-model-for-claude-code-skills-subagents-and-plugins-3dea9924bf05
6. *Why MCP Shouldn't Wrap an API One-to-One.* https://nordicapis.com/why-mcp-shouldnt-wrap-an-api-one-to-one/
7. *Your MCP Servers Are Eating Your Context.* https://blog.lakshminp.com/p/mcp-server-context-bloat
