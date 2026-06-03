---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# Creating one plugin — the `author` workflow

The full path from "package this into a plugin" to a validated, red-teamed, packaged bundle. **One plugin, one coherent job.** (For *many* skills → *many* plugins, run `carve-method.md` first; it hands you a per-plugin boundary, then each plugin is authored here.)

> **Build against the standard — read `authoring/build-against-the-standard.md` first.** It maps each holistic dimension (P1–P9) to the foundation you build it from, the rubric it's scored with, the ship-gate, and the critic who'll break it. You author *as the evaluator will score* — not a separate template retrofitted after a failing scorecard. Pull each live dimension's foundation as you write that part (P2 from `../foundations/component-fit-foundations.md`, P5 from `../foundations/plugin-architecture-foundations.md`, …).

The central authoring act of a plugin is **not** writing `plugin.json`. It is **assigning each capability to a primitive** (step 2). The manifest shape *follows* from that table. Do it first.

---

## Step 1 — Capture intent: the one-sentence job + who/when

Before any file, pin three things down. If the conversation already contains the workflow ("turn this into a plugin"), extract from history first.

1. **The one-sentence job.** Write the plugin's purpose in a single sentence with no "and also…" clause. If you need two sentences, you have two plugins (P1/P3 — split before you start). *"Lint, format, and policy-gate every commit in this repo."* is one job; *"…and also scaffold new services and manage our deploys"* is three.
2. **Who installs it, and when.** A plugin is a *distribution* unit — name the installer (a teammate? every repo in the org? a public marketplace consumer?) and the trigger to enable it. If the honest answer is "just me, on this machine, once," it may not warrant a plugin at all (P1 — a bare skill might be the right shape).
3. **The components you're packaging.** The capabilities/skills going in. Note which already exist (a skill you're bundling) vs which you'll create.

Output: a one-line job statement + an installer/when note. This is P1's evidence.

---

## Step 2 — The COMPONENT-FIT pass, FIRST (before the manifest)

**Write the `capability → primitive → why` table before scaffolding anything.** This table is simultaneously P2's evidence *and* the skeleton of `plugin.json` — every row becomes a directory. Run each capability down the decision ladder:

| Ask, in order | If yes → primitive | Goes in |
|---|---|---|
| Must it **run deterministically on an event** (lint, format, policy, notify, block)? | **Hook** | `hooks/hooks.json` |
| Does it touch an **external / stateful system**? | **MCP** (intent-level tools, *not* 1:1 API wraps) | `.mcp.json` |
| Does it need **context isolation or parallel fan-out**? | **Agent** | `agents/*.md` |
| Is it **model-auto-invoked knowledge / a workflow** the model should decide to use? | **Skill** | `skills/<name>/SKILL.md` |
| Is it a **user-named explicit action**? | **Command** | `commands/*.md` |

Two rules that catch the highest-frequency defects:

- **The guarantee rule (P2)**: anything that *must always happen* regardless of model behavior is a **hook**. "Hooks guarantee execution; prompts do not." A must-run gate left as a skill or a prose instruction is the **hopeful-guarantee** anti-pattern — it runs *usually*, then one day the model skips it.
- **The wrapper rule (P2)**: an MCP is a *curated intent-level perimeter*, not an API delivery mechanism. If your MCP would expose ~30 endpoint-shaped tools (`search_availability` + `create_booking` + …), consolidate to task-level tools (`schedule_event`). >~25 tools or 1:1-with-endpoints = the **API-wrapper MCP** anti-pattern (and a P6 context tax — its tool defs are always-on).

Example table for a repo-ops plugin:

| Capability | Primitive | Why |
|---|---|---|
| Run the formatter on every edit | **hook** (`PostToolUse`) | Must always run; can't depend on the model remembering. |
| Block commits that fail policy | **hook** (`PreToolUse`, blocking) | A genuine policy gate — deterministic, blocking reserved for this. |
| Query the CI system's run status | **MCP** | External/stateful system; intent-level tool `get_ci_status`, not a wrapper. |
| "Review this PR" deep multi-file analysis | **agent** | Context isolation + parallel file reads. |
| The repo-review methodology | **skill** | Model-auto-invoked knowledge; fires when the user asks to audit. |
| "Cut a release" | **command** (`/release`) | User-named explicit action. |

