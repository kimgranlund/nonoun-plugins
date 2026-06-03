---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Jakob N. / Laws of UX — Jakob's Law (lawsofux.com/jakobs-law). Formulated 2000."
  - "Nielsen Norman Group — The Difference Between Information Architecture (IA) and Navigation (nngroup.com/articles/ia-vs-navigation)"
  - "Nielsen Norman Group — Menu-Design Checklist: 17 UX Guidelines (nngroup.com/articles/menu-design)"
  - "Nielsen Norman Group — Breadcrumb Navigation (nngroup.com/articles/breadcrumbs)"
  - "Nielsen Norman Group — Tabs, Used Right (nngroup.com/articles/tabs-used-right)"
  - "Nielsen Norman Group — Information Architecture: 3 Key Models / Flat vs. Deep Hierarchies (nngroup.com/topic/information-architecture)"
---

# Navigation & Information Architecture

Information architecture (IA) and navigation are not the same thing, and the most common navigation defects are really IA defects wearing a UI costume. NN/g draws the line cleanly: **IA is the structure** — how content is categorized, labeled, and related; **navigation is the UI** that lets users move through that structure. Get the IA wrong and no menu styling can save you; get it right and even a plain menu works. This reference is the working manual for the interaction-layer patterns that surface an IA — menus, tabs, breadcrumbs, the hub-and-spoke shape — and for the one law that governs all of them: **users arrive with expectations formed everywhere else.**

> **Jakob's Law (Nielsen, 2000):** _"Users spend most of their time on other sites. This means that users prefer your site to work the same way as all the other sites they already know."_ The cumulative effect of meeting that expectation is lower cognitive load — users spend mental energy on their task, not on decoding your interface. The cost of violating it is paid in every session.

## When to use which navigation pattern

Navigation is not one control; it is a small family, each suited to a different relationship between items. Reach for the pattern that matches the structure, not the one that looks best.

| Pattern | Use when | Reach for it because |
| --- | --- | --- |
| **Global / primary nav (menu bar)** | The site has a stable top-level structure users return to from anywhere | It is the persistent map — it communicates scope ("what is here") and supports re-orientation |
| **Local / section nav** | Users explore within a section and need to move laterally between siblings | Prevents "pogo-sticking" up to a hub and back down just to reach a neighbor |
| **Tabs** | A few mutually exclusive views of the _same_ object/page, one shown at a time | Chunks lengthy content; cheap switching between parallel sections |
| **Breadcrumbs** | Deep hierarchy (3+ levels), especially with traffic arriving on deep pages | Answers "where am I?" and offers one-click ascent to ancestors — secondary, never primary |
| **Hub-and-spoke** | Discrete tasks/tools that don't relate to each other, accessed from a central home | Forces a deliberate return to the hub between tasks; classic mobile-app home screen |
| **Utility nav** | Account, search, cart, settings — cross-cutting, not part of the content hierarchy | Kept visually distinct from content nav so it doesn't compete with topical browsing |

## Canonical form: the menu

The menu is the load-bearing navigation control, and NN/g's menu-design guidance converges on a few non-negotiables.

- **Make navigation visible — don't hide it.** NN/g is blunt that "the hamburger menu (or any form of hiding the navigation categories under a single menu) is not appropriate for desktop." The rationale: **"Out of sight means out of mind."** Hidden navigation also strips the menu of its second job — communicating who you are and what you offer. Behind-the-icon navigation reliably lowers discoverability and engagement; reserve it for genuinely space-constrained mobile.
- **Use clear, descriptive labels.** Avoid "made-up words, internal jargon, or abstract high-level categorization." Labels must describe the content, feature, or resource in the user's words — strong _information scent_ so a glance predicts what's behind the link.
- **Signal the current location.** "Where am I?" is fundamental, and NN/g calls failing to indicate the current location "probably the single most common mistake we see on website menus." Highlight the active item; reinforce with breadcrumbs and the page heading.
- **Group related items; keep depth shallow.** Cascading multi-level dropdowns become error-prone beyond two tiers (mis-clicks, menus that close on the way down). Prefer a flatter grouping that a user can scan, not a maze they must thread.

## Canonical form: tabs

Tabs present **parallel sections of one object, one visible at a time.** NN/g's "Tabs, Used Right" gives the fit test and the build rules.

Use tabs when content has clear groupings, there are _few_ groupings, importance is roughly comparable, and — critically — **users do not need to see two sections at once.** If users must compare across sections, tabs are the wrong control: switching back and forth taxes short-term memory and raises interaction cost.

```text
┌─────────┬──────────┬──────────┐
│ Details │ Reviews  │ Shipping │   ← one row, never stacked
├─────────┴──────────┴──────────┤
│  [ active panel content ]     │   ← panel sits directly below the row
└───────────────────────────────┘
```

Build rules from NN/g:

- **Prominently highlight the selected tab**, using at least two indicators (e.g., color _and_ a connecting line/bold) — not color alone.
- **Keep unselected tabs visible** so users are reminded the other sections exist.
- **Use a single row** — "websites and simple apps should avoid stacking tab lists." Place tabs _above_ the panel; vertical or bottom arrangements get overlooked.
- **Short labels (1–2 words)**, no ALL CAPS (hurts legibility).
- **Don't mix in-page tabs with navigation tabs** in one control — inconsistent behavior disorients users.

## Canonical form: breadcrumbs

Breadcrumbs are "a list of links representing the current page and its 'ancestors'," shown in one line below the global nav. They support **wayfinding** by exposing the hierarchy as a clickable path.

