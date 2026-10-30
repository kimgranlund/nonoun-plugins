# Design maintenance

Read [repository guidance](../../AGENTS.md) first. This plugin ships design skills for Claude Code and Codex. It has no hooks, MCP services, native agents, model mapping, or SDLC dependency.

## Skills

| Skill | Owns |
|---|---|
| `base-ui` | Building UI with Differential Forms components, recipes and appearance rules |
| `mathematical-design-system` | The Differential Forms geometry model, its frozen snapshot and numerical checks |
| `hct-palettes` | HCT source palettes, ramps, Primes and balanced color sets |
| `ui-kit-inspector` | Jigs: live panels that tune a UI system's constants and export a change set; `examples/inspector-panel/` holds the former `inspector-panels` skill |
| `component-variants` | Interactive comparison pages for component implementation alternatives |
| `wireframe-review` | Interactive wireframes with alternatives, annotations and JSON feedback |
| `design-crit` | Four-reviewer critique of interfaces, workflows and wireframes |
| `make-figma-agent-connector` | Claude Code only: brings up the local figma-bridge and its Figma connector values |

## Rules

- Skills reach each other by relative paths inside `skills/`, so the plugin ships them together. `base-ui`, `component-variants`, `wireframe-review` and the inspector panel read `mathematical-design-system/assets/differential-forms/` or `base-ui/scripts/` as siblings; moving a skill breaks them.
- A skill in another plugin is named, never linked: write `dev-tools:closed-loop-run` and the page inside it, not a `../` path that leaves this plugin.
- `base-ui/kit.json` seals file hashes. After any change under `skills/base-ui/`, run `node scripts/seal.mjs` there, then `node scripts/check-kit.mjs`. The `ui-kit.lock.json` files in `component-variants` and `wireframe-review` pin a base-ui identity on purpose; update them only after reviewing a kit change.
- Keep `make-figma-agent-connector` script paths under `${CLAUDE_PLUGIN_ROOT}`, never a user-level skills folder.
- Dated evidence trees (`resources/reports/`) stay out of the plugin; record new evidence in `docs/reports/`.
- Model, effort and permission lines in the skills are user decisions; keep them as they are.

## Checks

From the repository root: `python3 scripts/check-packaging.py` (catalogs, manifests, skill names and sizes, cross-skill links). Inside `skills/base-ui`: `node scripts/check-kit.mjs`. Inside `skills/mathematical-design-system`: `node scripts/check-geometry.mjs` and `node scripts/check-curvature.mjs`. Inside `skills/ui-kit-inspector/examples/inspector-panel`: `npm test` (Node 24 or later). Run `git diff --check` for doc edits.
