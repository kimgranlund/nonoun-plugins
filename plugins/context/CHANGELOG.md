# Changelog

The context plugin (formerly Progressive Context), newest first. Releases before 0.2.0 are recorded only in git history.

## [0.3.0] - 2026-10-25

### Added

- Five context skills move in from the user-level skill folders (T-0790): `context-fog-of-war`, `context-routing-review`, `generative-systems`, `system-atlas` and `icm-architect`. Their content is unchanged except that links into evidence left out of the package (`generative-systems/resources/reports/`, two design skills' reports, a local download) became code spans. `progressive-context` is unchanged.

### Upgrade

- Update the plugin, then remove the user-level copies of the five skills (`~/.claude/skills/<name>`, `~/.codex/skills/<name>`) so each host loads one version. Start a fresh chat after the change.

## [0.2.0] - 2026-10-25

### Changed

- The plugin is renamed from `progressive-context` to `context` and now lives in `plugins/context/` (T-0793). Its skill keeps the name `progressive-context`, so it is invoked as `/context:progressive-context` in Claude Code and still as `$progressive-context` in Codex. Skill behavior is unchanged.

### Upgrade

- The install id changed. Claude Code: run `/plugin install context@sdlc-lite`, then `/plugin uninstall progressive-context@sdlc-lite` and remove any `progressive-context@sdlc-lite` entry left in `enabledPlugins` in your settings. Codex: refresh the marketplace, enable `context`, and remove `progressive-context`.
- Start a fresh chat after the change.
