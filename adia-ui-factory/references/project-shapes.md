---
name: project-shapes
load-when: classifying or laying out an adia-ui app's structure — picking the project shape, the four-axis layout, or page-trio vs page-DUO
load-size: ~2.5k tokens
required-for: [adia-ui-factory shape classifier, adia-ui-project (scaffold / add-surface / add-page)]
---

# Project shapes & structure

How real adia-ui apps are laid out (synthesized from the chat-ui apps). Three shapes over one four-axis layout, with a page-trio/DUO rule. The **structure rubric** at the bottom is the gate; `bin/adia-scaffold` mechanizes the layout.

## The four-axis layout (all shapes)

```
<app>/
├── README.md · PATTERNS.md · CHANGELOG.md   # entry + non-obvious patterns + history
├── spec/     design — BRIEF · ARCHITECTURE · SPEC (+ per-screen specs)
├── plan/     execution — ROADMAP · MILESTONES · PLAN
├── skills/   procedural knowledge — <app>-expert/ (optional)
└── app/      runnable source (shape-specific below)
```

Keep the axes separate: `spec/` is the contract, `plan/` the sequence, `app/` the build, `skills/` the app's own expertise. The design/plan docs are not optional scaffolding noise — they're how a surface stays traceable to intent.

## The three shapes

### Single-surface — one entry, one surface
One `app/<name>.html` + its contents + a controller; reactive state via signals, often Service/Controller/Command for mutations/undo.
```
app/
├── index.html · <name>.css
├── components/<tag>/<tag>.{js,css}
├── controller/ · service/ · state/   # if it has real domain logic
└── seed-data.js
```
Use for: a focused tool/widget (a board, a canvas, an embedded panel).

### Rollup — many sibling sub-pages under one app
Each sub-page is a page-trio or page-DUO; a uniform (or per-subflow) shell template loads it. Three flavors:
- **heterogeneous** — independent playgrounds, each its own chrome + logic; shared bits in `app/_shared/`.
- **homogeneous** — uniform template, fixtures per page, property-API wiring (often `admin-shell`).
- **declarative-DUO** — mostly static flows (auth/onboarding), per-subflow chrome, few controllers.
```
app/
├── _shared/                         # cross-page helpers (heterogeneous)
└── <sub>/<sub>.{html,contents.html[,contents.js]}
```
Use for: a suite of related surfaces (a SaaS admin, a flow set, a demo gallery).

### Shared-foundation — sibling apps over a shared core
Root-level `spec/plan/` for cross-app concerns; each app under `app/<name>/` with its own `spec/plan/src/`; a shared `app/shared/` (DataClient, loaders, mappers, tokens). The embed pattern lives here → becomes **`adia-embed-shell`**.
```
app/
├── shared/                          # DataClient · corpus/mappers · components · tokens
└── <surface>/{spec,plan,src}/       # one per embedded surface
```
Use for: multiple embedded surfaces sharing data context, components, and an embed bridge.

## Page-trio vs page-DUO

| Form | Files | When |
|---|---|---|
| **trio** | `<page>.html` + `<page>.contents.html` + `<page>.contents.js` (`export default setup(host)`) | the surface needs **behavior or property-API wiring** (events, `.columns=…`, streaming) |
| **DUO** | `<page>.html` + `<page>.contents.html` | the surface is **purely declarative** (static markup, CSS-only state) |

The `.html` shell fetches `.contents.html`, injects it, then dynamically imports `.contents.js` if present. **Rule:** add `.contents.js` only when there's behavior to wire — a DUO with a dead `.contents.js` and a trio missing its setup are both smells.

## State & data — which pattern (depth: `adia-ui-data`)

`signal()`/`effect()` (single-surface reactivity) · Service/Controller/Command (mutations + undo) · `DataClient.read(projection)` + pure mappers, with **`action_source` required on every `mutate`** (shared-foundation) · property-API (`el.columns = […]`, never post-connect `<option>` children) · declarative `data-*` (static flows). The data skill owns the choice; this is the map.

## Components

One folder per tag, mirroring the framework: `components/<tag>/<tag>.{js,css}` (folder name = custom-element tag). Authoring discipline: `authoring-components.md`.

## Structure rubric `[gate]`

A project is well-structured when (gate = all `[gate]` hold):
- **Four-axis present** `[gate]` — `spec/` + `plan/` + `app/` (skills/ optional).
- **Shape declared & matched** `[gate]` — the layout matches one of the three shapes; no half-rollup.
- **Page form correct** `[gate]` — every surface is trio or DUO per the rule; a DUO carries no `.contents.js`; a trio's `.contents.js` exports `setup`.
- **Components foldered** `[gate]` — every custom element is `components/<tag>/<tag>.{js,css}`.
- **No duplicated cross-surface code** `[review]` — shared logic lives in `app/shared/` (or `_shared/`), not copied per page.

Verify target for a scaffold/edit: this rubric passes, and any new surface renders through `adia-ui-verify`.