That table *is* the layout: this plugin has `hooks/`, `.mcp.json`, `agents/`, `skills/`, `commands/`. Now the manifest writes itself.

---

## Step 3 — Scaffold the layout from the template

Copy the directory tree from `plugin-template.md` and create only the dirs the fit table demanded. **The two layout laws** (P5 — `validate_plugin.py` enforces them):

- `.claude-plugin/` holds **only** `plugin.json` (and `marketplace.json` if this is a marketplace root). **No component lives inside `.claude-plugin/`** — a misplaced `skills/` there silently fails to load.
- **All component dirs live at the plugin ROOT**: `skills/`, `agents/`, `commands/`, `hooks/hooks.json`, `.mcp.json`, plus any `output-styles/`, `themes/`, `monitors/`, `bin/`, `settings.json` — all root-level, all `./`-relative.

State has a law too: **persistent state goes in `${CLAUDE_PLUGIN_DATA}`, never the plugin ROOT.** The root is the version-keyed cache copy — ephemeral, replaced on update. Bundled scripts are referenced via `${CLAUDE_PLUGIN_ROOT}` (also ephemeral, fine for read-only bundled assets).

---

## Step 4 — Wire `plugin.json` + the marketplace entry

`plugin.json` lives at `.claude-plugin/plugin.json`. **`name` is the only required field** (kebab-case, matches the directory). Add what the plugin needs (see `plugin-template.md` for the annotated example): `version` (semver — *or* omit for SHA-per-commit), `description` + `keywords` (these are always-on routing surface — keep terse, P6/P7), and component-path overrides only if you're *replacing* a default location (rarely).

If the plugin ships in a marketplace, add its entry to `.claude-plugin/marketplace.json` — `name` (kebab) + `source` per plugin, under a marketplace with a `name` + `owner{name}`. **Versioning rule**: set `version` in **exactly one place** — `plugin.json` *or* the marketplace entry, not both (both = a P5/P8 finding; the `plugin.json` value wins). Don't use a reserved marketplace name.

---

## Step 5 — Resolve any shared dependency LEGALLY (P4)

If this plugin reaches anything outside its own root — a shared type registry, a sibling's schema, a shared methodology — it **cannot** use a `../` path. Installed plugins are copied alone into a version-keyed cache; `../shared-types` resolves in your repo and **breaks on install**. Three legal resolutions, in decision order:

1. **Co-locate** — if one plugin dominantly consumes a small/stable shared file, copy it inside the root. Nothing crosses the boundary.
2. **Declare in `dependencies`** — if the shared thing is plugin-worthy and consumed by ≥2 plugins: `"dependencies": [{"name":"core-types","version":"~1.0.0"}]`. The depended-on plugin installs alongside.
3. **Symlink within the marketplace** — for a *file* shared across siblings *in the same marketplace*; the symlink is dereferenced/copied at install.

Run the **install test** on every reference: *does this path resolve after the directory is copied alone into a version-keyed cache?* Any `../` outside the root, or any cross-plugin `$ref`, = a P4 break to fix now.

---

## Step 6 — Make each ship-gate TRUE as you go (not after)

Walk `build-against-the-standard.md`'s gate column and satisfy each *while building the relevant part*, not as a retrofit. The load-bearing gates:

