# Changelog

All notable changes to **dev-kit-corpus** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.2.0] — 2026-06-15

### Changed

- **`spec-quality-check.py` validates SKILL-format specs.** The gate now reads a spec asset that is a **SKILL-format artifact** (front-matter intent surface + brief + the embedded ```json contract + optional `references/`), a **folder** (`spec/<slug>/SKILL.md`), or the legacy json-only contract — the embedded contract is the single source of truth either way, so every existing gate (schema-valid · criteria-checkable · rubric-binds · non-goals-present · decomposition-entailment) is unchanged. Added a `skill-shape` gate: when front-matter is present, the skill surface and the machine contract must AGREE (`name` present, `description` present, the contract `cell`'s slug == `name`); a legacy json-only spec passes it vacuously. Backs dev-kernel 0.2.0's `spec-author` skill; selftest extended (a SKILL-format file, the folder shape, and a name↔cell-slug disagreement).
- **`spec-quality.rubric.json`** notes the SKILL-format asset shape and carries the matching `skill-shape` gate dimension.
- **(0.2.0 council fixes)** `schema-valid` now asserts the cell's layer is `spec` (the spec gate rejects a non-spec cell asset); the `rubric-binds` dimension clarified — the gate checks the *binding*, the rubric-maturity precondition is a lattice invariant (`lattice.py` validity + `gate-ticket-ready`), not this standalone gate.

## [0.1.0] — 2026-06-14

Initial cut — the corpus family kit (the reference family binding the kernel's contracts).
