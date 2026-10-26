# Shared foundations

Read for a new artifact. This file owns shared reasoning boundaries; artifact-contract.md owns review structure and interchange. Detailed facts stay in their owning reference or executable source.

Start from intended user progress and available product capabilities. Reconcile gaps and tradeoffs rather than treating either as a fixed page recipe. Use design/index.md to find the relevant experience profile. Marketing may benefit from varied narrative rhythm; repeated product tasks usually benefit from consistent structures. Measures are hypotheses until observed, not claims of impact.

Default to three substantively different approaches, not cosmetic variants. Preserve coherent flows and identify incompatible mixed choices. Use realistic content lengths and clearly mark fictional evidence or unimplemented operations.

Semantic color roles own scheme behavior. Geometry owns control sizing and centered icon slots; typography exports own editorial scales. Layout owns container insets and sibling gaps. One parent owns sequential spacing. Navigation and content share width/gutters; full-width surfaces may contain narrower reading blocks. Controls keep their native semantics, stable borders and visible focus.

Bound foundational choices; allow novel composition. Reuse component families and relationships without requiring a catalog entry for every new arrangement. Explain only material exceptions. Do not invent exported roles or promise implementation support based on a contract alone.

For styling, read artifact-styling.md and the selected leaf, not every example. For document/scoped context, see style/bootstrap.md. For component grammar, see style/composition.md. These references own details; this page does not reproduce their inventories.

## Applying the foundations in generated HTML

The builder already supplies control geometry and semantic colors. Manifest CSS composes those roles; it must not replace the shared system with literal palette colors or fixed button/input dimensions. Brand direction uses semantic aliases. Verify the rendered artifact itself changes foreground and background correctly in light and dark, not just the surrounding review shell. Use `button__root` for button-like anchors so its foreground matches its fill. Native selects keep the shared geometry height and line-height; avoid adding padding that clips their text. Record any deliberately necessary foundation override with its reason.

Composed page sections are fragments, not independent application roots. Do not give each leaf a viewport/minimum page height. A grid can arrange only its actual children; verify the rendered page composition supports the layout described in the rationale.
