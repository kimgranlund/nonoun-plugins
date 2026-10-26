# Changelog

## 0.2.2 — 2026-10-22
- All focusable components use a 3px outline with 0px offset, including text-field wrappers.
- Removed inset focus exceptions; focused composites allow outline overflow and focused children paint above siblings. Geometry unchanged.

## 0.2.1 — 2026-10-22
- Text-input keyboard focus now outlines the neutral wrapper, including composed and collection inputs; sibling actions retain individual focus indicators.
- Appearance-only change: geometry contracts, resolvers, formulas and recipes remain unchanged.
- Updated local specimen hash from the published v0.2.0 baseline; no deployment performed.

## 0.2.0 — 2026-10-22
- Default curvature Soft; composite inset 0u.
- Chip-sized prefix/suffix/selector parts with real label wrappers, half control edge compensation and own-height minimum width.
- Composed-input height growth and physical per-axis nested curvature resolver.
- Chip-family composite options and currency trigger/listbox contract.
- Multiline rows moved to collection spacing and container curvature.
- Latest published specimen source included; portable dependency-free build/dev commands and local Codex setup guide.
- Added regression tests and updated manifests, recipes and manual verification cases.

## 0.1.0 — 2026-10-22
Initial extracted contracts, pure TypeScript geometry, composition recipes, agent entry point and frozen specimen.
