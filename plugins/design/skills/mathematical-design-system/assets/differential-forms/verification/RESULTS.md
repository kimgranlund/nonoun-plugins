# Verification results — 0.2.2

Completed 2026-10-22: build and all 14 automated tests passed. Source focus declarations consistently use 3px solid ink outlines with 0px offset; inset composite exceptions removed. Geometry formulas unchanged.

Browser spot checks: keyboard focus on the middle segmented button paints beyond the composite without clipping or sibling occlusion; text-field wrapper shows the thicker zero-offset ring. Evidence: uniform-focus.png. Full component/state matrix and accessibility/contrast/responsive audits remain pending.

## Previous verification — 0.2.1

Executed 2026-10-22: local build and all 14 automated test groups passed.

Browser checks in the local in-app browser: Tab into the plain field shows one wrapper outline in dark scheme; pointer click clears it. Tabbing through email/number to the increase stepper shows an individual action outline. In light scheme, Shift+Tab from Website domain to Amount shows the composed wrapper outline; Shift+Tab again moves the ring to the currency trigger alone. Tab back through Amount to Website domain restores the appropriate wrapper ring. Screenshot: input-focus.png.

The implementation adds only outline and outline-offset using the existing focus paint values. No geometry contracts, resolver formulas, specimen formulas, borders, padding, or recipes changed. Default wrapper measurements were 32px high in the browser. Numerical tests do not establish visual or accessibility compliance.

Still pending: full input-focus matrix across densities, borders and curvature extremes; forced-colors verification; comprehensive responsive, contrast and assistive-technology audits. The specimen continues to calculate geometry separately from the pure resolvers.

## Baseline record

### 0.2.0

Executed 2026-10-22: `node scripts/build.mjs` and `node --test verification/*.test.ts` using Node 24.

14 test groups passed, 0 failed. Checks cover defaults, font sizes, border conservation, exposed labels, composite extremes, chip-sized popup residual geometry, composed-input growth and per-axis curvature, collection multiline spacing, manifest references, recipes and snapshot SHA256/build fidelity.

The captured source's currency popup was previously checked in the browser: trigger/options 24px at default settings, pointer selection and keyboard selection working. No new full visual matrix, TypeScript static check, contrast audit or assistive-technology audit was performed for this export. The local standalone wrapper is generated from the exact published source fragment. The specimen still computes its own geometry separately from the pure resolver modules.
