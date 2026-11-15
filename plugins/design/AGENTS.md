# Design maintenance

Read [repository guidance](../../AGENTS.md) first. This plugin ships design skills for Claude Code and Codex. It has no hooks, MCP services, native agents, model mapping, or SDLC dependency.

## Skills

| Skill | Owns |
|---|---|
| `ui-colors` | HCT source palettes, ramps, Primes and balanced color sets, and a full light/dark color system (APCA-placed ramps, roles including a pressed solid, presets). Synced from the MacBook copy at `e9ff385` |
| `ui-geometry` | UI geometry derived from one font size and unit across four tiers, measured archetypes with dials, and fitting an existing project to the nearest system and archetype. Synced from the MacBook copy at `62d0cda`; `agents/openai.yaml` is repo-only |
| `ui-materials` | Painting UI parts in any material (flat, physical, frosted glass, glass, outline or a mix) from layer, relief and face, and components that render in all of them. Imported from the MacBook copy at `ec1743a` |
| `ui-content` | Printing values and labels so they read and line up: tabular figures, true minus, units, fixed value widths, time formats, terse labels. Imported from the MacBook copy at `1aafd92` |
| `ui-interaction-dev` | UI interactions that work for every input: drag and drop, keyboard alternatives, live regions, focus, target sizes, dialogs and popups, from a rule spec with tests. Imported from the MacBook copy at `de8f3a9` |
| `ui-frameworks` | Creating a UI kit in a project: light-DOM custom elements (or React) with plain CSS recipes over the WAI-ARIA APG patterns, tokens from ui-colors, ui-geometry and ui-materials. Imported from the MacBook copy (no git) |
| `ui-explore-variants` | One published page of coarsely distinct layout or interaction solutions under a shared fixture and stress control, with a comparison, a recommendation and per-variant feedback. Imported from the MacBook copy at `c7d3ac9` |
| `ui-showcase-bento` | Bento showcases: a fixed canvas of labelled groups and specimens packed to fit, from UI skills, frameworks or brands, with an in-page checker. Imported from the MacBook copy at `f3fbd78` |
| `ui-kit-inspector` | Jigs: live panels that tune a UI system's constants and export a change set; `examples/inspector-panel/` holds the former `inspector-panels` skill |
| `component-variants` | Interactive comparison pages for component implementation alternatives |
| `wireframe-review` | Interactive wireframes with alternatives, annotations and JSON feedback |
| `design-crit` | Four-reviewer critique of interfaces, workflows and wireframes |
| `make-figma-agent-connector` | Claude Code only: brings up the local figma-bridge and its Figma connector values |

## Rules

- Skills reach each other by relative paths inside `skills/`, so the plugin ships them together. `component-variants`, `wireframe-review` (`scripts/generate-geometry.mjs`) and the inspector panel read `ui-geometry/scripts/derive.mjs`; moving a skill breaks them.
- A skill in another plugin is named, never linked: write `dev-tools:closed-loop-run` and the page inside it, not a `../` path that leaves this plugin.
- `component-variants` (`assets/kit/`) and `wireframe-review` (`scripts/kit.mjs`) ship their own trimmed kits and have no lock.
- Keep `make-figma-agent-connector` script paths under `${CLAUDE_PLUGIN_ROOT}`, never a user-level skills folder.
- Dated evidence trees (`resources/reports/`) stay out of the plugin; record new evidence in `docs/reports/`.
- Model, effort and permission lines in the skills are user decisions; keep them as they are.

## Checks

From the repository root: `python3 scripts/check-packaging.py` (catalogs, manifests, skill names and sizes, cross-skill links). Inside `skills/ui-colors`: `node scripts/check.mjs`. Inside `skills/ui-geometry`: `node --test`. Inside `skills/ui-materials`: `node scripts/check.mjs`. Inside `skills/ui-interaction-dev` and `skills/ui-showcase-bento`: `node --test` (their SKILL.md says `node --test scripts/`, which Node 24 rejects as a module path). Inside `skills/ui-frameworks`: `node scripts/manifests.mjs --check` and `node scripts/lint-recipes.mjs`. Inside `skills/wireframe-review`: `node scripts/generate-geometry.mjs --check` and `node scripts/selftest.mjs`. Inside `skills/ui-kit-inspector/examples/inspector-panel`: `npm test` (Node 24 or later). Run `git diff --check` for doc edits.
