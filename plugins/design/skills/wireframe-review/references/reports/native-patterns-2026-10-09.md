# Native pattern implementation and verification, 2026-10-09

## Shipped paths

The shared native-patterns recipe supplies destination-link navigation using auto popover and explicit CSS anchors, a dialog opened/closed by native button commands, and exclusive named details. All consume the shared geometry and token CSS; decorative icons are local Phosphor SVGs. No page script is required for these native behaviors. Application navigation destinations and persistence remain consuming-page responsibilities.

The old details-based menu and its prototype runtime remain available for existing artifacts. Native panels use a different class and must not receive the legacy runtime. Missing anchor support falls back to a centered native popover; use the legacy recipe if anchored placement on older platforms is required. This is not an ARIA application menu or a universal legacy-browser solution.

## Verification

Run `node scripts/check-native-patterns.mjs PLAYWRIGHT OUTPUT`. The fixture consumes source CSS and markup. Page scripts are disabled; automation inspects state and applies test mutations. The matrix is three engines, two widths, three geometry sizes and two directions (light LTR, dark RTL), 36 cases, plus a broken-offset control for each engine.

Measured behavior includes native keyboard opening, half-inset gap, viewport containment, stable trigger geometry, destination-link focus, Escape dismissal/focus return, peer-panel and outside-click dismissal, named-accordion exclusivity, modal open/close/Escape and focus handling, scroll tracking, clipped-container escape, viewport-edge placement, and oversized-panel scrolling. Desktop and narrow screenshots accompany the results.

WebKit's default macOS key preference skips links with Tab; the test uses Option-Tab to include them. This is recorded, not hidden by adding tabindex to every link. Browser engine/version details and individual assertions are in the generated verification.json.

Output: /Users/kimgranlund/.codex/skill-previews/wireframe-review/native-patterns/. These are Playwright Chromium/Firefox/WebKit builds, not the user's installed Safari. Screen-reader, physical touch-device and full browser-zoom verification remain outside this evidence. No support claim is made for customizable select, interest invokers or CSS carousel markers; those remain research candidates.

The source-derived sheets reuse the native recipes for menu/dialog/accordion specimens. Source hashes, token index, select observations and packaged skill must be refreshed after source changes.
