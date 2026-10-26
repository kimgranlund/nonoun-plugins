# Changelog

The context plugin (formerly Progressive Context), newest first. Releases before 0.2.0 are recorded only in git history.

## [0.2.0] - 2026-10-25

### Changed

- The plugin is renamed from `progressive-context` to `context` and now lives in `plugins/context/` (T-0793). Its skill keeps the name `progressive-context`, so it is invoked as `/context:progressive-context` in Claude Code and still as `$progressive-context` in Codex. Skill behavior is unchanged.

### Upgrade

- The install id changed. Claude Code: run `/plugin install context@sdlc-lite`, then `/plugin uninstall progressive-context@sdlc-lite` and remove any `progressive-context@sdlc-lite` entry left in `enabledPlugins` in your settings. Codex: refresh the marketplace, enable `context`, and remove `progressive-context`.
- Start a fresh chat after the change.
