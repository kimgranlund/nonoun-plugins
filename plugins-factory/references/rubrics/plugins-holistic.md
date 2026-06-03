---
date: 2026-06-02
status: draft
version: "0.1.0"
---

# Holistic Plugin Quality — 9-Dimension Meta-Rubric

**A plugin is a distribution contract, not a folder of stuff.** It promises that a coherent capability set can be installed, toggled, versioned, and trusted as one unit — and that each capability inside it is the _right shape_ for its job. This rubric asks whether all nine load-bearing concerns are addressed, because a plugin that scores 5/5 on packaging can still fail if a single capability uses the wrong primitive or a shared dependency uses a path that breaks at install.

This is a **synthesis rubric**, not a replacement for the individual rubrics. P2–P6 each point to a detailed drill-down rubric paired 1:1 with a foundation. P1, P7, P8, and P9 deliberately reference `skills-studio`'s existing rubrics (cold-start, skills-authoring, skill-extensibility, security-and-scope-containment) rather than duplicate them — a plugin's fitness, routing, evolution, and security concerns are the skill concerns one layer up.

**Grounding**: Synthesized from the official Claude Code plugin reference (manifest, components, `${CLAUDE_PLUGIN_ROOT}`/`${CLAUDE_PLUGIN_DATA}`, marketplace, namespacing, validation, install scopes), Anthropic's Agent Skills + "Writing tools for agents" engineering guidance, and the packaging-cohesion wisdom of mature plugin ecosystems (VS Code activation events, ESLint shareable configs, Backstage's "monolithic plugin problem", Obsidian single-purpose guidance).

---

## §The Problem

A `plugin.json` validating cleanly tells you the JSON is well-formed. It tells you nothing about whether:

- A capability that **must always run** (a lint/format/policy gate) was shipped as a hopeful skill instead of a deterministic **hook**
- A bundled **MCP server** 1:1-wraps an API — 30 endpoint-tools eating 50K+ of always-on context before the first action
- The plugin reaches a shared type registry through a `../shared-types` path that **silently breaks the moment it's installed** from a marketplace
- The plugin is a **kitchen sink** that taxes every install with standing context for capabilities most users never touch
- Two bundled skills have **overlapping triggers** with no hand-off, so the model can't reliably pick between them

**No manifest validation catches these, because they are architecture, not syntax.** This rubric is the site plan that says which of the nine load-bearing concerns were considered — and which drill-down rubric to run when one is weak.

---

## §First Principles

### 1. The plugin is the packaging unit; the component is the capability unit

Scope by "what do I toggle together," not "what is one feature." The official model is explicit: plugins "toggle on and off as needed… to reduce system prompt context." A plugin earns its boundary when a user enables/disables the whole set as one coherent capability and pays its standing context only while it's on. This is _distribution_ granularity, orthogonal to capability count.

### 2. Component fit is a consequence of task shape, not taste

Each capability has a determined right shape. **Hooks guarantee execution; prompts do not** — anything that must run on an event is a hook. **MCP connects external systems; a skill teaches the procedure** — they are complementary, and an MCP that wraps endpoints 1:1 is the field's most-cited anti-pattern. **Agents isolate context and parallelize.** **Skills are model-auto-invoked knowledge.** **Commands are user-named actions.** Picking the wrong one is the highest-frequency plugin defect.

### 3. Installed plugins cannot reach outside their own directory

Plugins are copied into a version-keyed cache at install; a `../shared-utils` path or a cross-plugin `$ref` does not resolve. Shared infrastructure must therefore be **co-located**, declared in **`dependencies`**, or **symlinked within the same marketplace** (dereferenced/copied at install). This is not a style preference — it is the single constraint that most often turns a clean-on-disk carve into a broken-on-install one.

### 4. Standing context is the tax every install pays

`claude plugin details` splits cost into _always-on_ (descriptions + MCP tool defs, paid every session) and _on-invoke_ (paid when a component fires). A good plugin keeps always-on minimal and pushes detail into load-on-demand skill references (progressive disclosure). An MCP server is the most expensive component to bundle and must clear the highest bar.

### 5. A plugin runs arbitrary code with the user's privileges

"Plugins and marketplaces are highly trusted components that can execute arbitrary code on your machine." A hook fires on your events, a bundled MCP starts on enable, a `bin/` joins your PATH. Trust is designed in: document every hook's side-effect, scope bundled MCPs, and rely on the loader rule that plugin-shipped agents cannot declare `hooks`/`mcpServers`/`permissionMode` — never on model behavior.

---

## §The Rubric

### P1 — Plugin Fitness & Scope `[gate]`

