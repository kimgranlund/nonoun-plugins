# Design maintenance

Read [repository guidance](../../AGENTS.md) first. This plugin ships design skills for Claude Code and Codex, and designer agents for Claude Code only. It has no hooks, MCP services, model mapping, or SDLC dependency.

## Skills

| Skill | Owns |
|---|---|
| `ui-colors` | HCT source palettes, ramps, Primes and balanced color sets, and a full light/dark color system (APCA-placed ramps, roles including a pressed solid, presets). Synced from the MacBook copy at `e9ff385` |
| `ui-geometry` | UI geometry derived from one font size and unit across four tiers, measured archetypes with dials, and fitting an existing project to the nearest system and archetype. Synced from the MacBook copy at `ec93828`; `agents/openai.yaml` is repo-only |
| `ui-materials` | Painting UI parts in any material (flat, physical, frosted glass, glass, outline or a mix) from layer, relief and face, and components that render in all of them. Synced from the MacBook copy at `59d4f4b` |
| `ui-content` | Printing values and labels so they read and line up: tabular figures, true minus, units, fixed value widths, time formats, terse labels. Synced from the MacBook copy at `f0bf8a6` |
| `ui-interaction-dev` | UI interactions that work for every input: drag and drop, keyboard alternatives, live regions, focus, target sizes, dialogs and popups, from a rule spec with tests. Synced from the MacBook copy at `ba2f4c4` |
| `ui-frameworks` | Creating a UI kit in a project: light-DOM custom elements (or React) with plain CSS recipes over the WAI-ARIA APG patterns, tokens from ui-colors, ui-geometry and ui-materials. Synced from the MacBook copy at `97eee29`; differs from source: sibling lookup, T-0862 (`scripts/siblings.mjs` tries `SKILLS_DIR`, then the plugin's `skills/`, then `~/.claude/skills`; keep it on the next sync) |
| `explore-variants` | One published page of answers that differ in kind to one open question (a UI layout, an architecture, a strategy, a creative direction, a review of what was built), each shown as the thing itself under a shared fixture and stress, with a comparison, a recommendation and per-variant feedback; `references/` holds one recipe per subject. Formerly `ui-explore-variants`. Synced from the MacBook copy at `8ab4c62` |
| `ui-showcase-bento` | Bento showcases: a fixed canvas of labelled groups and specimens packed to fit, from UI skills, frameworks or brands, with an in-page checker. Imported from the MacBook copy at `f3fbd78` |
| `ui-kit-inspector` | Jigs: live panels that tune a UI system's constants and export a change set; `examples/inspector-panel/` holds the former `inspector-panels` skill |
| `component-variants` | Interactive comparison pages for component implementation alternatives |
| `wireframe-review` | Interactive wireframes with alternatives, annotations and JSON feedback |
| `design-crit` | Four-reviewer critique of interfaces, workflows and wireframes |
| `make-figma-agent-connector` | Claude Code only: brings up the local figma-bridge and its Figma connector values |

## Agents

Claude Code only: Claude Code finds them in `agents/` and names them `design:<name>`; Codex has no design agents. Each is a design director formed by one designer's principles, method and context: it sets direction, makes and reviews visual artifacts (websites, documents, reports, dashboards, decks, interfaces, demos) and critiques work through that designer's thinking. Imported unchanged from the MacBook share (`~/.claude/agents/`, files dated 2026-11-23); keep them identical to the source on the next sync. Their `model: opus` line is a user decision.

| Agent | Use when the user wants work directed through |
|---|---|
| `dieter-rams` | Dieter Rams |
| `ive-newson` | Jony Ive and Marc Newson |
| `jan-tschichold` | Jan Tschichold |
| `john-maeda` | John Maeda |
| `karl-gerstner` | Karl Gerstner |
| `le-corbusier` | Le Corbusier |
| `max-bill` | Max Bill |
| `muller-brockmann` | Josef Müller-Brockmann |
| `muriel-cooper` | Muriel Cooper |
| `naoto-fukasawa` | Naoto Fukasawa |
| `wim-crouwel` | Wim Crouwel |

## Rules

- Skills reach each other by relative paths inside `skills/`, so the plugin ships them together. `component-variants`, `wireframe-review` (`scripts/generate-geometry.mjs`) and the inspector panel read `ui-geometry/scripts/derive.mjs`; moving a skill breaks them.
- A skill in another plugin is named, never linked: write `dev-tools:closed-loop-run` and the page inside it, not a `../` path that leaves this plugin.
- `component-variants` (`assets/kit/`) and `wireframe-review` (`scripts/kit.mjs`) ship their own trimmed kits and have no lock.
- Keep `make-figma-agent-connector` script paths under `${CLAUDE_PLUGIN_ROOT}`, never a user-level skills folder.
- Dated evidence trees (`resources/reports/`) stay out of the plugin; record new evidence in `docs/reports/`.
- Model, effort and permission lines in the skills are user decisions; keep them as they are.

## Checks

From the repository root: `python3 scripts/check-packaging.py` (catalogs, manifests, skill names and sizes, cross-skill links). Inside `skills/ui-colors`: `node scripts/check.mjs`. Inside `skills/ui-geometry`: `node --test`. Inside `skills/ui-materials` and `skills/ui-content`: `node scripts/check.mjs`. Inside `skills/ui-interaction-dev` and `skills/ui-showcase-bento`: `node --test` (their SKILL.md says `node --test scripts/`, which Node 24 rejects as a module path). Inside `skills/ui-frameworks`: `node scripts/manifests.mjs --check` and `node scripts/lint-recipes.mjs`. Inside `skills/wireframe-review`: `node scripts/generate-geometry.mjs --check` and `node scripts/selftest.mjs`. Inside `skills/ui-kit-inspector/examples/inspector-panel`: `npm test` (Node 24 or later).

The two browser checks need Playwright, which the repository does not track. Make a throwaway project outside the repository (`mkdir <scratch> && cd <scratch> && npm init -y && npm i playwright && npx playwright install chromium webkit`; this needs the network). Inside `skills/explore-variants`: `node scripts/check.mjs <scratch>` (Chromium and WebKit; pass `chromium` as a second argument for one engine). Inside `skills/ui-kit-inspector/examples/inspector-panel`: serve the folder (`python3 -m http.server 8000`), then `PLAYWRIGHT_MODULE=<scratch>/node_modules/playwright-core/index.mjs node examples/test.mjs http://localhost:8000/examples/demo.html <scratch>/out`.

Run `git diff --check` for doc edits.
