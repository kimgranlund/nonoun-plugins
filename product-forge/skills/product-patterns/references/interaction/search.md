---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Nielsen Norman Group — Filters vs. Facets: Definitions (nngroup.com/articles/filters-vs-facets)"
  - "Nielsen Norman Group — Ecommerce Search UX, including Faceted Search (report) (nngroup.com/reports/ecommerce-ux-search-including-faceted-search)"
  - "Nielsen Norman Group — Designing Search Suggestions / autocomplete (nngroup.com/videos/designing-search-suggestions)"
  - "Nielsen Norman Group — Mobile Faceted Search with a Tray (nngroup.com/articles/mobile-faceted-search)"
  - "Nielsen Norman Group — The Difference Between Information Architecture (IA) and Navigation (nngroup.com/articles/ia-vs-navigation)"
---

# Search, Filtering & Faceting

Search is the escape hatch users reach for when browsing fails — and the moment a search experience breaks, it breaks hard, because the user has already told you exactly what they want and you've come up empty. This reference covers the four moves that make search usable: the search input itself, **autocomplete** that lowers the cost of asking, **filtering/faceting** that narrows a result set, and the **zero-results** state that decides whether a failed query ends the session. The governing tension, per NN/g, is that **browsing categories is often faster and easier than composing a good query** — so search and navigation are partners, not substitutes.

> NN/g's load-bearing distinction: **a filter** "analyzes a given set of content to exclude items that don't meet certain criteria," while **faceted navigation** "extends the idea of filters into a complex structure that describes all the different aspects of an object," letting users narrow along many dimensions at once. Faceting is filtering raised to a multi-dimensional, combinable system.

## When to use which search affordance

| Affordance | Use when | Notes |
| --- | --- | --- |
| **Prominent search box** | Large/ deep inventory; users arrive with a specific target in mind | Open text field, visible (not behind an icon) on content-heavy/commerce sites |
| **Autocomplete / suggestions** | Queries are long, error-prone, or hard to spell; mobile typing is costly | Reduces typing and mis-spelling; most valuable exactly where input is hardest |
| **Scoped search** | The same query means different things in different sections | A scope selector ("in: Docs / Issues") prevents irrelevant cross-section noise |
| **Filters** | A result/listing set needs trimming on one or two attributes | Simple exclusion; good when the attribute space is small |
| **Faceted navigation** | Items have many describable attributes users combine (price × brand × size) | The matrix-IA pattern; show controls _and_ results together |
| **Sort** | The right items are present but in the wrong order | Keep visually separate from filters — conflating the two is a known error |

## Canonical form: the search input

- **Make it visible and obvious.** On any site where search is a primary path (commerce, docs, large content libraries), the search field should be present and recognizable as a text input — not collapsed behind a magnifying-glass icon that costs a click to discover.
- **Don't make browsing depend on it.** NN/g's finding is that "using navigation categories is often faster and easier for users than generating a good search query." Search complements a navigable IA (see `navigation-ia.md`); it does not excuse a missing one.
- **Be forgiving by default.** Tolerate typos, plurals/singulars, and synonyms; treat the query as intent to interpret, not a literal string to match. The harshest failure (zero results) is frequently a tolerance failure, not a true "we don't have it."

## Canonical form: autocomplete (search suggestions)

Autocomplete offers query completions as the user types. NN/g's guidance:

- **It pays off most where input is hardest.** Autocomplete is "more valuable on mobile than on desktop: it reduces the typing burden precisely when that burden is highest." It also rescues users who can't spell the term.
- **Suggestions must lead somewhere real.** "Useful search suggestions lead to relevant results" — never suggest a query that dead-ends in zero results.
- **Make suggestions visually distinct from the typed query** so users can tell their input from the system's offer, and can scan the list quickly.
- **Keep the list short and ranked by likely intent;** support keyboard navigation (arrow + Enter), and don't hijack the user's own text mid-edit.

```text
┌──────────────────────────────────────┐
│ Search:  runn|                    [×] │   ← user's typed text
├──────────────────────────────────────┤
│  running shoes            (popular)   │   ← suggestion, visually distinct
│  running shorts                       │
│  running watch                        │
└──────────────────────────────────────┘
       ↑ every suggestion must resolve to real results
```

## Canonical form: filtering and faceting

Faceted navigation is the workhorse of large catalogs. NN/g attributes its power to one design move: **"displaying the facet controls and the results at the same time," so the effect of each filter is instantly visible.** The user narrows and sees the consequence without a round-trip.

Design rules drawn from NN/g's ecommerce-search research:

