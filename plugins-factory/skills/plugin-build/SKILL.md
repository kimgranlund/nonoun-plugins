---
name: plugin-build
description: >
  Build Claude Code plugins — author a new plugin from intent, carve a skill library into plugin
  boundaries, or edit an existing plugin. Runs the component-fit pass (each capability → its right
  primitive: skill / agent / command / hook / MCP), wires plugin.json + the marketplace entry
  against the 9-dimension architecture standard, validates with validate_plugin.py, and red-teams
  the draft with the critic council. Triggers on "package this into a plugin", "author a plugin",
  "what plugins should these skills become", "carve this library", "fix my plugin", "wire
  plugin.json". NOT for scoring/auditing an existing plugin (use plugin-evaluate), one skill's
  content (skills-studio), library restructuring (skills-refactor), or MCP-internal tool design
  (core-mcp-best-practices).
---

# plugin-build — the maker

The builder seat of the studio. Where `plugin-evaluate` **judges**, this skill **produces** — and it produces *against the same standard it will be judged by*. You do not author to a separate template and then get scored; you build against the same rubric library, foundations, and critics that `score` and `critique` use. That bi-directionality is the whole point.

This file is a table of contents. The depth lives in the shared spine under `${CLAUDE_PLUGIN_ROOT}/references/`, loaded on demand.

## First principles

1. **The plugin is the packaging unit; the component is the capability unit.** Scope a plugin by "what do I toggle together," not "what is one feature." It earns its boundary when a user enables/disables the whole set as one coherent capability — and pays its standing context cost only while on.
2. **Component fit is the crux, and the wrong primitive is the most common defect.** A **hook** for what must run deterministically on an event, an **MCP** for an external/stateful perimeter, an **agent** for context-isolation or parallel fan-out, a **skill** for model-auto-invoked knowledge, a **command** for a user-named action.
3. **Shared infrastructure must survive the install boundary.** Installed plugins are copied into a version-keyed cache and **cannot reference files outside their own directory** — a `../shared` path or cross-plugin `$ref` *breaks at install*. Resolve shared infra by co-location, `dependencies:`, or same-marketplace symlink — never `..`.
4. **Cohesion is bounded on both sides** — neither kitchen-sink nor fragment. Ship internal granularity (many well-named skills) inside *one* domain plugin.
5. **A plugin executes arbitrary code with the user's privileges.** A hook fires on your events, a bundled MCP starts on enable, a `bin/` joins your PATH. Security is a first-class dimension — document every hook's side-effect, scope bundled MCPs, never let a bundled agent hold the lethal trifecta.

## The component-fit decision is the first move, not the last

Unlike a skill (one primitive), a plugin's central authoring act is **assigning each capability to a primitive** — *before* writing the manifest, because the manifest shape follows from it. Write the fit table first (`capability → primitive → why`). That table **is** P2's evidence and the skeleton of the `plugin.json`:

- must **run** on an event (lint, format, policy, notify)? → **hook** (`hooks/hooks.json`)
- touches an **external/stateful system**? → **MCP** (`.mcp.json`), intent-level tools only
- needs **context isolation or parallel fan-out**? → **agent** (`agents/*.md`)
- **model-auto-invoked** knowledge/workflow? → **skill** (`skills/*/SKILL.md`)
- a **user-named** explicit action? → **command** (`commands/*.md`)

## The three sub-modes

**Build against the standard — read `${CLAUDE_PLUGIN_ROOT}/references/authoring/build-against-the-standard.md` first.** It maps each holistic dimension (P1–P9) to the foundation you build it from, the rubric it gets scored with, the ship-gate the plugin must pass, and the critic who will try to break it.

| Sub-mode | What it does | Read |
|---|---|---|
| `author` | New plugin: intent → component-fit pass → boundary check → wire `plugin.json` + marketplace entry → `validate_plugin.py` → build-time red-team → package | `build-against-the-standard.md` + `creating-plugins.md` + `plugin-template.md` |
| `carve` | A skill library → a plugin-boundary proposal: map the real composition graph, cluster by domain, resolve shared infra (co-locate / `dependencies` / symlink), flag orphans + dead components | `carve-method.md` (+ `${CLAUDE_PLUGIN_ROOT}/agents/carve-analyst.md` for the graph fan-out) |
| `edit` | Targeted fix — a mis-fit component, a kitchen-sink boundary, an illegal `../` dependency, bloated always-on context, a routing collision | `build-against-the-standard.md` + the relevant rubric |