Should this be a plugin at all, and is its job one coherent sentence?

| Score | Evidence |
| --- | --- |
| **5** | Exists to be shared / versioned / reused across people or projects (not a personal one-off, not better as a bare skill or a standalone MCP). Job states in one sentence; every bundled component serves it. A user can reason about enabling/disabling it as one capability. |
| **4** | Clearly a shareable distribution unit with a one-sentence job. One component is tangential but defensible. |
| **3** | A plugin by packaging but the job needs two sentences, or 1–2 components belong to a different job/audience. Toggle rationale is fuzzy. |
| **2** | Should probably be a standalone skill or a single MCP — packaged as a plugin for no share/version/reuse reason — OR the scope spans clearly distinct jobs. |
| **1** | No coherent job. A junk drawer of unrelated capabilities, or a personal experiment dressed as a distributable plugin. |

**Go deeper**: `cold-start-orientation.md` _(co-located)_ (one-sentence orientation), `boundary-cohesion.md` (P3, the scope-width companion). **Test** (the one-sentence test): write the plugin's job in one sentence. If every component serves it → P1 ≥ 4. If naming the components forces "and also…" clauses → P1 ≤ 3.

---

### P2 — Component Fit `[gate]` `[review]`

Is each capability the right primitive — hook, MCP, agent, skill, or command?

The decision ladder (`component-fit.md`): **must-run-deterministically-on-an-event → Hook** · **external/stateful system → MCP** (intent-level tools, not 1:1 endpoints) · **context isolation or parallel fan-out → Agent** · **model-auto-invoked knowledge workflow → Skill** · **user-named explicit action → Command**.

| Score | Evidence |
| --- | --- |
| **5** | Every capability uses the primitive its task shape determines. Guarantees are hooks; external state is an intent-level MCP; isolation/parallel work is an agent; auto-invoked knowledge is a skill; named actions are commands. Each choice is justified, not defaulted. |
| **4** | Mostly correct. 1 borderline choice (e.g. a command that could be a skill) that doesn't cause active failure. |
| **3** | Some mismatches with real cost: a "should always run" check left as a prose instruction; a skill doing what a hook should guarantee; an agent task that didn't need isolation. |
| **2** | Most capabilities defaulted to "skill" regardless of shape. A required guarantee depends on the model remembering. An MCP wraps an API 1:1. |
| **1** | No fit reasoning. Everything is one primitive (all skills, or an everything-MCP). The wrong-primitive tax is paid on every dimension downstream. |

**Go deeper**: `component-fit.md`, `foundations/component-fit-foundations.md`. **Test** (the guarantee test + the wrapper test): (a) list every capability that _must_ happen regardless of model behavior — each one not a hook is a P2 defect. (b) If a bundled MCP exists, count its tools; >~25 or 1:1-with-endpoints = a wrapper, not a perimeter → P2 fails.

---

### P3 — Boundary Cohesion `[review]`

Is the scope coherent — neither a kitchen sink nor a fragment — with internal granularity inside one domain?

| Score | Evidence |
| --- | --- |
| **5** | One domain/workflow. Internal granularity is rich (many well-named skills) but the _plugin_ boundary is one job. Not a monolith taxing every install; not a fragment that only works with three sibling plugins installed. |
| **4** | Coherent domain. Slightly broad or slightly narrow, but the toggle still makes sense and no cross-plugin coupling is hidden. |
| **3** | Borderline: the bundle spans two adjacent jobs that _could_ split, or is a fragment that assumes a sibling is always co-installed without declaring it. |
| **2** | Kitchen-sink (cross-cutting scope taxing every install) OR over-fragmented (one workflow scattered across plugins that only work together). |
| **1** | Scope is incoherent — components share a directory but not a job, or the "plugin" is one skill that should not have been split out at all. |

**Go deeper**: `boundary-cohesion.md`, `foundations/plugin-cohesion-foundations.md`. **Test** (split/merge test): would a user ever want exactly half of this plugin and none of the other half? If yes → it's two plugins (fragment the _other_ way: it's too broad). Does this plugin only function when a specific sibling is also enabled, undeclared? → it's a fragment. Either = P3 ≤ 2.

---

### P4 — Dependency & Shared-Infra Legality `[gate]`

Are cross-plugin dependencies resolved legally — and is nothing dead bundled?

