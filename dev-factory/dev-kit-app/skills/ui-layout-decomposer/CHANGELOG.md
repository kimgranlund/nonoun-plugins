# Changelog — ui-layout-decomposer

Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: [SemVer](https://semver.org/).

## [0.1.0] — 2026-06-15

Initial cut. The two-axis UI-decomposition technique extracted from the dev-factory cockpit + design-rubric work.

### Added
- **The two-axis method** (`references/decomposition-method.md`) — OUTSIDE-IN (macro→micro: frame → regions →
  groups → atoms) × INSIDE-OUT (core→whole: actions → bindings → feedback → coherence), the gated rubric
  (A1·A2·B1·B2 `[gate]`, the rest `[review]`), the "pretty-but-dead vs functional-but-unreadable" framing, and the
  DECOMPOSE / DESIGN / GRADE workflows.
- **Four archetype references with ASCII wireframes** — `productivity-shell` (the cockpit we built),
  `saas-dashboard` (clamshell · sidebar/section-nav · breadcrumbs · page-header · table/data/settings content ·
  modal/drawer/snackbar), `marketing-site` (homepage section stack + feature/about/pricing/lead-gen/blog
  templates), `mobile-app` (tabbed view stack · sheets · modality · FAB · workflows). Each carries a named-pattern
  vocabulary + per-archetype outside-in / inside-out notes.
- `SKILL.md` table-of-contents with Quick Start, the archetype-selection table, §SelfAudit (structure-not-skin;
  artifact-as-data; gates-before-reviews; two-scores-never-one), and a Verify Target.