- **They are location-based, not history-based.** NN/g: breadcrumbs "are not intended to show the history of pages traversed during a session… they are intended to show the hierarchical structure of the site." History trails grow "long and confusing, with a lot of repetition."
- **They are secondary, never primary.** "Breadcrumbs should not replace the global navigation bar or the local navigation within a section." They augment.
- **Form rules:** start with a Home link; the current page is the last item and **is not a link**; include only real pages (not logical categories that have no page); in polyhierarchies, show a single canonical path. On mobile, keep tap targets ≥ ~1cm and consider truncating to the final levels rather than wrapping.

NN/g's testing finding: breadcrumbs deliver "many benefits and no downsides" for secondary navigation — a rare unambiguous verdict.

## Canonical form: hub-and-spoke

In a hub-and-spoke structure, a central home (the **hub**) links out to discrete destinations (the **spokes**), and each spoke routes back to the hub rather than across to its siblings. It is the classic smartphone home-screen model: tap an app (spoke), do the task, press Home (hub) to switch.

- **Best for unrelated, self-contained tasks.** The forced return to the hub is a feature when the spokes have nothing to do with each other — it keeps each task in its own focused context.
- **It is a poor fit when users move _between_ related sections,** because every lateral move becomes a two-hop detour through the hub. There, add **local/section navigation** so siblings link directly.

This is one of the three IA structures NN/g teaches alongside **hierarchical** (parent/child trees — the default for most content sites) and **sequential** (a guided linear path — checkout, onboarding, wizards). A **matrix** structure lets users move along multiple dimensions (e.g., filter by both price and color) rather than only up/down a tree — the conceptual basis of faceted navigation (see `search.md`). Pick the structure from the content's real shape, then choose navigation controls that express it.

## IA depth: flat vs. deep

A standing IA trade-off NN/g frames directly: **flat** hierarchies (many siblings, few levels) minimize clicks-to-content and keep the structure scannable but can overwhelm a single level with too many choices; **deep** hierarchies (few siblings, many levels) tidy each screen but bury content and multiply the chances to take a wrong turn. There is no universal winner — the right depth depends on how many top-level categories users can meaningfully distinguish. The practical bias for most sites is **as flat as the content allows**, because clicks are cheap but getting lost is expensive.

## Anti-patterns

- **Hidden desktop navigation (hamburger by default).** Trades a few pixels for measurably lower discoverability — "out of sight, out of mind."
- **No "you are here" indicator.** NN/g's single most common menu mistake; users who arrive on a deep page can't orient.
- **Tabs for comparable content.** If the user needs both panels at once, tabs force memory-juggling — use a single page or side-by-side layout.
- **History-trail breadcrumbs.** Repetitive, confusing, and they betray the user's mental model of breadcrumbs as a hierarchy.
- **Breadcrumbs as the only navigation.** They augment; they never replace global/local nav.
- **Jargon and clever labels.** "Synergy Hub" has no information scent; users can't predict what's behind it. Label in the user's words.
- **Mystery-meat / icon-only nav** without text labels, forcing hover or trial-and-error to learn what each item does.
- **Over-deep dropdowns (3+ cascading levels)** — mis-clicks and accidental dismissals climb sharply past two tiers.
- **Reinventing conventions for novelty's sake** — a direct Jakob's-Law violation; users pay the learning cost on every visit.

## Accessibility

- **Landmark the structure.** Wrap primary navigation in a `<nav>` element (an implicit `navigation` landmark); when a page has more than one `<nav>`, give each an `aria-label` (e.g., "Primary", "Breadcrumb") so screen-reader users can tell them apart and jump between them.
- **Provide a skip link** ("Skip to main content") as the first focusable element so keyboard and screen-reader users can bypass a long, repeated menu.
- **Breadcrumbs:** use an ordered list inside `<nav aria-label="Breadcrumb">`; mark the current page with `aria-current="page"` (this is the accessible equivalent of "you are here").
- **Tabs follow the WAI-ARIA tabs pattern:** `role="tablist" / tab / tabpanel`, the active tab carries `aria-selected="true"`, arrow keys move between tabs, and only the active tab is in the Tab order (a roving tabindex). Don't ship visual-only tabs.
- **Current-page signaling must not be color-only** (WCAG 1.4.1, Use of Color) — pair the color with weight, an underline, or `aria-current` so it survives low vision and color blindness.
- **Menus need adequate target size and visible focus** so keyboard and motor-impaired users can operate them (WCAG 2.4.7 Focus Visible; 2.5.5/2.5.8 Target Size).

## Good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Conventions (Jakob's Law)** | Novel nav metaphor users must learn from scratch | Familiar placement/behavior so existing mental models transfer |
| **Visibility** | Desktop nav hidden behind a hamburger | Primary categories shown; nav communicates scope at a glance |
| **Labels** | Jargon / invented category names, no scent | Plain, user-language labels that predict their destination |
| **Orientation** | No active-state, no breadcrumb on a deep page | Highlighted current item + `aria-current` breadcrumb |
| **Tab fit** | Tabs used for content users must compare | Tabs only for one-at-a-time parallel views; single row |
| **Breadcrumb type** | Session-history trail, or breadcrumbs as the only nav | Location-based hierarchy path, secondary to global/local nav |
| **IA structure** | Structure forced onto a template that doesn't fit the content | Structure (hierarchical / sequential / hub-and-spoke / matrix) chosen from the content's real shape |
| **Depth** | Deep tree that buries content many clicks down | Depth tuned to distinguishable categories; as flat as content allows |
| **A11y** | Color-only current state; no landmarks; no skip link | `<nav>` landmarks, skip link, ARIA tabs, non-color "you are here" |
