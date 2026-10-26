# Context and example consolidation, 2026-10-09

Scope: installed personal wireframe-review skill, its maintained previews and portable package. Historical evaluation artifacts are retained. No upstream Ultimate Tokens engines or vendored foundation snapshots were changed.

## Requirements and evidence

| Requirement | Authoritative implementation/context | Verification |
| --- | --- | --- |
| Compact product h1-h6, semantic ranks preserved | wireframe.css; style/contract.json headingContexts; product-foundation heading context | 18 heading cases, 3 negative controls across Chromium/Firefox/WebKit |
| Breadcrumb baseline and wrapping | wireframe.css; components contract/context | 36 cases and 3 regression controls |
| Contained native disclosure with geometry header and Phosphor caret | wireframe.css; components contract/context; native-patterns and components recipes | 36 no-JS native cases; six color-popover cases verify expanded body inside outer border |
| Popover/control radius parity and half-inset placement | wireframe.css; navigation-menu and compact popover contracts | native pattern and sheet geometry checks |
| Bulk palettes, OKLCH precision/alpha, source provenance | build-sheets; colorNotation contract; reference-sheets workflow | 291 declarations; 582 light/dark conversions checked against source RGBA within one byte; original source excerpts retained |
| Swatch button contains equal light/dark halves | sheet generator/workflow | sm/md/lg radius, equal-width and touching-edge assertions; native opening |
| Pairing samples and sheet cards consume shared card geometry | sheet generator/workflow | pair padding/border/radius parity at three sizes; page rhythm |
| Rebuilt examples and maintained outputs | build-demo-suite, component/native recipes, sheet builder, starter builder | nine scenarios, 360 rendered page proposals; catalog, spacing, product, sheets and static-select gates |
| Skill/package consistency | concise SKILL routing; owning docs/contracts; token index and observations | validator; 26 self-tests; source hashes; offline glyph and legacy-removal guards; package byte parity |

A WebKit narrow-screen test exposed an offscreen bottom Close control after scrolling expanded source details. The color popover now keeps Close in a sticky header. Pointer, keyboard, Escape and outside dismissal pass in all three tested engines with page scripts disabled.

Evidence files live under the wireframe-review preview directory: headings/verification.json, breadcrumbs/verification.json, native-patterns/verification.json, components/report.json and sheets/{verification,popover-verification}.json. The final consolidation audit binds source and maintained HTML hashes.

## Limits

These are authored-example and browser regression checks, not a new clean-context generation round or screen-reader certification. Browser engines are Playwright Chromium, Firefox and WebKit, not the installed Safari application. Existing sheet gaps remain explicit; this task does not fabricate missing per-token usage guidance. Vendored legacy color excerpts remain verbatim even though new literal/display notation is OKLCH.
