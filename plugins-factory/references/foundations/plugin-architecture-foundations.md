---
date: 2026-06-02
status: draft
coverage: canonical
version: "0.1.0"
primary_sources:
  - "Anthropic. Claude Code Plugins reference. code.claude.com/docs/en/plugins-reference"
  - "Anthropic. Create plugins (scope + standalone-vs-plugin guidance). code.claude.com/docs/en/plugins"
  - "Anthropic. Create and distribute a plugin marketplace. code.claude.com/docs/en/plugin-marketplaces"
related: "references/plugin-architecture.md (the scannable field-level reference; this doc is the load-bearing mental model + failure modes behind it)"
---

# Plugin Architecture — Foundational Knowledge Document

The theory behind P5: _why_ the manifest, layout, path variables, and versioning rules exist, and _how_ a plugin silently breaks when they're violated. For the field-level reference (every manifest field, every component dir), see `../plugin-architecture.md`. This doc is the mental model.

## The Core Claim

A plugin is not run in place — it is **copied into a version-keyed cache** when installed, and re-resolved through path variables at runtime. Almost every packaging rule that feels arbitrary follows from that one fact. The author who holds the cache-copy model in their head packages correctly; the one who pictures "my files, where I put them" ships plugins that load half their components, lose state on update, or never receive their own changes.

Three mental-model facts carry most of the weight:

1. **The manifest is a thin, optional declaration — the layout is the real contract.** `.claude-plugin/plugin.json` needs only `name`; everything else auto-discovers _from fixed root locations_. So the directory layout, not the manifest, is what determines whether a component loads. Put a component in the wrong place and the plugin loads fine with that component silently missing.
2. **`${CLAUDE_PLUGIN_ROOT}` is ephemeral; `${CLAUDE_PLUGIN_DATA}` is persistent.** The install dir changes on every update (the old version lingers ~7 days, then is cleaned up). State written to the root is lost on update; state written to `${CLAUDE_PLUGIN_DATA}` (`~/.claude/plugins/data/{id}/`) survives.
3. **The version is the cache key.** Whether a user _receives_ your changes is decided by the version resolution order (plugin.json `version` → marketplace entry `version` → git SHA → `unknown`). Set it in two places and one silently wins; pin it and forget to bump and users never update.

## Failure mode 1 — the silently-missing component

The #1 documented packaging error: a component placed inside `.claude-plugin/` instead of at the plugin root. _"The `.claude-plugin/` directory contains the `plugin.json` file. All other directories (commands/, agents/, skills/, hooks/, …) must be at the plugin root, not inside `.claude-plugin/`."_ The plugin **loads** — validation passes, the manifest is fine — but the misplaced component never registers. The symptom is "my skill isn't firing" with a green validate. The mental-model fix: `.claude-plugin/` holds exactly one file (the manifest); everything else lives one level up.

A second variant: a root `CLAUDE.md` is **not** loaded as project context. Authors expect "instructions in CLAUDE.md" to reach the model; in a plugin they don't. Instructions must ship as a skill.

A third: a malformed `hooks/hooks.json` doesn't fail _that hook_ — it blocks the **entire plugin** from loading. The blast radius of a JSON typo is the whole bundle.

## Failure mode 2 — state in the ephemeral root

An author writes a cache file, a generated config, or a venv into `${CLAUDE_PLUGIN_ROOT}/...`. It works until the first update, when the root path changes and the state vanishes (and the old dir is reaped after the grace period). The fix is structural: bundled _read-only_ assets (scripts, configs, templates) are referenced via `${CLAUDE_PLUGIN_ROOT}`; anything _written_ goes to `${CLAUDE_PLUGIN_DATA}`. The reference docs even show a `SessionStart`-hook pattern that re-installs dependencies into `${CLAUDE_PLUGIN_DATA}` only when the bundled `package.json` differs from the persisted copy — the canonical "ephemeral code, persistent state" split.

## Failure mode 3 — the version set twice

`version` in both `plugin.json` and the marketplace entry: `plugin.json` wins silently, so a stale manifest version can mask the marketplace one, and `/plugin update` reports "already at latest" while the author swears they bumped it. The rule: set `version` in exactly one place. Two deliberate strategies — explicit semver (bump on every release; best for published plugins) or omit-version SHA mode (every commit is an update; best for active internal development) — and never both.

## Failure mode 4 — replace-vs-extend path fields

A custom path field silently _replaces_ the default directory for some fields and _adds to_ it for others. `commands`/`agents`/`outputStyles`/`themes`/`monitors` **replace** the default dir; `skills` **adds** to the default `skills/`. An author who sets `"commands": ["./extras/"]` expecting to _add_ extras loses the default `commands/` dir. The fix: know which fields replace, and list the default explicitly when you mean to extend (`["./commands/", "./extras/"]`).

## The marketplace layer

A `.claude-plugin/marketplace.json` is a catalog: `name` (kebab) + `owner` + `plugins[]`, each entry `name` + `source`. Sources can be a relative path (git-added marketplaces only), `github`, `url`, `git-subdir`, or `npm`; a `source` containing `..` is a hard error (the same traversal discipline as P4). `strict` (default true) decides whether `plugin.json` is the authority and the marketplace entry supplements it, or the marketplace entry _is_ the whole definition. Reserved marketplace names (anthropic-_, claude-_, etc.) cannot be used. A marketplace is typically just a git repo.

## Why "plugin" is the distribution unit (the scope mental model)

The official guidance is explicit that a plugin is a _packaging/distribution_ choice, not a capability one: use a **standalone `.claude/` skill** (short name `/hello`) for personal, project-only, or experimental work; use a **plugin** (namespaced `/plugin:hello`) when you want to share, version, reuse across projects, or distribute through a marketplace. "Start with standalone configuration… then convert to a plugin when you're ready to share." This is why P1 (Fitness) asks "should this be a plugin at all?" before P5 asks "is the plugin well-formed?" — a perfectly-packaged plugin that should have been a standalone skill still fails fitness.

## Validation as the mechanized gate

`claude plugin validate <path> [--strict]` checks the manifest, component frontmatter, and `hooks/hooks.json`; `--strict` promotes unrecognized-field warnings to errors (the CI mode). A mature plugin wires it into CI. Because this skill's gate must run without the CLI guaranteed present, `plugins-factory` ships `${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py` to reproduce the documented static checks in-repo (kebab name, `./`-relative paths, no `..`, layout, version placement, marketplace fields) and gates on its exit code.

## Implications for plugins-factory

- P5's `[gate]` dimensions are exactly the statically-checkable rules above; `${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py` mechanizes them and the rubric's tests invoke it.
- The `author` workflow makes these true _as it builds_ (the manifest follows the component-fit table), not after.
- Owning critics: **David F.** (reproducible, idempotent packaging + the CI gate) and **Scott W.** (make the illegal layout/state unrepresentable).

## Source Citations

1. Anthropic. _Claude Code Plugins reference._ <https://code.claude.com/docs/en/plugins-reference>
2. Anthropic. _Create plugins._ <https://code.claude.com/docs/en/plugins>
3. Anthropic. _Create and distribute a plugin marketplace._ <https://code.claude.com/docs/en/plugin-marketplaces>
