---
date: 2026-06-03
coverage: deep
primary_sources:
  - "Luke Wroblewski. *Mobile First*. A Book Apart, 2011. ISBN 9781937557027. https://abookapart.com/products/mobile-first · https://www.lukew.com/resources/mobile_first.asp"
  - "Ethan Marcotte. \"Responsive Web Design.\" *A List Apart*, 25 May 2010 (the three ingredients: fluid grid, flexible images, media queries). https://alistapart.com/article/responsive-web-design/ — expanded in *Responsive Web Design*, A Book Apart, 2011."
  - "Steven Hoober. \"How Do Users Really Hold Mobile Devices?\" *UXmatters*, 18 February 2013 (1,333 observations; 49% one-handed; ~75% thumb-driven; origin of \"the thumb zone\"). https://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php"
  - "Apple. *Human Interface Guidelines* — Layout / Accessibility (minimum 44×44 pt hit target). https://developer.apple.com/design/human-interface-guidelines/"
  - "Google. *Material Design* — Accessibility / touch targets (minimum 48×48 dp). https://m3.material.io/foundations/designing/structure (M3) · https://m2.material.io/design/usability/accessibility.html (M2)"
  - "Samantha Ingram. \"The Thumb Zone: Designing For Mobile Users.\" *Smashing Magazine*, 19 September 2016 (popularized the easy/stretch/hard thumb-zone map from Hoober's data). https://www.smashingmagazine.com/2016/09/the-thumb-zone-designing-for-mobile-users/"
---

# Responsive & Mobile: designing for the device in the hand

Most product usage is mobile, touch-first, and one-handed — so the substrate every pattern renders onto is a small, variable, finger-operated viewport before it is ever a desktop window. This reference collects the durable patterns for that reality: mobile-first responsive layout (Wroblewski; Marcotte), touch ergonomics and the thumb zone (Hoober; Smashing), the platform-native touch-target and convention baselines (Apple HIG; Material Design), and how those compose into flows that work with a thumb on a train. It is tier **extended** — practitioner-consensus and platform guidance, broadly stable but more convention than law — and it sits beside the accessibility reference, which sets the non-negotiable AA floor underneath all of it.

> The discipline in one line: design for the smallest, most constrained, one-handed context _first_, then progressively enhance to larger screens and more capable input — because a layout that works thumb-first on a 320px phone almost always scales up, while a desktop layout almost never scales down.

## Mobile-first: a constraint that improves the whole product

"Mobile first," named by Luke Wroblewski (_Mobile First_, A Book Apart, 2011), is the practice of designing for the smallest, most limited device before the desktop. Wroblewski's argument is that the mobile context is not a degraded desktop — it is a forcing function with three benefits: it **forces focus** (a small screen has room only for what matters, killing feature bloat at the design stage), it lets you **capitalize on new capabilities** (location, camera, touch, sensors), and it **future-proofs** against the device mix, which has long since tipped mobile-majority. The method is _progressive enhancement_: start from the core content and the primary task that must work everywhere, then layer richer layout, interaction, and detail as screen size and input capability allow — the inverse of _graceful degradation_, where a full desktop design is stripped back and usually breaks.

## Responsive web design: the three ingredients

Responsive Web Design — Ethan Marcotte's term (_A List Apart_, 25 May 2010) — is the technique that makes one layout adapt fluidly to any viewport. Marcotte identifies three technical ingredients, and they are still the spine of the approach:

- **A fluid grid.** Layout sized in _relative_ units (percentages, and today `fr`, `%`, `rem`, viewport units) rather than fixed pixels, so columns reflow with the viewport instead of overflowing it.
- **Flexible images / media.** Media constrained to its container (`max-width: 100%`) so it scales down rather than forcing horizontal scroll.
- **Media queries.** CSS breakpoints (`@media`) that change the layout when the viewport crosses a threshold — and, mobile-first, written `min-width` so the base styles are the small-screen layout and each query _adds_ complexity upward.

Modern CSS extends the same philosophy with tools Marcotte's 2010 piece predates but which serve the identical goal — **container queries** (adapt to the _component's_ available width, not the viewport's, which is what component-driven UIs actually need), intrinsic layout via `flex`/`grid` with `minmax()` and `clamp()` for fluid type and spacing, and the `<picture>` element / `srcset` for responsive images. Breakpoints should follow the _content_, not a list of named device widths — add a breakpoint where the layout starts to look wrong, not where a particular phone happens to be.

## Touch ergonomics and the thumb zone

Touch is not mouse input shrunk down; it has a different error model and a different reachable area, and the canonical evidence is Steven Hoober's field study.

