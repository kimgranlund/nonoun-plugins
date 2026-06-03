# Changelog

All notable changes to **adia-ui-forge** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.1.0] — 2026-06-03

Initial release — the maintainer-side counterpart to `adia-ui-factory`, carved and de-repo'd from the `@adia-ai` monorepo's `.agents/` system (scope A: the framework's own authoring toolkit, assuming `@adia-ai` monorepo conventions).

### Added

- **7 skills** — `adia-ui-forge` (orchestrator: classify subsystem → route) + `adia-ui-authoring` (web-components / web-modules), `adia-ui-a2ui` (the A2UI / gen-ui engine), `adia-ui-llm` (the `@adia-ai/llm` client), `adia-ui-gen-review` (generated-UI quality scoring), `adia-ui-dogfood` (QA sweep), `adia-ui-release` (release engineering + migration-guide authoring).
- **7 commands** — `/adia-forge-orient·author·a2ui·llm·review·dogfood·release`.
- **Advisory authoring-lint hook** — `bin/forge-lint` (11 component-authoring smells; `PostToolUse` on `Write|Edit`, never blocks).
- **Co-located shared infra** — `references/shared/` (content-trust, plan-execute-verify, skill-conventions) + `bin/lib/` (audit-axes, teach-router, dry-run-irreversible, run-skill-evals). Self-contained, zero cross-plugin paths.

### Reviewed

- Red-teamed with the `plugins-factory` 9-critic council (CONDITIONAL → folded): reconciled the build-state docs, cut the always-on context tax (removed a redundant `trigger:` block, trimmed the longest skill descriptions), disclosed and guarded the release scripts' publish / network reach, synced the four description surfaces, and labeled the `forge-lint` ↔ `adia-lint` shared-core duplication. Full record under `reviews/`.
