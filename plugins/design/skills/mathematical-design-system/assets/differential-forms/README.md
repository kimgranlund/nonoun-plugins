# Differential Forms
Version 0.2.0 · 2026-10-22

A self-contained local Codex project: design contracts, typed geometry, composition recipes, agent rules and an editable specimen. Start with AGENTS.md and system.manifest.json.

## Run
Requires Node 24+. No dependencies or installation step.

```sh
npm test
npm run build
npm run dev
```

Open http://localhost:4173. Read docs/local-project.md for project setup and the suggested first Codex prompt.

## Current decisions
Border 0px; composite inset 0u; Soft curvature for controls and containers; label edge 1.5u and half that for chips. Composed-input adornments use chips, nested curvature and minimum width equal to own height. Currency uses a chip trigger and listbox. Multiline rows use collection/table spacing, independently of listboxes.

## Authority
Explicit task instructions > confirmed contracts > executable resolvers/tests > recipes > specimen. Reconcile contradictions explicitly. Contract changes require updated code, tests, documentation and changelog.

This is a geometry system and development specimen, not a production component library. Read docs/exceptions.md for accessibility and nesting limitations. The specimen retains separate formulas; changes must keep it aligned with the extracted geometry modules. Fonts/icons need CDN access. Numerical tests do not constitute a visual or accessibility audit.