- **How phones are actually held (Hoober, UXmatters, 2013).** Across 1,333 street observations, **49%** of people used a one-handed grip, 36% cradled the device and tapped with the other hand, and 15% used both thumbs — and across all grips, **~75% of interactions were driven by the thumb**. The design consequence: the _thumb_, not a precise pointer, is the primary input device, and its comfortable reach is limited and arc-shaped.
- **The thumb zone (popularized by Smashing Magazine, 2016, from Hoober's data).** On a one-handed grip the screen divides into three ergonomic regions: an **easy / natural** zone (roughly the lower-centre, where the thumb rests), a **stretch** zone (mid and upper-middle, reachable with deliberate extension), and a **hard / "ow"** zone (the far top corners and opposite top edge, uncomfortable or impossible to reach without re-gripping). As phones have grown past 6", the easy zone has shrunk _relative_ to the screen and the top has moved further out of reach — making bottom-anchored controls more important, not less.
- **The design rule.** Put **primary, frequent, and confirming actions in the easy zone** (bottom and bottom-centre): bottom navigation bars, primary CTAs, the send/submit button, the in-reach FAB. Push **destructive or rare actions toward the hard zone**, where an accidental thumb-tap is unlikely. Top-of-screen controls (a back chevron, a title) are acceptable for _infrequent_ navigation but poor for anything done repeatedly. This is why the mobile pattern stack inverted over the last decade — bottom tab bars, bottom sheets, and reachability gestures all exist to bring targets into the thumb's arc.

## Touch-target sizing: the platform baselines

A target the thumb can reliably hit has a _minimum physical size_, and the two platform authorities set it — above the WCAG floor.

| Authority | Minimum touch target | Notes |
| --- | --- | --- |
| **Apple HIG** | **44 × 44 pt** | The long-standing iOS minimum tappable area; points scale across device pixel densities. |
| **Material Design** | **48 × 48 dp** | Android's minimum; Material recommends ~8dp spacing between targets so their touch areas don't overlap. |
| **WCAG 2.2 (2.5.8)** | **24 × 24 CSS px** (AA) | The _accessibility floor_, deliberately lower than the platform ergonomics — meet it as a minimum, but design to 44/48 on touch. |

The reconciliation: **44pt / 48dp is the design target on touch surfaces; 24px is the absolute WCAG floor.** A control can satisfy WCAG and still be frustrating to tap — size to the platform number, and ensure adequate _spacing_ so adjacent targets don't steal each other's taps (fat-finger error). Hover, by the way, does not exist on touch — never hide a primary affordance behind `:hover`, and provide an explicit tap target instead.

## Platform conventions: respect them (Jakob's Law on mobile)

Native platform conventions are the mobile expression of Jakob's Law (users expect your app to work like the other apps they already know — see the laws-of-ux reference). Diverging from them raises the interaction cost for no benefit. The conventions worth honouring:

- **Navigation.** iOS leans on a bottom tab bar plus a top navigation bar with a back chevron and edge-swipe-back; Android pairs bottom navigation with the system Back affordance and (in Material) a navigation drawer for breadth. Use the platform's standard rather than inventing a third model.
- **System gestures and safe areas.** Respect OS-reserved edge gestures (swipe-back, home-indicator swipe, notification pull) and lay out within **safe-area insets** so content isn't clipped by notches, rounded corners, or the home indicator.
- **Controls and sheets.** Prefer native-feeling pickers, switches, and **bottom sheets** (which rise into the thumb zone) over desktop-style dropdowns and centre-screen modals that force a re-grip.
- **Input and keyboards.** Set the right input type / `inputmode` and `autocomplete` so the correct on-screen keyboard appears and autofill works; keep the active field and its primary action above the keyboard, not hidden behind it.
- **One-handed reach.** For tall screens, lean on bottom-anchored chrome and OS reachability features rather than stranding actions in the hard zone.

## Composing it: a mobile/responsive flow checklist

Run this when designing or reviewing any flow that will be used on a phone — which is most of them.

```text
1. Mobile-first?         Was the smallest, one-handed, touch context designed FIRST and
                         enhanced upward — not a desktop layout squeezed down?
2. Fluid + breakpoints.  Relative units + min-width media/container queries; breakpoints
                         placed where the CONTENT breaks, not at named device widths.
3. Thumb zone.           Primary / frequent / confirming actions in the easy (bottom)
                         zone; destructive actions out of accidental thumb reach.
4. Target size & spacing. Touch targets ≥ 44pt (iOS) / 48dp (Android) — never below the
                         24px WCAG floor — with enough spacing to prevent fat-finger taps.
5. No hover dependence.  Every affordance has a tap target; nothing essential hides
                         behind :hover. Touch error model assumed, not pointer precision.
6. Platform convention.  Native nav model, system gestures, and safe-area insets
                         respected (Jakob's Law); bottom sheets over centre modals.
7. Input ergonomics.     Correct inputmode/autocomplete; active field and its action stay
                         above the on-screen keyboard.
8. Reflow + zoom floor.  Survives a 320px viewport and 200% text zoom with no horizontal
                         scroll or lost function (ties to the accessibility reference).
```

Note on tier: items 4 and 6 (platform numbers and conventions) and the thumb-zone map are practitioner/platform guidance that evolves with hardware and OS releases — verify Apple HIG and Material against their current published versions before treating a specific figure as fixed. The mobile-first and responsive principles (items 1-3, 5, 8) are durable.
