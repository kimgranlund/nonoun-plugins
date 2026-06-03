---
date: 2026-06-02
status: draft
coverage: canonical
version: "0.1.0"
primary_sources:
  - "Anthropic. Claude Code Plugins reference (path-traversal limit, ${CLAUDE_PLUGIN_ROOT}/${CLAUDE_PLUGIN_DATA}, dependencies, symlink dereferencing). code.claude.com/docs/en/plugins-reference"
  - "Anthropic. Create and distribute a plugin marketplace (allowCrossMarketplaceDependenciesOn, metadata.pluginRoot, source forms). code.claude.com/docs/en/plugin-marketplaces"
  - "ESLint. Shareable configs (multiple entry points in one package; peerDependency hygiene). eslint.org/docs/latest/extend/shareable-configs"
  - "Backstage. Backend plugins must be stateless / store state externally. backstage.io/docs/backend-system/architecture/plugins"
---

# Dependency & Shared-Infra Legality — Foundational Knowledge Document

The theory behind P4: an installed plugin cannot reach outside its own directory, so every shared resource must be resolved by a legal mechanism — or the plugin ships dangling references the moment someone installs it.

## The Core Claim

A plugin that is correct on disk can be broken on install. Claude Code **copies a plugin into a version-keyed cache** when it is installed from a marketplace, and *"installed plugins cannot reference files outside their directory. Paths that traverse outside the plugin root (such as `../shared-utils`) will not work after installation."* The plugin author who develops against a monorepo layout — where `../core-types/schemas/foo.json` resolves fine locally — ships a plugin that fails for every user, because the sibling directory was never copied into the cache alongside it.

This is the single constraint that most often turns a clean carve into a broken one. It has nothing to do with manifest validity (P5): the JSON is perfect, the layout is correct, `claude plugin validate` passes — and the plugin still dangles, because a `$ref` or an include or a script path reaches across the install boundary.

The discipline is: **for every path a plugin references, ask "does this resolve after the directory is copied, alone, into a version-keyed cache?"** If the answer is no, it must be resolved by one of three legal mechanisms.

## The three legal mechanisms

### 1. Co-location
Put the shared resource *inside* the plugin that needs it. Correct when the resource is small, tightly coupled to one plugin, or has a single dominant consumer. The cost is duplication if a second plugin also needs it; the benefit is zero cross-boundary risk. A type registry whose `$ref`s resolve a pipeline's schemas belongs co-located with that pipeline (its tightest, hottest consumer), even if a second plugin also references it.

### 2. The `dependencies` manifest field
Declare the other plugin as a dependency: `"dependencies": ["helper-lib", {"name": "secrets-vault", "version": "~2.1.0"}]`. Correct when two plugins are *each* independently useful and one genuinely builds on the other — the skill-level dependency. The dependency is resolved by the marketplace at install, not by a filesystem path. This is the ESLint "multiple entry points / peerDependency" model translated to plugins: separable concerns stay separable and re-compose through a declared edge, not a hard-coded path.

### 3. Same-marketplace symlinks
Within one marketplace, symlink the shared file into the plugin. The documented resolution: *links within the plugin's own dir are preserved as relative symlinks; links elsewhere in the same marketplace are dereferenced (content copied in); links outside the marketplace are skipped for security.* Correct for **file-level** sharing where a `dependencies` edge is too coarse (you need the actual bytes of a schema/template, not a plugin relationship). The symlink is resolved to copied content at install, so it survives the cache copy — but only if its target is inside the same marketplace.

## The decision among the three

| Shared resource shape | Mechanism |
|---|---|
| Small / tightly coupled / one dominant consumer | **Co-locate** |
| A whole plugin another plugin builds on, both independently useful | **`dependencies`** edge |
| Specific file bytes (a schema, a template, a persona corpus) shared across same-marketplace plugins | **Symlink** (within the marketplace) |
| Anything outside the marketplace | **None is legal** — vendor a copy in, or restructure |

The trap is reaching for a fourth, illegal mechanism — the raw `../` path — because it is the one that *works in development*. It is also the one that silently breaks in production. A validator that only checks JSON will never catch it; the check must be a path-resolution test against the copied-alone layout.

## A real example of the trap (this very library)

When this skill library is carved into plugins, the UI pipeline's 16 tightly-coupled `ui-compose-*` / `ui-verify-*` skills declare *zero* peers but are coupled through a shared type registry via `shared://artifacts/*` `$ref`s. A naive carve that puts the type registry in its own `core-types` plugin and the compose skills in a `design-system` plugin creates exactly the AP-P2 failure: every `$ref` from a compose skill into `core-types` is a cross-plugin reference that won't resolve post-install. The legal fixes: **co-locate** the registry inside `design-system` (its tightest consumer) and **symlink** it into the meta-authoring plugin that also needs it — or give both a declared **`dependencies`** edge and resolve the schemas through the marketplace, not a path. The carve is correct only when every shared `$ref` is run through the install test first.

## Dead weight is a dependency problem too

A plugin that bundles a retired, renamed, or never-read component carries a different defect on the same axis: a reference that points at something that *shouldn't be there*. Shipping `extract-ui-css` (retired) or a `peer_skills` entry naming a skill that no longer exists is a dangling reference of the opposite kind — not a path that escapes the plugin, but a pointer to a corpse inside it. Both fail P4 because both ship references that don't resolve to live, correct targets. Run the dead-weight grep before packaging: every bundled component name, every internal pointer, must resolve to a live file.

## Marketplace-level cross-dependencies

When plugins in *different* marketplaces depend on each other, the marketplace must opt in via `allowCrossMarketplaceDependenciesOn` (a whitelist of other marketplaces its plugins may depend on). Managed environments restrict this further via `strictKnownMarketplaces`. For a single-marketplace library carve, this is moot — but a plugin declaring a dependency on a plugin in *another* marketplace without the whitelist is an install-time failure waiting to happen.

## When not to share at all

Not every apparent overlap is shared infrastructure. Two plugins that each contain a small, slightly-different copy of a 20-line helper are *better duplicated than coupled* — the coupling cost (a dependency edge, a symlink, a version constraint to keep in sync) can exceed the duplication cost. ESLint's guidance applies: prefer internal granularity and a little duplication over a fragile web of cross-package dependencies. Share infrastructure that is genuinely load-bearing and changes in lockstep; duplicate the rest.

## Implications for plugins-studio

- The `carve` mode's step 4 (`carve-method.md`) is *exactly* this decision, run for every shared-infra item: co-locate / `dependencies` / symlink, never `../`.
- P4's mechanical test in `plugins-holistic.md` is the **install test**: for every referenced path, does it resolve after copy-into-cache? Plus the dead-weight grep.
- The validator `${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py` statically flags `../`-traversal in component paths and `source` fields; the deeper `$ref`-escapes-the-plugin check is a `[review]` item the evaluator runs.
- Owning critics: **Wlaschin** (make the illegal layout unrepresentable) and **Simon** (a cross-boundary reference is also an attack-surface question).

## Source Citations

1. Anthropic. *Claude Code Plugins reference.* https://code.claude.com/docs/en/plugins-reference
2. Anthropic. *Create and distribute a plugin marketplace.* https://code.claude.com/docs/en/plugin-marketplaces
3. ESLint. *Shareable Configs.* https://eslint.org/docs/latest/extend/shareable-configs
4. Backstage. *Backend system — plugins.* https://backstage.io/docs/backend-system/architecture/plugins/
