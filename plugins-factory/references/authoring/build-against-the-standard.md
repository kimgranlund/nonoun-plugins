# Build against the standard — the bi-directional bridge

**The point of `plugins-factory`: the same knowledge powers building _and_ evaluating a plugin.** When you `author` (or `carve`) you are not following a separate template and _then_ getting it scored — you build it **against the same rubric library, foundations, and critics** that `score` and `critique` use to judge it. This file is the bridge: for each holistic dimension it names what you **build from**, what it gets **scored with**, the **ship-gate** the produced plugin must pass, and the **critic** who will try to break it.

Read this at the start of any `author`, `carve`, or `edit` job. It turns "author a plugin → then evaluate it" (a hand-off) into "author _as_ an evaluator would score it" (a shared standard).

## The 9-dimension bridge

The spine is `../rubrics/plugins-holistic.md` (P1–P9). For each dimension:

| Dim | Build it from (foundation) | Score it with (rubric) | Ship-gate the produced plugin must pass | Red-team lens |
| --- | --- | --- | --- | --- |
| **P1** Plugin Fitness & Scope | _(composite — no dedicated foundation)_ | `../rubrics/cold-start-orientation.md` _(co-located)_ + `../rubrics/boundary-cohesion.md` | exists to share/version/reuse (not a personal one-off, not better as a bare skill/MCP); job is one sentence; every component serves it | Elon |
| **P2** Component Fit | `../foundations/component-fit-foundations.md` | `../rubrics/component-fit.md` | each capability's primitive named + justified against the ladder; every must-run step is a hook; no 1:1-API-wrapper MCP | Huyen / Elon |
| **P3** Boundary Cohesion | `../foundations/plugin-cohesion-foundations.md` | `../rubrics/boundary-cohesion.md` | one coherent domain; internal granularity inside one job; not kitchen-sink, not fragment-of-a-workflow | Steve |
| **P4** Dependency & Shared-Infra Legality | `../foundations/dependency-and-sharing-foundations.md` | `../rubrics/dependency-and-sharing.md` | **zero `../` cross-plugin paths**; shared infra co-located / in `dependencies` / symlinked-in-marketplace; no dead component bundled | Wlaschin / Simon |
| **P5** Manifest & Packaging Correctness | `../foundations/plugin-architecture-foundations.md` | `../rubrics/manifest-and-packaging.md` | `validate_plugin.py` clean: kebab `name`, `./`-relative paths, components at root, `${CLAUDE_PLUGIN_ROOT}`, state in `${CLAUDE_PLUGIN_DATA}` | Farley / Wlaschin |
| **P6** Context Economy | `../foundations/context-economy-foundations.md` | `../rubrics/context-economy.md` | always-on cost minimal + justified; bundled skills use progressive disclosure; detail lives on-invoke | Boris / Karpathy |
| **P7** Routing & Discoverability | _(composite — no dedicated foundation)_ | `../rubrics/skills-authoring.md` _(co-located, D1–D2)_ | every bundled skill/command has third-person what+when + triggers; no intra-bundle collision; an explicit `/command` entry | Boris |
| **P8** Evolution & Maintenance | _(composite — no dedicated foundation)_ | `../rubrics/skill-extensibility.md` _(co-located)_ | semver + `CHANGELOG`; stable invocation names; additive growth; state in `${CLAUDE_PLUGIN_DATA}`; `validate_plugin.py` in CI | Steve / Farley |
| **P9** Security & Trust | _(composite — no dedicated foundation)_ | `../rubrics/security-and-scope-containment.md` _(co-located)_ | every hook side-effect documented; bundled agents carry no `hooks`/`mcpServers`/`permissionMode` + no trifecta; MCP scoped | Simon |

_P1/P7/P8/P9 are scored with four rubrics **co-located from `skills-studio`** (`cold-start-orientation`, `skills-authoring`, `skill-extensibility`, `security-and-scope-containment`, bundled in `../rubrics/`) rather than re-derived — a plugin's fitness, routing, evolution, and security are the skill concerns one layer up. Co-location (not a `../skills-studio/` reference) is what keeps this plugin self-contained: zero cross-plugin paths. P2–P6 are plugin-distinctive and get a dedicated foundation + drill-down rubric, gated 1:1 by `bin/check-foundations-coverage.py`._

## How to use it while building

1. **Pick the dimensions the plugin actually has.** A single-skill plugin may skip P3 (cohesion is trivial) and P4 (nothing shared). A plugin bundling a hook + MCP lives or dies on P2 and P9. The `plugins-holistic.md` §Scope says which are load-bearing for which plugin shape.
2. **For each live dimension, read its foundation before you write that part.** Build P2 from `component-fit-foundations.md`, P5 from `plugin-architecture-foundations.md`, etc. — so the bundle is grounded, not guessed.
3. **Make each ship-gate true as you go**, not after. The gate column above _is_ the produced plugin's pre-ship checklist — `validate_plugin.py` enforces the mechanical ones (manifest validity, path legality, layout); the rest are the §SelfAudit review items.
4. **Then red-team your own draft** (next section) before declaring done.

## The component-fit decision is the first move, not the last

Unlike a skill (which is one primitive), a plugin's central authoring act is **assigning each capability to a primitive**. Do this _before_ writing the manifest, because the manifest shape follows from it:

- Does it **have to run** on an event (lint, format, policy, notify)? → **hook** (`hooks/hooks.json`)
- Does it touch an **external/stateful system**? → **MCP** (`.mcp.json`), intent-level tools only
- Does it need **context isolation or parallel fan-out**? → **agent** (`agents/*.md`)
- Is it **model-auto-invoked knowledge/workflow**? → **skill** (`skills/*/SKILL.md`)
- Is it a **user-named explicit action**? → **command** (`commands/*.md`)

Write the fit table first (`capability → primitive → why`). That table _is_ P2's evidence and the skeleton of the `plugin.json`.

## Build-time red-team — summon the critics on your _own_ draft

Authoring is not done at "passes `validate_plugin.py`." Run `critique` on the plugin you just designed — the same 9-critic panel `evaluate` mode uses, turned on your own output. Self-review relaxes the cold-read rule, not the adversarial bar: push for ≥1 Critical or document why none exists.

**Stakes-tiered default:**

| When | Red-team pass |
| --- | --- |
| **Every produced plugin, before ship** (the floor) | `critique single-critic simon` (blast radius of bundled hooks/MCP, trust posture) **+** `single-critic wlaschin` (manifest correctness, illegal layout/state). Cheap; catches the two highest-frequency failure classes. |
| **A plugin that bundles hooks or an MCP**, OR a **marketplace** (multi-plugin), OR a **multi-plugin carve** | `critique full-panel` + synthesis — the full 9 lenses. The marketplace/carve case especially: a shared-infra mistake (P4) multiplies across every plugin, so Wlaschin's and Simon's lenses compound. |
| **A targeted edit** to one concern | the one or two critics who own that dimension (the table's "Red-team lens" column). |

Fold the surviving Critical/Major findings back into the draft (the `edit` step) before packaging. That is the loop closing on itself: **author/carve → score/critique → edit**, all inside one skill, over one shared body of knowledge.

## Why this matters

Without this bridge, `plugins-factory` is two halves bolted together — a packaging toolkit and an evaluation toolkit that share a directory. _With_ it, the building side draws on the **same foundations, rubrics, and critics** the evaluation side scores against, so a plugin is built to the standard it will be judged by. That is the bi-directionality: not a hand-off, a shared standard.