## Ship-gates — every produced plugin must pass (each maps to a holistic dimension)

- **Component fit declared** *(P2)* — every capability's primitive named and justified; nothing must-run left as a hopeful instruction; no MCP that 1:1-wraps an API. `[gate]`
- **Manifest & layout valid** *(P5)* — passes `validate_plugin.py`: kebab `name`, `./`-relative paths with no `..`, manifest alone in `.claude-plugin/` and **all** components at the plugin root, `${CLAUDE_PLUGIN_ROOT}` for bundled scripts, persistent state only in `${CLAUDE_PLUGIN_DATA}`. `[gate]`
- **Dependency legality** *(P4)* — no cross-plugin `../` path; shared infra co-located / in `dependencies` / symlinked-in-marketplace; no dead component bundled. `[gate]`
- **Coherent, toggleable scope** *(P1, P3, P6)* — one-sentence job; every component serves it; always-on context justified. `[review]`
- **Routable + collision-free** *(P7)* — every bundled skill/command has a third-person what+when description with triggers; distinct triggers + explicit hand-offs; an explicit `/command` entry for the main workflow. `[gate]`/`[review]`
- **Security posture stated** *(P9)* — every hook's side-effect documented; bundled agents carry no `hooks`/`mcpServers`/`permissionMode` (loader rule) and no trifecta; bundled MCP scoped. `[gate]`
- **Evolution-ready** *(P8)* — semver + `CHANGELOG.md`; stable invocation names; additive growth; `validate_plugin.py` in CI. `[gate]`
- **The produced plugin does not exempt itself from its own requirements.** `[review]`

## Build-time red-team — summon the critics on your own draft

Authoring is not done at "passes `validate_plugin.py`." Run the council (`plugin-council`) on the plugin you just designed — the same panel `plugin-evaluate` uses, turned on your own output.

| When | Pass |
|---|---|
| **Every produced plugin** (floor) | `critic-simon` (hook/MCP blast radius, trust) + `critic-scott-w` (manifest correctness, illegal layout/state) |
| **Bundles a hook or MCP**, a **marketplace**, or a **multi-plugin carve** | `full-panel` (all 9) + synthesis — the shared-infra and trust lenses compound |
| **A targeted edit** | the one or two critics who own that dimension |

Fold surviving Critical/Major findings back via `edit` before packaging. That is the loop closing: **author/carve → score/critique → edit**, over one shared body of knowledge.

## §SelfAudit (before declaring done)

Built against `build-against-the-standard.md` (each live dimension grounded in its foundation); component-fit declared for every capability; `plugin.json` passes `${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py`; no `../` cross-plugin path; every hook's side-effect documented; the build-time red-team ran (Simon + Wlaschin floor, or full-panel by stakes) and surviving Critical/Major findings were folded in. **Not done** when the manifest validates but a capability uses the wrong primitive, a shared dependency uses `../`, a hook's side-effect is undocumented, or no critic ever saw the draft.

## References (the shared spine)

| File (`${CLAUDE_PLUGIN_ROOT}/references/`) | Load when |
|---|---|
| `authoring/build-against-the-standard.md` | **first** — dimension → foundation → rubric → ship-gate → critic |
| `authoring/creating-plugins.md` + `plugin-template.md` | `author` — workflow + copy-pasteable `plugin.json` / `marketplace.json` / layout |
| `carve-method.md` (+ `agents/carve-analyst.md`) | `carve` — library→plugins method + the composition-graph fan-out subagent |
| `plugin-architecture.md` | the technical model — manifest fields, components, path variables, marketplace, namespacing, scopes, validation |
| `rubrics/*.md` + `rubric-manifest.json` | the dimension you're building — `component-fit`, `boundary-cohesion`, `dependency-and-sharing`, `manifest-and-packaging`, `context-economy` (P2–P6); `cold-start-orientation`, `skills-authoring`, `skill-extensibility`, `security-and-scope-containment` (P1/P7/P8/P9, co-located) |
| `foundations/*.md` | the theory grounding a dimension you're building |

## Boundaries

- **Scoring / auditing / critiquing an existing plugin** → `plugin-evaluate`. This skill builds; that one judges.
- **Authoring or fixing one skill's content** → `skills-studio`. This skill bundles skills; it does not write them.
- **Renaming / merging / retiring skills** (the restructuring a carve recommends) → `skills-refactor`.
- **A single MCP server's tools / schemas** → `core-mcp-best-practices`. **An agent loop** → `core-agent-loops`.
