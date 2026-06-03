---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "W3C. *Web Content Accessibility Guidelines (WCAG) 2.2*. W3C Recommendation, 5 October 2023 (latest editor's revisions thereafter). https://www.w3.org/TR/WCAG22/"
  - "W3C Web Accessibility Initiative (WAI). \"What's New in WCAG 2.2.\" https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/"
  - "W3C WAI. \"WCAG 2.1/2.2 — Understanding\" docs, incl. *Understanding SC 1.4.3 Contrast (Minimum)*. https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum"
  - "W3C WAI. \"Introduction to Web Accessibility\" and \"WCAG 2 Overview\" (the POUR principles, conformance levels). https://www.w3.org/WAI/fundamentals/accessibility-intro/ · https://www.w3.org/WAI/standards-guidelines/wcag/"
---

# Accessibility (WCAG 2.2): the inclusion floor

Accessibility is not a feature tier or a late-stage audit — it is the floor every pattern in this library stands on. The authoritative reference is the W3C's **Web Content Accessibility Guidelines (WCAG) 2.2**, a W3C Recommendation since 5 October 2023, developed by the Web Accessibility Initiative (WAI). WCAG defines, testably, what makes web content usable by people with disabilities — visual, auditory, motor, cognitive, and situational. This file states the shape of the standard (POUR, the three levels, the conformance unit), fixes the **AA** bar that production work is held to, and pins the handful of criteria a product reviewer checks first: contrast, keyboard, focus, and target size. Treat AA as the minimum a shipped surface must clear, not the ceiling it aspires to.

> The standard in one line: WCAG organizes accessibility under four principles (POUR), states 87 testable success criteria graded A / AA / AAA, and the working bar for legal compliance and professional practice is **Level AA** — which means meeting **all 56** Level A _and_ AA criteria, since the levels are cumulative.

## POUR: the four principles

Every WCAG success criterion hangs off one of four principles. They are the mental model — if a design fails, it fails one of these, and naming which one frames the fix.

- **Perceivable.** Information and UI components must be presentable in ways users can perceive — it cannot be invisible to all their senses. Covers text alternatives for non-text content, captions and alternatives for media, content that adapts (reflow, orientation) without losing meaning, and sufficient contrast.
- **Operable.** UI components and navigation must be operable — every interaction must be possible by the input methods users actually have. Covers full keyboard operability, enough time, no seizure-inducing flashing, navigable structure (focus order, headings, link purpose), and input modalities including target size and pointer/drag alternatives.
- **Understandable.** Information and the operation of the UI must be understandable — readable, predictable, and forgiving. Covers readable language, consistent and predictable behaviour (consistent navigation, consistent help), and input assistance (labels, error identification, error suggestion, redundant-entry relief).
- **Robust.** Content must be robust enough to be reliably interpreted by a wide variety of user agents, including assistive technologies — and to keep working as they evolve. Covers valid, well-formed markup and correct name/role/value exposure (the basis of the accessibility tree that screen readers consume; SC 4.1.2 _Name, Role, Value_).

The hierarchy is: **4 principles → 13 guidelines → 87 success criteria (A/AA/AAA) → techniques** (advisory ways to satisfy a criterion).

## The three conformance levels, and why AA is the bar

WCAG grades each success criterion at one of three levels, and they are **cumulative** — AA includes all of A; AAA includes all of A and AA.

- **Level A** — the minimum; content is broadly inaccessible without it (e.g. keyboard operability, text alternatives, no keyboard traps).
- **Level AA** — the **working standard**: the level most accessibility law and procurement points at (e.g. the EU EN 301 549 baseline, and the de-facto US Section 508 / ADA reference), and the level professional teams ship to. Reaching AA means satisfying every A and AA criterion — **56** criteria in total in WCAG 2.2.
- **Level AAA** — enhanced; W3C explicitly notes it is _not recommended as a blanket requirement_ for whole sites because some content cannot meet all AAA criteria. Apply AAA selectively where the audience warrants it.

**The conformance unit is the page (or a complete process), not a component.** A "fully conformant" page meets _all_ applicable criteria at the chosen level — a single uncaptioned video or one keyboard trap breaks conformance for the whole page. There is no partial credit at the page level; this is why accessibility must be designed in, not bolted on.

## The criteria a product reviewer checks first

These are the high-frequency AA criteria that catch most real defects in product UI. Numbers and thresholds are from WCAG 2.2; the contrast ratios are unchanged from WCAG 2.1.

### Contrast (Perceivable)

- **1.4.3 Contrast (Minimum) — AA.** Text and images of text need a contrast ratio of at least **4.5:1**, except **large text** (≥ 18pt, or ≥ 14pt bold — i.e. ~24px / ~18.66px bold) which needs **3:1**. Incidental, disabled, and pure-decoration text is exempt.
- **1.4.11 Non-text Contrast — AA.** UI components (their states and boundaries) and graphical objects needed to understand content need at least **3:1** against adjacent colour. This is what holds button edges, input borders, icons, and focus indicators to a visible standard.
- **1.4.1 Use of Color — A.** Colour must not be the _only_ visual means of conveying information (e.g. an error shown only by turning a field red fails; add text or an icon).

