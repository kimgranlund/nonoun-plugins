---
name: hackable-criterion
description: >
  Every text-on-surface pair the palette generator emits meets WCAG AA contrast (4.5:1) — a generated theme
  a designer can trust as accessible without hand-checking each pairing.
---
# Palette contrast — every pair clears WCAG AA

**Intent.** The generator emits a full theme (surfaces, text roles, states). **Every** text-on-surface pair
it produces must clear WCAG AA (4.5:1), so the output is accessible by construction.

**Non-goals.** WCAG AAA; non-text (icon/border) contrast.

```json
{ "title": "Palette contrast", "cell": "spec.system.hackable-criterion",
  "binds_rubric": "rubric.system.spec-quality",
  "acceptance_criteria": [ { "id": "cc-01", "check": "contrastRatio(defaultText, defaultSurface) >= 4.5" } ],
  "non_goals": [ "WCAG AAA", "non-text contrast" ] }
```
