# Appearance

Geometry is independent of state appearance. Retain the same transparent border width in default, hover, selected, disabled and invalid states. If an invalid/focus indicator is needed, use a paint-layer indicator that does not add dimensions. Keyboard focus uses a 3px solid ink outline with 0px offset across all focusable components, including text-field wrappers. No divider lines where surface backgrounds already identify boundaries.

## Surface palette captured from the specimen
| Role | Light | Dark |
|---|---|---|
| surface-lowest | #e9e9e6 | #1a1a19 |
| surface-low | #efefec | #222221 |
| surface-mid | #f5f5f2 | #2b2b29 |
| surface-high | #fafaf7 | #333330 |
| surface-highest | #ffffff | #3d3d39 |
| ink | #20201f | #eeeeee |
| muted-ink | #62625d | #b8b8b1 |

Use lowest for canvas, mid for cards, low for composites/chips, highest for controls/selected options, and high for collection rows. Selected filter chips and attached buttons may invert ink and surface. Hover must not introduce layout changes. Filled input values do not gain a new background merely because they are nonempty. Plus/minus buttons remain transparent and circular.

Use system-ui for the interface and IBM Plex Mono weight 400 for technical specimen captions. Use intentional type hierarchy and grid alignment, following the Swiss/Vignelli-inspired direction. Do not introduce decorative font families into controls. Phosphor regular icons in demos are loaded via CDN; pin the version when integrating. The frozen specimen records its precise URLs.

These palette values reproduce the specimen; no contrast certification is implied. Test text, placeholders, disabled content and focus in both schemes. Future OKLCH adaptation must preserve roles and verified contrast, not only hue similarity.