| Score | Evidence |
| --- | --- |
| **5** | Every shared resource (types, knowledge, methodology, a sibling skill) is resolved by **co-location**, a declared **`dependencies`** entry, or a **same-marketplace symlink** (dereferenced at install). **Zero `../`-traversal paths** and zero cross-plugin `$ref`s that won't resolve post-install. No dead/orphan/retired component is bundled. |
| **4** | Legal sharing throughout; `dependencies` declared. One reference file is unused (dead-weight) but no path is illegal. |
| **3** | Sharing works on disk but leans on a co-location that should be a declared `dependency`, OR a bundled component is retired/never-read. No outright `../` break yet. |
| **2** | A shared `$ref` or include uses a path that resolves locally but **breaks when installed** from a marketplace. The plugin is correct in the repo and broken in the cache. |
| **1** | Multiple `../` cross-plugin paths; shared infra assumed to "just be there." Ships dangling references on first install. |

**Go deeper**: `dependency-and-sharing.md`, `foundations/dependency-and-sharing-foundations.md`. **Test** (the install test): for every path the plugin references, ask "does this resolve after the directory is copied, alone, into a version-keyed cache?" Any `../` outside the plugin root, or any `$ref` into a sibling plugin, = P4 fails. Then grep the bundle for retired/renamed component names.

---

### P5 — Manifest & Packaging Correctness `[gate]`

Is the `plugin.json` (and `marketplace.json`, if present) valid, with a correct directory layout?