- **P2** Component fit declared — the step-2 table exists; every must-run step is a hook; no wrapper MCP.
- **P4** Dependency legality — zero `../`; shared infra co-located / `dependencies` / symlinked; no dead component bundled.
- **P5** Manifest & layout — `validate_plugin.py` clean; manifest-only in `.claude-plugin/`; components at root; state in `${CLAUDE_PLUGIN_DATA}`.
- **P1/P3/P6** Coherent toggleable scope — one-sentence job; every component serves it; always-on cost terse and justified.
- **P7** Routable + collision-free — each bundled skill/command has a third-person *what + when* description with trigger terms; distinct triggers + explicit hand-offs between bundled skills; an explicit `/command` entry for the main workflow.
- **P9** Security posture — every hook's side-effect documented (mutates? blocks? on which events/matchers?); bundled agents carry no `hooks`/`mcpServers`/`permissionMode` (loader rule) and no lethal trifecta; bundled MCP scoped.
- **P8** Evolution-ready — semver + `CHANGELOG.md`; stable invocation names; additive growth; `validate_plugin.py` wired into CI.

---

## Step 7 — Run `${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py`

Mechanical gate for P5 (and the path-legality half of P4):

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py plugin <path>
python3 ${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py marketplace <path>   # if a marketplace root
```

Any **ERROR** = the plugin is not done. The validator checks the manifest fields, kebab `name`, `./`-relative paths with no `..`, the manifest-only-in-`.claude-plugin/` layout, components-at-root, and obvious state-in-root smells. It is the floor, not the ceiling — it cannot judge component fit, cohesion, or trust.

---

## Step 8 — Build-time red-team (summon the critics on YOUR OWN draft)

`validate_plugin.py` passing is not "done." Run `critique` on the plugin you just designed — the same panel `evaluate` uses, turned inward. Self-review relaxes the cold-read rule, not the adversarial bar: push for ≥1 Critical or document why none exists.

| When | Pass |
|---|---|
| **Every plugin, before ship (the floor)** | `critique single-critic simon` (blast radius of bundled hooks/MCP, trust posture) **+** `single-critic wlaschin` (manifest correctness, illegal layout/state). Cheap; catches the two highest-frequency failure classes. |
| **Bundles a hook or an MCP**, OR a **marketplace**, OR a **multi-plugin carve** | `critique full-panel` + synthesis — all 9 lenses. (A shared-infra P4 mistake multiplies across every plugin in a marketplace, so Simon's + Wlaschin's lenses compound.) |
| **A targeted edit** to one concern | the 1–2 critics owning that dimension (the bridge's "Red-team lens" column). |

---

## Step 9 — Fold findings + package

Fold every surviving **Critical / Major** back into the draft via `edit` (re-run the relevant gate after). That closes the loop — **author → score/critique → edit**, all in one skill over one body of knowledge. Then package: confirm `CHANGELOG.md` has an entry for this version, the marketplace entry (if any) is wired, and `validate_plugin.py` is clean one final time. The output contract: a packaged plugin folder that passes the validator *and* a build-time red-team, with every capability's primitive named and justified.

---

## Common pitfalls (the ones the gates catch)

| Pitfall | Why it's wrong | Dim |
|---|---|---|
| **Component inside `.claude-plugin/`** (e.g. `.claude-plugin/skills/`) | Only the manifest lives there; the component silently never loads. | P5 |
| **Persistent state written to the plugin ROOT** | The root is the ephemeral version-keyed cache copy — state is lost on update. Use `${CLAUDE_PLUGIN_DATA}`. | P5/P8 |
| **A `../` cross-plugin dependency path** | Resolves in the repo, **breaks on install** (cache can't reach outside the plugin dir). | P4 |
| **An API-wrapper MCP** (≈30 endpoint-shaped tools) | Not a curated perimeter; its tool defs are an always-on context tax. Consolidate to intent-level tools. | P2/P6 |
| **A hopeful guarantee** (must-run step left as a skill/prose) | "Hooks guarantee execution; prompts do not." It runs *usually*, then fails silently once. Make it a hook. | P2 |
| **`version` in two places** (`plugin.json` *and* marketplace entry) | Drift; the `plugin.json` value wins anyway. Pick one. | P5/P8 |
| **A bundled agent declaring `hooks`/`mcpServers`/`permissionMode`** | Loader rule forbids it; plugin-shipped agents can't carry those. | P9 |
| **First-person / vague bundled-skill descriptions** | Not routable; the model can't pick it. Third-person *what + when* + trigger terms. | P7 |
