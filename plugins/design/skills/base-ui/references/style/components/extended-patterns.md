# Extended patterns

Read only the family needed. Load the common CSS and recipe runtime; call `mountExtendedPatterns(root)` after insertion and call its returned cleanup before removal. Scope one instance per root and namespace IDs when copying. Native fallbacks remain usable without JavaScript.

All patterns use inherited geometry and semantic role pairs. Persistent application state belongs to the prototype adapter; do not treat the standalone example DOM as application storage.

## multiselect

Native checkbox group; filter and removable selected-value buttons.
Filter retains selection; disabled selected choices cannot be removed.
Native checkboxes remain usable without scripts.
Boundary: Async search, virtual lists and token-input combobox behavior.

## tooltip

Descriptive text linked by aria-describedby; manual native popover.
Focus or hover reveals; Escape dismisses; hover may enter the tooltip.
Description remains inline without scripts.
Boundary: Interactive content, essential instructions available only on hover, or touch-only discovery.

## toast

Named notification region and polite status; ordinary dismiss buttons.
Maximum three persistent local notifications; dismiss returns focus to adjacent notification or trigger.
Static explanation; producing notifications requires scripts.
Boundary: Auto-expiry, cross-page delivery, server messages or emergency alerts.

## pagination

Named navigation and aria-current page; underlying ordinary list.
Three records per page; filter resets page; empty results announced; buttons preserve focus.
All records remain visible without scripts.
Boundary: Remote pagination, URL routing or virtualized datasets.

## tree

Single-select tree with nested groups and roving focus.
Arrows traverse/expand/collapse; Home/End, typeahead, sibling expansion and Enter selection.
Nested lists expose the whole hierarchy without scripts.
Boundary: Lazy loading, drag-and-drop, multiselection or route navigation.

## date-picker

Native bounded date input with optional modal calendar grid.
Arrows and week edges move days; PageUp/Down changes month, Shift changes year; selection commits, Escape cancels.
Native date input remains usable without scripts.
Boundary: Range selection, time zones, non-Gregorian calendars or missing min/max bounds.

## data-grid

Two-column editable grid; native labelled inputs in fallback.
Roving cell focus; Enter/F2 edits; Enter commits valid data, Escape cancels; Tab commits then moves cell.
Ordinary table with native editable inputs without scripts.
Boundary: Spreadsheet formulas, dynamic columns, sorting, virtualization or multi-cell selection.

## rich-text

Multiline textbox with roving formatting toolbar and plain-text fallback.
Select text then apply bold, italic or plain text; paste inserts text only; local save exposes restricted semantic HTML.
Native textarea remains editable without scripts.
Boundary: Full document editing, links, images, lists, collaborative editing or guaranteed undo history.

## Styling ownership

tooltip: Resolved control presentation radius; margin=2u; runtime trigger/viewport clearance=1u derived from computed panel margin.

toast: Card presentation radius and4u margin;3u message/action gap; message uses surface ink.

pagination: Ordinary page actions use surface/ink; current page uses action/on-action; only keyboard focus uses the focus ring.

tree: Hierarchy nodes have no row padding. Direct label owns control typography,1u icon gutter, minimum control height, resolved radius and canonical focus ring; child group owns3u indentation.

date-picker: Ordinary dates use surface/ink; selected date action/on-action; today uses muted surface; canonical focus ring is independent.

rich-text: Editor uses textarea field geometry:1u block and1.5u inline margin, resolved margin radius, paired surface/ink and canonical focus ring.

These styling relationships do not extend supported behavior or environment coverage. Preserve previously recorded observations; changed paint/geometry requires focused checks.
