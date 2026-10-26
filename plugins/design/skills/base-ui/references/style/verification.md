# Base UI verification

Standalone UI checks are owned here and indexed in [checks.json](../checks.json). Run only the checks affected by a source change. The original scripts/check-*.mjs entry points in wireframe-review forward to these checks; they do not maintain a second implementation. Review controller, manifest, sheet and historical-evidence checks remain with the review tool.

Run scripts/check-kit.mjs for package/source integrity. Icon maintenance uses scripts/generate-icons.mjs --check and scripts/check-icon-generation.mjs NEW_OUTPUT. The latter detects stale rules, verifies explicit repair and requires preservation of cascade position and outside CSS bytes.

The relocation reused unchanged component assertions and CSS/recipe bytes. It does not establish fresh passes for every browser matrix. The existing state-applicability validator fails because the stepper declares current outside the shared vocabulary; this remains a recorded contract issue. Source-only select observation hashes were refreshed, with previous bytes retained in the migration report; browser-support claims were not changed.

Keep outputs under /private/tmp and preserve any evidence needed for delivery. Installed Safari, screen readers, physical touch, native zoom and platform forced-color rendering keep their previous limitations. See [ownership report](../../resources/reports/check-ownership-2026-10-11/report.md).
