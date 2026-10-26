# Page rhythm verification, 2026-10-09

The reference-sheet generator emitted flat main children with no page-boundary spacing owner. Default heading margins created 16px after Authority but 0px between the preceding tiles and Authority. Ad hoc sheet margins also competed with shared composition rules.

## Changes

Shared opt-in page composition uses local geometry inset u: page sections 6u, section header/body 3u, heading/description 1u. At default u=8px these resolve to 48/24/8px. Existing card padding/major/content/tight relationships remain 4u/3u/2u/1u (32/24/16/8px). One parent owns each gap; direct-child block margins are reset only within these composition classes.

The generator now emits semantic heading and section groups. Native disclosure content has its own wrapper: 2u below its summary, 3u between content groups, 1u within heading groups. SKILL.md routes page-boundary work to product-foundation.md; the style contract, build workflow, sheets workflow and page-rhythm recipe carry the same rules.

## Evidence

- Authority boundary: 0px before / 16px after became 48px before / 8px after, independently measured in Chromium.
- Page rhythm: 30 cases (five pages, two widths, three sizes), including expanded disclosures; three deliberately broken spacing controls detected.
- Reference sheets: source coverage/hashes, 20 responsive cases, navigation and bounded specimen interactions passed.
- Existing spacing suite: six cases and 30 negative controls passed.
- Product regression: 13 checks passed; final gate rejects untested behavior claims.
- Self-test: 26 checks passed.
- Desktop and mobile screenshots visually reviewed for grouping and hierarchy.

Evidence output: /Users/kimgranlund/.codex/skill-previews/wireframe-review/sheets/ (rhythm-verification.json, authority-spacing.json, rhythm-after-desktop.png, rhythm-after-mobile.png). Original screenshot: /tmp/wf-rhythm-evidence/before.png.

These are authored-fixture checks in Chromium, not proof of fresh-agent uptake, Safari parity, or a complete zoom/accessibility audit. A subsequent clean-context generation round should test whether agents choose the documented grouping and spacing rules without repair.
