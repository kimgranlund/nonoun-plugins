---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Jakob N. / Nielsen Norman Group — Progressive Disclosure (nngroup.com/articles/progressive-disclosure), 2006"
  - "Nielsen Norman Group — Progressive Disclosure (video) (nngroup.com/videos/progressive-disclosure)"
  - "Interaction Design Foundation — Progressive Disclosure (glossary) (ixdf.org/literature/book/the-glossary-of-human-computer-interaction/progressive-disclosure)"
  - "Jakob N. / Laws of UX — Jakob's Law (lawsofux.com/jakobs-law)"
---

# Progressive Disclosure

Progressive disclosure is the single most reliable lever for taming interface complexity without amputating capability. The idea, formalized by Jakob N., is to **show the few options that matter to most users now, and defer the rest to a second layer that's available on request.** Done well, the novice sees a simple screen and the expert can still reach everything — the complexity isn't removed, it's _staged_. This reference covers the canonical Nielsen form, the crucial distinction from **staged** disclosure, and the discipline of choosing the split (which is where most attempts fail).

> Nielsen's definition: progressive disclosure **"defers advanced or rarely used features to a secondary screen, making applications easier to learn and less error-prone."** The mechanics: _"Initially, show users only a few of the most important options. Offer a larger set of specialized options upon request."_ A consequence he stresses: in such a design, **the very fact that something appears on the initial display tells users it's important.**

## When to use it

Reach for progressive disclosure when:

- **The full feature set would overwhelm the initial view,** but you can't simply delete the advanced parts (some users genuinely need them).
- **Usage is heavily skewed** — a small set of options serves the majority of sessions, and a long tail of options serves occasional power needs.
- **You want to raise learnability and lower error rate** without sacrificing depth. Nielsen's claim is concrete: progressive disclosure **"improves 3 of usability's 5 components: learnability, efficiency of use, and error rate."** Beginners aren't confronted with options they don't understand (fewer errors), and experts aren't slowed because the advanced layer is one obvious click away.

Do **not** reach for it when the "advanced" options are actually needed by most users on most visits — hiding frequently-used controls behind a disclosure is a net cost, not a simplification.

## Canonical form: two layers, one obvious door

The pattern is a **primary layer** (the core, always shown) and a **secondary layer** (advanced/rare, revealed on demand), connected by a clearly-labeled control with strong information scent about what lies behind it.

```text
Primary layer (shown to everyone)
┌───────────────────────────────────┐
│  [ the few most-used options ]    │
│                                   │
│  ▸ Advanced options               │  ← one obvious, well-labeled door
└───────────────────────────────────┘
            │ on request
            ▼
Secondary layer (advanced / rarely used)
┌───────────────────────────────────┐
│  [ the long tail of options ]     │
└───────────────────────────────────┘
```

Two requirements make or break it (Nielsen):

1. **Get the split right between initial and secondary features.** Put the frequently-used items up front; push the rest down. Too much on layer one defeats the purpose; the wrong things on layer one strand the majority in the advanced layer.
2. **Make the progression obvious.** The mechanism must be simple and clearly labeled, with strong "information scent" so users can predict what the second layer holds — otherwise they never discover it.

## Progressive vs. staged disclosure (don't conflate them)

These are different patterns with different shapes, and Nielsen separates them explicitly.

|  | **Progressive disclosure** | **Staged disclosure** |
| --- | --- | --- |
| Initial display | Core features | The features needed _first_ in a task sequence |
| Later display | Secondary / advanced features | Later steps, possibly equally important |
| Who reaches layer 2 | **Usually not** most users — they finish in the core layer | **Everyone**, unless the task stops early |
| Navigation shape | **Hierarchical** (drill down on demand) | **Linear** (proceed through ordered steps) |
| Primary benefit | Learnability — hide rarely-used depth | Simplicity _per step_ — fewer choices on screen at once |

