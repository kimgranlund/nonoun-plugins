---
date: 2026-06-02
status: draft
coverage: canonical
version: "0.1.0"
primary_sources:
  - "Anthropic. Customize Claude Code with plugins (toggle to reduce system-prompt context). claude.com/blog/claude-code-plugins"
  - "Anthropic. Claude Code Plugins reference (claude plugin details: always-on vs on-invoke token cost). code.claude.com/docs/en/plugins-reference"
  - "Anthropic. Agent Skills best practices (progressive disclosure: SKILL.md <500 lines as TOC; references one level deep; scripts don't load into context). platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices"
  - "Anthropic (2025). Equipping agents for the real world with Agent Skills (three-tier disclosure). anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills"
  - "Your MCP Servers Are Eating Your Context (tool defs consume the majority of the window before work begins). blog.lakshminp.com"
  - "VS Code. Activation events (lazy activation; load resources only when needed). code.visualstudio.com/api/references/activation-events"
---

# Context Economy — Foundational Knowledge Document

The theory behind P6: every enabled plugin pays a standing context tax on every session, whether or not its capabilities are used. A good plugin keeps that tax minimal and pushes detail behind load-on-demand boundaries — so it is worth leaving enabled.

## The Core Claim

Context is the budget every install spends. The official model is explicit: plugins "toggle on and off as needed… to reduce system prompt context and complexity." That framing only works if a plugin's _standing_ cost — what it adds to every session merely by being enabled — is small. The tooling makes the cost legible: `claude plugin details` reports two numbers, **always-on** (component names + descriptions + MCP tool definitions, paid every session) and **on-invoke** (the body of a skill/agent, paid only when it fires). A well-designed plugin minimizes the first and lets the second be as rich as the work demands.

The design goal: **lean always-on, rich on-invoke.** A user should be able to leave the plugin enabled without it degrading unrelated sessions. The failure is a plugin whose standing cost is high enough that users toggle it off between uses — which defeats the entire point of a shareable, always-available capability.

## The two costs and what drives them

| Cost | Paid | Driven by |
| --- | --- | --- |
| **Always-on** | every session the plugin is enabled | skill/command **descriptions** (one or two lines each), agent descriptions, and — the big one — **MCP tool definitions** |
| **On-invoke** | only when a component fires | the body of the SKILL.md, the loaded reference files, the agent's system prompt |

The single largest always-on driver is a bundled **MCP server**. Measured setups show MCP tool definitions consuming a majority of the context window before any work begins; a multi-server setup can burn tens of thousands of tokens at startup. This is why P2 (component fit) and P6 (context economy) are linked: an API-wrapper MCP with 30 endpoint tools fails both at once. An MCP earns its standing cost only when the capability genuinely needs external state and its tool set is consolidated and bounded.

The second driver is **verbose descriptions**. A description is the routing surface (it must state what + when with trigger terms), but it is also always-on context. Terse, specific descriptions route well _and_ cost little; padded ones tax every session for no routing benefit.

## Progressive disclosure is the on-invoke discipline

The richness lives behind the on-invoke boundary, governed by progressive disclosure — the three-tier model from Anthropic's skill guidance:

1. Only `name` + `description` is pre-loaded (always-on).
2. The SKILL.md body loads when the skill becomes relevant (on-invoke).
3. Bundled reference files load only when the model reads them (on-demand).

The concrete rules that keep tier 2/3 lean:

- **SKILL.md under ~500 lines, acting as a table of contents** that points to detail, not the detail itself.
- **References domain-partitioned and one level deep** from SKILL.md. Deeply nested references cause partial reads (the model `head`s a file and misses content); a reference >100 lines should carry its own TOC.
- **Deterministic logic in scripts, not prose** — "when Claude runs a script, the script's code never loads into the context window; only its output consumes tokens." A bundled validator is free context until it runs.
- **No context penalty for large bundled files until accessed** — complete API docs, datasets, examples can all ship, because they cost nothing until read. Comprehensiveness and leanness are not in tension when structured this way.

A plugin whose bundled skills follow these rules has a low on-invoke cost _per fire_ and a near-zero standing cost. A plugin that front-loads reference content into SKILL.md, or stuffs standing knowledge into descriptions, pays for everything all the time.

## The plugin-CLAUDE.md trap

A subtle always-on mistake: authors expect a plugin-root `CLAUDE.md` to carry standing instructions. It is **not loaded** as context — so it costs nothing, but it also does nothing. Instructions that must reach the model belong in a skill (where they're disclosed on-invoke), not in a file that's silently ignored. This is the inverse of bloat: a place authors _think_ they're paying context and getting value, when they're getting neither.

## Lazy activation is the same idea, ecosystem-wide

VS Code's activation-event system is the mature-ecosystem analogue: "use the most specific activation events possible… the `*` event activates on startup, which can impact performance, so use it sparingly," and "load additional resources only when needed." The principle is universal — an extension/plugin should cost the host nothing until the moment its capability is actually needed. Progressive disclosure is Claude Code's version of lazy activation.

## When always-on cost is justified

Lean does not mean empty. Some always-on cost is the price of discoverability: a plugin's skills _must_ carry descriptions for the router to find them. The judgment is whether the standing cost is _proportional to and in service of_ the capability:

- A handful of terse, specific skill descriptions — justified (that's the routing surface).
- A bundled MCP whose external-state capability is the plugin's whole point, with consolidated tools — justified, even though it's the costliest.
- An MCP bundled "in case," 1:1-wrapping an API the plugin doesn't centrally need — not justified.
- Padded descriptions, front-loaded references, a mega-SKILL.md — not justified.

## The empirical signal (a hypothesis to track)

The real test of context economy is behavioral: **do users leave the plugin enabled by default, or toggle it off between uses?** A plugin cheap enough to leave on is paying an acceptable tax; one users disable to reclaim context is not. This is a `[hypothesis]` dimension — measure it with install/disable telemetry and `plugin details` cost where available, rather than asserting it.

## Implications for plugins-factory

- P6's mechanical proxy is the **always-on audit**: read `claude plugin details` (or the planned `context-cost.py`) and check whether anything other than terse descriptions dominates the always-on number. An MCP's tool defs or verbose descriptions dominating = a context-economy failure.
- The `[hypothesis]` sub-dimension (stays-enabled-by-default) is explicitly unverified in v0.1 — tracked for calibration, not asserted.
- Owning critics: **Boris** (vanilla > ceremony; the standing-cost discipline) and **Karpathy** (is the cost actually paying for verifiable capability?).

## Source Citations

1. Anthropic. _Customize Claude Code with plugins._ <https://claude.com/blog/claude-code-plugins>
2. Anthropic. _Claude Code Plugins reference._ <https://code.claude.com/docs/en/plugins-reference>
3. Anthropic. _Agent Skills best practices._ <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
4. Anthropic (2025). _Equipping agents for the real world with Agent Skills._ <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
5. _Your MCP Servers Are Eating Your Context._ <https://blog.lakshminp.com/p/mcp-server-context-bloat>
6. VS Code. _Activation Events._ <https://code.visualstudio.com/api/references/activation-events>
