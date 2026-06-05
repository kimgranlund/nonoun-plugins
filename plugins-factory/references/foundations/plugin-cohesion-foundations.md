---
date: 2026-06-02
status: draft
coverage: canonical
version: "0.1.0"
primary_sources:
  - "Anthropic. Customize Claude Code with plugins (toggle on/off to reduce context; five use cases). claude.com/blog/claude-code-plugins"
  - "Anthropic. anthropics/claude-code plugins README (reference plugins bundle by workflow: code-review, feature-dev, plugin-dev). github.com/anthropics/claude-code"
  - "ComposioHQ. awesome-claude-plugins (functional-domain taxonomy; focused domain problems, not cross-cutting concerns). github.com/ComposioHQ/awesome-claude-plugins"
  - "Backstage. The monolithic plugin problem / everything-is-a-plugin. infoq.com/presentations/backstage-plugin"
  - "VS Code. Activation events (most-specific activation; * is expensive). code.visualstudio.com/api/references/activation-events"
  - "ESLint. Shareable configs (multiple entry points in one package). eslint.org/docs/latest/extend/shareable-configs"
  - "Obsidian. Plugin guidelines (single-purpose; avoid duplication). docs.obsidian.md/Plugins/Releasing/Plugin+guidelines"
---

# Plugin Cohesion — Foundational Knowledge Document

The theory behind P3: a plugin's scope is bounded on _both_ sides. Too broad taxes every install; too narrow scatters one workflow across fragments. The target is one coherent job with rich internal granularity.

## The Core Claim

Cohesion is the property that a plugin does **one coherent job**, and every component in it serves that job. It is the most-cited design principle across every mature plugin ecosystem, and it is bounded on two sides:

- **Upper bound — the kitchen sink.** A plugin scoped to "all our team's tooling" imposes a per-session tax on everyone who installs it (its standing context is always-on) and a "which capability do I reach for?" routing tax on the model. Backstage names this directly as "the monolithic plugin problem." VS Code's entire activation-event system exists to mitigate the cost of broad extensions ("the `*` event activates on startup… use it sparingly").
- **Lower bound — the fragment.** Splitting one coherent workflow across several plugins forces users to discover, install, enable, and version-coordinate pieces that only work together. It defeats the point of a plugin (consistent, shareable tooling) and creates hidden cross-plugin coupling.

The official framing is a toggle: plugins "are designed to toggle on and off as needed… enable them when you need specific capabilities and disable them when you don't to reduce system prompt context." A plugin earns its boundary when a user would enable/disable _the whole set_ as one coherent capability. That is the cohesion test.

## The unit of cohesion is the job-to-be-done, not the org chart

Anthropic's own reference plugins demonstrate the pattern: `code-review` bundles one command + five parallel review agents; `feature-dev` ships a command + `code-explorer`/`code-architect`/`code-reviewer` agents around one structured workflow; `plugin-dev` bundles a command + 3 agents + 7 skills _all about plugin development_. The unifying thread is never component count — it is **one coherent job-to-be-done**. A good plugin's job fits one sentence: "Deployment automation tools," "Dependency analysis for Claude Code sessions."

The Composio marketplace taxonomy makes the same point at the catalog level: plugins are organized into functional domains, and "this taxonomy suggests plugins should solve focused domain problems rather than cross-cutting concerns." Cohere around a domain; resist cross-cutting scope.

## Internal granularity ≠ external fragmentation

The most important nuance: **ship rich internal granularity inside one cohesive plugin, rather than fragmenting into many micro-plugins.** ESLint gives the cleanest version — because a shareable config is just a package, "you can export as many configs as you'd like from the same package." The translation to plugins: prefer several well-named skills (and agents, and a hook) _inside_ one domain plugin over a constellation of one-skill plugins the user must assemble. The _plugin_ boundary is the domain; the _internal_ structure can be as granular as the work demands.

This dissolves the apparent tension between cohesion and completeness. A `design-system` plugin can bundle 25 skills and still be perfectly cohesive — because all 25 serve the one job "turn brand intent into a production design system." The defect would be bundling those 25 _plus_ an accounting skill _plus_ a repo-audit skill: now three jobs share a directory.

## The discriminating tests

Two questions separate a coherent boundary from a defective one:

1. **The split test (catches kitchen sinks):** would a user ever want _exactly half_ of this plugin and none of the other half? If yes — if a meaningful population wants the design-tokens half but never the brand-strategy half — those are two plugins. Generation, serialization, reference, diagnosis, and strategy are genuinely different toggles even within one domain.
2. **The merge test (catches fragments):** does this plugin _only function_ when a specific sibling is also enabled, with that requirement undeclared? If yes, it's a fragment — either declare the `dependencies` edge or merge it back into one coherent plugin.

The `dependencies` mechanism is the release valve for _genuinely_ separable concerns: two plugins each independently useful, one building on the other. Use it when both halves stand alone, not to paper over an over-fragmented design.

## Cohesion and context cost are linked

A kitchen-sink plugin fails cohesion (P3) and context economy (P6) together: its breadth is exactly what makes its always-on cost high. This is why "scope a plugin so a user can reason about, and toggle, a coherent capability set without paying for unrelated context" is one principle, not two. The toggle is the user-facing manifestation of cohesion.

## When a "plugin" shouldn't exist at all

Cohesion's degenerate case: a "plugin" that is one skill which should never have been split out. If the capability is a single skill, has no share/version/reuse story distinct from the library it lives in, and bundles nothing else — it's a standalone skill, not a plugin (this is P1's territory). Over-fragmentation at the limit produces plugins that are emptier than the packaging overhead they carry.

## Implications for plugins-factory

- The `carve` mode's step 5 (`carve-method.md`) is the granularity decision: cluster by job, avoid both poles, ship internal granularity inside domain plugins.
- P3's mechanical test in `plugins-holistic.md` is the split/merge test; P1 catches the "shouldn't be a plugin at all" degenerate case.
- The five-way design-family split in the carve proposal (`design-system` / `design-tokens` / `design-knowledge` / `design-review` / `brand-forge`) is the worked example: looks like fragmentation, is actually five distinct jobs each independently useful — the split test passes for each.
- Owning critic: **Steve Y.** (platform vs product, the granularity and namespacing call).

## Source Citations

1. Anthropic. _Customize Claude Code with plugins._ <https://claude.com/blog/claude-code-plugins>
2. Anthropic. _anthropics/claude-code — plugins/README.md._ <https://github.com/anthropics/claude-code/blob/main/plugins/README.md>
3. ComposioHQ. _awesome-claude-plugins._ <https://github.com/ComposioHQ/awesome-claude-plugins>
4. InfoQ. _Backstage: Everything is a Plugin._ <https://www.infoq.com/presentations/backstage-plugin/>
5. VS Code. _Activation Events._ <https://code.visualstudio.com/api/references/activation-events>
6. ESLint. _Shareable Configs._ <https://eslint.org/docs/latest/extend/shareable-configs>
7. Obsidian. _Plugin Guidelines._ <https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines>