The litmus test: **progressive disclosure is hierarchical and optional** (many users never open layer two, because they're done); **staged disclosure is linear and sequential** (users advance through steps because later steps are required to complete the task). A multi-step checkout that defers payment details to a later screen is _staged_ disclosure — not progressive. Nielsen notes staged disclosure "requires a thorough task analysis to understand which options are used together and which are better thought of as separate stages." (For the staged/wizard pattern in depth, see `forms.md`.)

## Defaults vs. advanced: the real design work

The visible-set decision is a usage-data problem, not an aesthetic one. The brief is to **choose defaults that serve the common case so well that most users never need the advanced layer at all** — defaults _are_ the primary act of complexity management here.

- **Decide the split from real usage frequency, not from the org chart or feature parity.** The question is "what do most users need on most visits?" — answered by analytics, not by which team owns which feature.
- **Sensible defaults beat exposed knobs.** Every option you can pre-set well (and let users change later) is an option that doesn't have to live on the initial screen. The advanced layer should hold genuine edge cases, not decisions you declined to make for the user.
- **Keep the door discoverable.** The failure twin of "too much on screen" is "the advanced layer is so hidden no one finds it." Strong scent and a stable, conventional location for the disclosure control (Jakob's Law) keep the expert path usable.
- **Don't bury frequently-used controls.** If logs show users routinely expand the advanced layer to do a common thing, that thing belongs on layer one — re-promote it.

## Anti-patterns

- **Hiding frequently-used options** in the advanced layer — punishes the majority to flatter the initial screen.
- **Confusing staged for progressive** — chopping a required linear task into "advanced" branches, or treating a genuinely optional depth layer as a mandatory step.
- **Low-scent disclosure controls** — a vague "More" with no hint of what's behind it; users can't predict the second layer and never open it.
- **Too many disclosure layers** — nesting reveal inside reveal inside reveal, so reaching a real control is an archaeology dig.
- **Disclosure as a substitute for cut decisions** — shoving everything you couldn't prioritize behind an "Advanced" toggle instead of choosing defaults. Disclosure manages complexity; it doesn't absolve you of reducing it.
- **Defaults that serve no real common case**, forcing most users into the advanced layer on every visit — the inverse of the pattern's intent.
- **Pure accordion sprawl** — a screen of a dozen collapsed sections is not progressive disclosure; it's an un-prioritized page hidden behind chevrons.

## Accessibility

- **Disclosure controls must be real, operable buttons** that toggle `aria-expanded` (`true`/`false`) and point at the controlled region (`aria-controls`) — follow the WAI-ARIA **Disclosure** pattern. A `<div>` with a chevron is not keyboard-operable.
- **Keyboard reachable and operable** (Enter/Space toggles; WCAG 2.1.1 Keyboard) — the expert path can't be mouse-only.
- **Move or manage focus sensibly** when the second layer appears, and don't trap it; revealed content should follow the trigger in the reading/Tab order.
- **State must not be conveyed by a rotating chevron alone** (WCAG 1.4.1, Use of Color / non-text cues) — `aria-expanded` carries the open/closed state to assistive tech.
- **Don't hide content needed to complete a required task** behind a disclosure that screen-reader or keyboard users might miss; reserve the advanced layer for genuinely optional depth, and ensure collapsed content is removed from the accessibility tree (not merely visually hidden while still focusable).

## Good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **The split** | Common controls buried in "Advanced"; layer one still cluttered | Most-used options on layer one; rare/advanced deferred, by usage data |
| **Pattern fit** | Required linear steps mislabeled as optional "advanced" branches | Hierarchical optional depth; staged disclosure used for required sequences |
| **Information scent** | A bare "More…" that hides its contents | Labeled door predicting the second layer ("Advanced shipping options") |
| **Discoverability** | Advanced layer so hidden experts can't find it | Conventional, scent-rich control experts reach in one obvious click |
| **Defaults** | Few/poor defaults; users hit the advanced layer every visit | Strong defaults serve the common case; most users never open layer two |
| **Depth** | Reveal nested in reveal nested in reveal | One primary layer, one secondary; flat and predictable |
| **A11y** | Chevron `<div>`, color-only state, mouse-only toggle | ARIA disclosure button, `aria-expanded`, keyboard-operable, managed focus |
