# Extended pattern verification

Authored behavior passed in Chromium 151.0.7922.34, Firefox 153.0 and WebKit 26.5 at widths 390/1280 in light/dark, with native fallbacks per engine. Prototype persistence and compiled-shell checks use Chromium. Actual screen readers, installed Safari and physical touch remain unverified. Evidence is recorded separately under the extended-patterns-2026-10-10 handoff; these observations do not establish full state-matrix coverage.

## multiselect

Bounded browser checks passed. Async search, virtual lists and token-input combobox behavior.

## tooltip

Bounded browser checks passed. Interactive content, essential instructions available only on hover, or touch-only discovery.

## toast

Bounded browser checks passed. Auto-expiry, cross-page delivery, server messages or emergency alerts.

## pagination

Bounded browser checks passed. Remote pagination, URL routing or virtualized datasets.

## tree

Bounded browser checks passed. Lazy loading, drag-and-drop, multiselection or route navigation.

## date-picker

Bounded browser checks passed. Range selection, time zones, non-Gregorian calendars or missing min/max bounds.

## data-grid

Bounded browser checks passed. Spreadsheet formulas, dynamic columns, sorting, virtualization or multi-cell selection.

## rich-text

Bounded browser checks passed. Full document editing, links, images, lists, collaborative editing or guaranteed undo history.