| Score | Evidence |
| --- | --- |
| **5** | `validate_plugin.py` passes: kebab-case `name`; `version` + `CHANGELOG`; all component paths `./`-relative with no `..`; **only** `plugin.json` in `.claude-plugin/`, all component dirs at the plugin **root**; `hooks/hooks.json` / `.mcp.json` at root; bundled scripts referenced via `${CLAUDE_PLUGIN_ROOT}`; persistent state only in `${CLAUDE_PLUGIN_DATA}`. marketplace entry (if any) has `name` + legal `source`, no reserved name. |
| **4** | Manifest valid and layout correct. One advisory: a custom component path that replaces rather than extends a default, or a missing `description`/`keywords`. |
| **3** | Loads, but a component is misplaced inside `.claude-plugin/` (silently won't load), OR state is written to the ephemeral plugin root, OR `version` set in both `plugin.json` and the marketplace entry. |
| **2** | A wrong-typed manifest field, a malformed `hooks/hooks.json` (blocks the whole plugin), or a `source` path containing `..`. |
| **1** | Invalid JSON / missing required `name`, or a layout where most components silently fail to load. |

**Go deeper**: `manifest-and-packaging.md`, `foundations/plugin-architecture-foundations.md`, `../plugin-architecture.md`. **Test**: run `${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py plugin <path>` (and `marketplace <path>` if applicable). Any ERROR = P5 fails. Then confirm: is any non-manifest file inside `.claude-plugin/`? Is any persistent write target inside `${CLAUDE_PLUGIN_ROOT}`?

---

### P6 — Context Economy `[review]` `[hypothesis]`

Is the plugin toggleable with lean always-on cost, and is its knowledge progressively disclosed?

| Score | Evidence |
| --- | --- |
| **5** | `claude plugin details` always-on cost is minimal and justified (terse component descriptions; no needless MCP server). Bundled skills follow progressive disclosure (SKILL.md as TOC, references domain-partitioned + one level deep). Detail lives on-invoke. The plugin is worth leaving enabled. |
| **4** | Lean always-on; progressive disclosure mostly followed. 1 heavy description or 1 preemptively-loaded reference. |
| **3** | Noticeable standing cost (verbose descriptions, or an MCP whose tool defs dominate) but tolerable. Some bundled skills front-load reference content. |
| **2** | Always-on cost is high enough that users will toggle it off between uses — defeating the bundle. Bundled knowledge is front-loaded, not disclosed. |
| **1** | The plugin dumps standing context (many verbose descriptions + a wrapper MCP) such that enabling it measurably degrades every unrelated session. |

**Go deeper**: `context-economy.md`, `foundations/context-economy-foundations.md`. The `[hypothesis]` sub-property is `context-economy` **D6** (Stays Enabled by Default). **Test** (always-on audit): read `claude plugin details` (or `context-cost.py` when available). Is always-on cost dominated by anything other than terse skill/command descriptions? An MCP server's tool defs or verbose descriptions dominating = P6 ≤ 2. `[hypothesis]`: a plugin users leave _enabled by default_ is the real signal — track install/disable telemetry where available.

---

### P7 — Routing & Discoverability `[gate]` `[review]`

Do the right components fire at the right time, with no intra-bundle collisions?

| Score | Evidence |
| --- | --- |
| **5** | Every bundled skill/command has a third-person _what + when_ description with specific trigger terms and a convention-following name. No two bundled skills have overlapping triggers without an explicit hand-off. An explicit `/command` entry exists for the main workflow (not only model-routed skills). Namespacing (`/plugin:skill`) is correct. |
| **4** | Descriptions routable; an explicit entry point exists. One mild trigger overlap between bundled skills, with a hand-off. |
| **3** | Descriptions activate but are over-broad; no explicit `/command` entry (humans must rely on the router). Some overlap without hand-off. |
| **2** | Two+ bundled skills collide on triggers; the model picks unreliably between them. Vague or first-person descriptions. |
| **1** | Components are undiscoverable or constantly mis-route against each other. Tag-cloud descriptions. |

**Go deeper**: `skills-authoring.md` _(co-located, D1–D2)_, `cold-start-orientation.md`. **Test** (collision scan): for each pair of bundled skills, do their trigger phrases overlap without a "for X use this, for Y use that" hand-off? Any colliding pair = P7 ≤ 3. Then: is there a user-typable entry point, or only model-invoked skills?

---

### P8 — Evolution & Maintenance `[gate]` `[review]`

Can the plugin grow and be updated without breaking installs?

| Score | Evidence |
| --- | --- |
| **5** | semver (or deliberate SHA mode) + `CHANGELOG.md`; invocation `name`s stable across releases; growth is additive (a new skill drops in without breaking existing `/name` shortcuts); persistent state in `${CLAUDE_PLUGIN_DATA}` (survives updates); `validate_plugin.py` wired into CI; obvious additive headroom in the domain. |
| **4** | Versioned + changelogged + stable names + additive. Missing: a CI validate gate, or a documented update path for bundled deps. |
| **3** | Versioned but no changelog discipline, OR growth requires touching existing wiring (a new component renames an old shortcut). |
| **2** | No semver intent (version pinned in two places / never bumped), invocation names unstable across releases, or state in the ephemeral root (lost on update). |
| **1** | No version, no changelog, no additive path. Every change is an ad-hoc append that risks breaking existing installs. |

**Go deeper**: `skill-extensibility.md` _(co-located)_, `manifest-and-packaging.md` (versioning rules). **Test** (additive-growth test): would adding one new capability to this plugin break any existing component's invocation name or any installed user's shortcuts? If yes → P8 ≤ 3. Is the `version` set in exactly one place (`plugin.json` _or_ the marketplace entry, not both)?

---

### P9 — Security & Trust `[gate]` `[review]`

Is the plugin's execution surface contained, with documented side-effects and no smuggled trifecta?

_Mechanization split: `validate_plugin.py` mechanically ERRORs on the **loader rule** (a bundled agent declaring `hooks`/`mcpServers`/`permissionMode`) — that sub-check is the `[gate]`. The trifecta, hook-side-effect-documentation, and MCP-scope checks are `[review]` (evidence-cited), not script-enforced — a green validator does not discharge them._

| Score | Evidence |
| --- | --- |
| **5** | Trust posture stated. Every hook's effect documented (does it mutate? block? on which events/matchers?), with blocking reserved for genuine policy. Bundled agents declare no `hooks`/`mcpServers`/`permissionMode` (loader rule) and carry no lethal trifecta (private data + untrusted content + external action in one agent). Bundled MCP scoped to the minimum perimeter. Bundled skills that read untrusted content treat it as data, not instructions. |
| **4** | Hooks documented; agents clean; MCP scoped. One gap: a hook's matcher is broad, or an MCP's perimeter is wider than the job needs. |
| **3** | Hooks present but side-effects under-documented; trust posture implicit. No outright trifecta, but blast radius unassessed. |
| **2** | A hook mutates or blocks silently, OR a bundled agent + MCP combination gives an injection foothold, OR untrusted-content handling is "the model is told to be careful." |
| **1** | Lethal trifecta live in a bundled agent (reads untrusted content + private data access + external action), or a hidden destructive hook. Model behavior is the only defense. |

**Go deeper**: `security-and-scope-containment.md` _(co-located)_, `agents/critic-simon.md`. **Test** (the bundled-trifecta test): for each bundled agent/skill, does it (a) access private data, (b) process untrusted content, (c) take external actions? Two present = elevated; all three in one component = structural separation required. Then: is any hook's side-effect undocumented, or any bundled agent declaring `mcpServers`/`hooks`/`permissionMode`?

---

## §Scope — what these nine cover, and the split with skills-studio

These nine are **per-plugin** quality dimensions — properties a single plugin can be scored on. The split with `skills-studio` is deliberate and non-redundant:

- **P2–P6 are plugin-distinctive** (component fit, boundary cohesion, dependency legality, manifest/packaging, context economy) — concerns that only exist _because_ a plugin bundles multiple component types and is distributed. Each has a dedicated foundation + drill-down rubric.
- **P1, P7, P8, P9 are skill concerns one layer up** — a plugin's fitness/orientation (cold-start), routing (skills-authoring), evolution (skill-extensibility), and security (security-and-scope-containment) are scored against `skills-studio`'s existing rubrics rather than re-derived here. Duplicating them would be the redundancy the `expert-council-design` rubric and the critics flag.
- **Carving a library into plugins** (the `carve` mode) is scored by applying P1 + P3 + P4 _across the set_ — there is no separate carve dimension in v0.1 (a `carve-quality` rubric is tracked in ROADMAP).

---

## §Anti-patterns (cross-dimensional)

### AP-P1 — The kitchen-sink monolith

**Symptom**: One plugin bundles a whole team's tooling (P3 ✗). Always-on cost is high (P6 ✗); the model faces a "which capability?" routing tax (P7 ✗). **Root cause**: Scoping by org boundary instead of by toggle/job. Distribution granularity confused with "everything we own." **Correction**: Split by job-to-be-done; ship internal granularity inside each domain plugin; use `dependencies` for genuinely separable concerns.

### AP-P2 — The broken-on-install shared dep

**Symptom**: Clean in the repo (P5 passes), broken after `/plugin install` — a `../shared-types` path or cross-plugin `$ref` doesn't resolve in the cache (P4 ✗). **Root cause**: Designing against the on-disk monorepo layout, not the installed-cache layout. Validation that checks JSON but not path-resolution-after-copy. **Correction**: Co-locate, declare in `dependencies`, or symlink within the marketplace. Test every path against "does this resolve when copied alone?"

### AP-P3 — The hopeful guarantee

**Symptom**: A lint/format/policy step shipped as a skill or a prose instruction (P2 ✗). It runs "usually." One day the model skips it and an unformatted/unsafe change lands. **Root cause**: "Hooks guarantee execution; prompts do not" was not applied. The capability's _must-always-run_ shape was ignored. **Correction**: Anything that must run on an event is a hook. Reserve skills/prompts for judgment work the model _should_ decide about.

### AP-P4 — The API-wrapper MCP

**Symptom**: A bundled MCP exposes 30 endpoint-shaped tools (P2 ✗); their definitions dominate always-on context (P6 ✗). **Root cause**: Treating MCP as a delivery mechanism for an API instead of a curated intent-level action perimeter. **Correction**: Consolidate to task-level tools (`schedule_event`, not `search_availability` + `create_booking` + …); ≤~25 high-signal tools; namespace with a consistent prefix.

### AP-P5 — The trifecta agent in a trusted bundle

**Symptom**: A bundled agent reads external content, holds credentials/private-data access, and can push/call out — each reviewed in isolation looked fine (P9 ✗). **Root cause**: The plugin's trust posture was never assessed as a combination; the loader's agent restrictions were treated as the whole defense. **Correction**: Audit each bundled agent for the trifecta; structurally separate reading-untrusted from acting-externally; document every hook's blast radius.

---

## §Hard Tests

1. **The one-sentence test** (P1): write the plugin's job in one sentence. If naming the components forces "and also…" clauses, the scope is incoherent.

2. **The guarantee test** (P2): list every capability that must happen regardless of model behavior. Each one not implemented as a hook is a fit defect.

3. **The wrapper test** (P2): if a bundled MCP exists, count its tools. >~25 or 1:1-with-endpoints = a wrapper, not a perimeter.

4. **The split/merge test** (P3): would a user ever want exactly half this plugin? Does it only work with an undeclared sibling co-installed? Either = a boundary defect.

5. **The install test** (P4): for every referenced path, does it resolve after the directory is copied _alone_ into a version-keyed cache? Any `../` outside the root or cross-plugin `$ref` = a break.

6. **The validate test** (P5): `validate_plugin.py plugin <path>` clean? Any non-manifest file inside `.claude-plugin/`? Any persistent write to `${CLAUDE_PLUGIN_ROOT}`?

7. **The always-on audit** (P6): is `claude plugin details` always-on cost dominated by anything other than terse descriptions? An MCP's tool defs or verbose descriptions dominating = a context-economy failure.

8. **The collision scan** (P7): any pair of bundled skills with overlapping triggers and no hand-off? Is there a user-typable entry point at all?

9. **The additive-growth test** (P8): would adding one capability break an existing invocation name? Is `version` set in exactly one place?

10. **The bundled-trifecta test** (P9): any single bundled agent/skill with private-data access + untrusted-content exposure + external-action capability? Any undocumented hook side-effect?