- **Show applied filters explicitly, and make them individually removable.** A persistent "applied filters" area (chips/tokens with an × each, plus a "clear all") is how users keep a mental model of what's currently constraining the set. NN/g flags failure to surface applied filters as a common, costly omission.
- **Separate filtering from sorting.** They are different operations and "confusing these functions is easy" — keep them in distinct, clearly-labeled controls.
- **Tailor facets to the category being viewed.** Filter dimensions should be "prioritized logically and specifically for the items being viewed," not a one-size-fits-all template stamped across every category (shoes need size; books need author).
- **Keep results live as facets change** so the user sees the set shrink/grow as they go (the instant-feedback property that makes faceting feel powerful).
- **On mobile, use a push-out tray.** NN/g's recommended mobile pattern shows "the facet controls as a 'push-out' style tray on top of the search results," solving the small-screen problem of showing both controls and results — and applying filters live, with a count of matching results, before the user commits.

Research signal NN/g reports: users complete tasks meaningfully faster with faceted navigation than with keyword search alone, and users who successfully apply filters are far more likely to find what they want and feel satisfied.

> **Single-source / approximate figures.** Specific magnitudes seen in secondary write-ups of NN/g's commerce research (e.g., "25–50% faster with facets," "~68% of top sites display applied filters") are reported second-hand and approximated here; treat them as directional. The qualitative findings — facets beat keyword-only search; applied-filter visibility is widely missed — are well-attested in NN/g's primary report.

## Canonical form: the zero-results state

A zero-results page is, in NN/g's framing, **the single most damaging moment in a search experience** — the user expressed precise intent and the system replied "nothing." A blank "0 results found" ends sessions. A good zero-results state does five things:

1. **Confirm what was searched** and make the query editable in place — most zero-results are a typo or an over-narrow filter, and the fastest fix is re-editing, not re-starting.
2. **Explain the likely cause in plain language** ("No results for _runing shoes_") rather than a bare count.
3. **Offer a recovery path:** spelling correction / "did you mean…", relaxing the most restrictive filter, or broadening the scope.
4. **Show something useful anyway:** popular categories, best-sellers, recent searches, or partial matches — never a dead end.
5. **For over-filtered sets, surface which facet to loosen** (and ideally how many results loosening it would yield), so the user can climb back to a non-empty set.

## Anti-patterns

- **Search hidden behind an icon** on a site where search is a primary path — a discoverability tax for no real space saving on desktop.
- **Literal, intolerant matching** that returns zero for a plural, a typo, or a synonym you actually stock.
- **Suggestions that dead-end** in zero results — autocomplete promising things the index can't deliver.
- **Applied filters invisible.** Users lose track of why the set is so small and can't undo a single constraint.
- **Filter/sort conflation** — putting "Price: low → high" inside the filter list so users can't tell narrowing from reordering.
- **Universal facet templates** — showing "Author" on a shoe category because every page reuses the same filter set.
- **A bare "0 results" dead end** — no query echo, no suggestion, no fallback content, no facet to loosen.
- **Mobile facets that require leaving the results, applying blind, and coming back** instead of a live tray with a result count.
- **Hijacking the query box** — autocomplete that overwrites or reorders what the user is actively typing.

## Accessibility

- **Label the field** with a real, programmatic label (`<label>` or `aria-label`, e.g., "Search products"); a placeholder is not a label — it vanishes on focus and many ATs ignore it.
- **Announce result and suggestion changes.** Wire autocomplete to the **WAI-ARIA combobox pattern** (`role="combobox"`, `aria-expanded`, `aria-controls`, `aria-activedescendant`) so screen readers hear suggestions; put the live result count in an `aria-live="polite"` region so "12 results" is announced when facets change.
- **Operable by keyboard end to end** — type the query, arrow through suggestions, Tab to filters, toggle a facet, and remove an applied-filter chip, all without a mouse (WCAG 2.1.1 Keyboard).
- **Don't encode filter state in color alone** (WCAG 1.4.1) — an active facet needs a checkbox/label/chip, not just a tint.
- **Adequate target size** for filter checkboxes and removable-chip × buttons, especially in a mobile tray (WCAG 2.5.5/2.5.8).
- **Zero-results must be announced**, not just rendered — route it through a live region or move focus to the message so AT users know the search failed and what to do next.

## Good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Findability of search** | Search hidden behind an icon on a search-primary site | Visible, recognizable text input on content/commerce pages |
| **Query tolerance** | Literal matching; typo → zero results | Forgiving of typos, plurals, synonyms; interprets intent |
| **Autocomplete** | Suggestions that dead-end; overwrite typed text | Distinct, ranked, keyboard-navigable suggestions that all resolve |
| **Facets vs filters** | One filter template for every category; sort mixed into filters | Category-specific facets; filtering and sorting visually separate |
| **Applied-filter visibility** | No record of active constraints; no way to remove one | Removable chips + "clear all"; results update live |
| **Mobile faceting** | Apply-blind, leave-and-return flow | Push-out tray with live result count before commit |
| **Zero results** | Bare "0 results" dead end | Query echo, "did you mean", facet-to-loosen, fallback content |
| **A11y** | Placeholder-as-label; color-only facet state; silent result changes | Real labels, ARIA combobox, live result count, keyboard-operable chips |