### Keyboard (Operable)

- **2.1.1 Keyboard — A.** All functionality must be operable through a keyboard interface, without requiring specific timings for keystrokes. If you can do it with a mouse, you must be able to do it with a keyboard.
- **2.1.2 No Keyboard Trap — A.** Focus that can move _into_ a component with the keyboard must be able to move _out_ of it the same way. Modal dialogs and custom widgets are the usual offenders.
- **2.4.3 Focus Order — A** and **2.4.7 Focus Visible — AA.** Focus moves in a meaningful, logical order, and the keyboard focus indicator is always visible.

### Focus appearance and obscuring (Operable, new in 2.2)

- **2.4.11 Focus Not Obscured (Minimum) — AA.** When a component receives focus, it is _not entirely_ hidden by author-created content (e.g. a sticky header must not cover the focused element). New in WCAG 2.2.
- **2.4.13 Focus Appearance — AAA.** Specifies a minimum _size and contrast_ for the focus indicator: the indicator must be at least as large as the area of a **2 CSS-pixel-thick perimeter** of the component, with a **3:1** contrast between focused and unfocused states. (Note: this criterion is **AAA** in WCAG 2.2 — a common error is to cite it as AA. Aim for it as best practice; it is not part of the AA bar. Labeled to avoid the frequent miscitation.)

### Target size and pointer (Operable, new in 2.2)

- **2.5.8 Target Size (Minimum) — AA.** Pointer targets are at least **24×24 CSS pixels**, unless an exception applies (e.g. an equivalent larger target exists, the target is inline in a sentence, spacing creates a 24px clearance circle, or the presentation is user-agent-determined). New in WCAG 2.2 — and notably _below_ the platform-native ergonomic minimums (44pt iOS / 48dp Android; see the responsive-mobile reference), so 24px is a floor, not a target you should design _to_.
- **2.5.7 Dragging Movements — AA.** Any drag interaction must have a single-pointer alternative that is not a drag (e.g. tap-to-select then tap-to-place). New in WCAG 2.2.
- **2.5.1 Pointer Gestures — A** and **2.5.3 Label in Name — A.** Multipoint/path-based gestures need a simple alternative; the visible label of a control must be contained in its accessible name (so speech-input users can target it).

### Understandable and Robust spot-checks

- **3.3.1 Error Identification — A / 3.3.2 Labels or Instructions — A / 3.3.3 Error Suggestion — AA.** Errors are identified in text, inputs are labelled, and corrections are suggested where known.
- **3.2.6 Consistent Help — A** and **3.3.8 Accessible Authentication (Minimum) — AA.** New in WCAG 2.2: help is in a consistent place; and authentication must not depend on a _cognitive function test_ (remembering/transcribing) without an alternative — passwords with paste support and passkeys pass; a "retype this from memory" step fails.
- **4.1.2 Name, Role, Value — A.** Every UI component exposes a correct name, role, state, and value to assistive tech — the contract that makes custom components legible to screen readers.

## The "does it clear the floor?" checklist

Run this before treating any interactive surface as shippable. Each item is an AA criterion (or noted otherwise); a failure on any one breaks page-level conformance.

```text
1. Keyboard-only pass.   Tab through the whole surface with no mouse. Can you reach
                         AND operate every control? Can you always escape? (2.1.1, 2.1.2)
2. Focus visible.        Is the focused element always clearly indicated and never fully
                         hidden behind sticky/overlay content? (2.4.7, 2.4.11)
3. Contrast.             Text ≥ 4.5:1 (large ≥ 3:1); component borders / icons / focus
                         rings ≥ 3:1. Is meaning ever carried by colour alone? (1.4.3,
                         1.4.11, 1.4.1)
4. Target size.          Pointer targets ≥ 24×24 CSS px (AA floor) — and ideally the
                         44pt / 48dp platform ergonomic size on touch. (2.5.8)
5. No drag-only / gesture-only. Every drag or path gesture has a single-tap
                         alternative. (2.5.7, 2.5.1)
6. Names & errors.       Inputs labelled; errors identified in text with a suggested
                         fix; visible label is in the accessible name. (3.3.1-3, 2.5.3)
7. Structure & roles.    Headings/landmarks present; custom widgets expose correct
                         name/role/value to AT. (1.3.1, 4.1.2)
8. Reflow & zoom.        Content reflows to a 320px-wide viewport and survives 200%
                         text zoom without loss of content or function. (1.4.10, 1.4.4)
```

Conformance is page-level and AA is cumulative: clearing this list is necessary, not automatically sufficient, but a surface that fails any item is below the inclusion floor and is a defect to fix before it ships.
