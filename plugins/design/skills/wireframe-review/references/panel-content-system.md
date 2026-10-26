# Panel content system

## Home and contextual navigation

Artifacts with page units open on an all-pages canvas. Each page row renders its declared raw proposals side by side, with recorded choices visibly marked. The panel starts in global mode: artifact context, overall feedback, whole-artifact notes, decisions and handoff. Page-specific controls are hidden until a page or section is selected. Standalone component artifacts continue to open their decision directly.

Page titles open page review. The Sections select and selectable preview sections open that unit with its page and variant context; preview sections support keyboard activation. The All pages option in the Page select returns to global mode; do not duplicate it as a separate button. Navigation and browsing never record a selection or discard feedback. Overall feedback remains one field moved between global and handoff contexts, not separate copies. Home preview clicks navigate rather than annotate.

## Outside-in structure

The panel serves five tasks: recognize the current context, choose a proposal, explain changes, scan decisions across the artifact, and hand off feedback. Identity belongs in handoff, not before the current decision. Current context follows the assembled page in My selection and the active unit in Compare/Inspect.

The persistent Selection | Decisions segmented control (one shared track, equal segments and an inset selected surface) separates contextual feedback from the cross-artifact ledger. Selection contains current/global context, comments and handoff. Decisions contains progress, search, global choices and overrides. Presentation changes never mutate recorded choices or feedback.

## Global decision access

The header's Decisions shortcut activates the panel's Decisions view and focuses search. Opening a unit from the ledger returns to Selection and contextual review. Choosing a variant in the ledger keeps Decisions active. Both views use the same review state; no overview DOM is moved into a separate dialog.

The adjacent Feedback button opens a named dialog containing Copy feedback JSON, Download JSON, and Import JSON. Selecting an option closes that dialog before invoking its action or fallback; Escape returns focus to Feedback.

## Inside-out anatomy

- Context: human-readable page/unit title, preview mode, viewport. Previewing is not choosing.
- Effective choice: variant token, explicit-choice versus fallback label, source badge. A page override beats a global choice; absent both, the page composition supplies a fallback. Inactive units are identified.
- Decision row: unit navigation action, dedicated clear action, one, two or three equal proposal controls matching that unit. Symbol plus accessible state name distinguishes untouched, considered, chosen, rejected. No prose serialization of the states. Selection here applies globally and says so in the overview and accessible action name.
- Override: nested beneath its unit, with page title, variant, active/inactive badge, and separately named remove action. No detached override ledger to reconcile.
- Field: persistent label, optional help, associated control. Unit rationale applies across pages and says so; page-specific explanation belongs in a scoped comment.
- Comment: readable target, state/priority badges, full wrapping feedback, response, Edit and Locate. Stable IDs remain in the export. Locate restores variant and viewport; element feedback focuses its target.
- Empty state: distinguish no feedback from no matching feedback, preserve access to all comments, and state the available next action.
- Handoff: summary, optional reviewer, copy/download. Every comment and choice is exported regardless of panel filters.

## Geometry and behavior

Use shell foundations for border-box controls, constant border occupancy, independent axes, label padding, icon containers and glyph sizing. Use editorial typography for feedback and layout roles for section grouping. Prefer wrapping long titles; if space requires truncation, keep the complete accessible name and a visible full-text route, such as adjacent native disclosure. Do not rely on a hover-only tooltip for the full title. Feedback always wraps. Color never carries state alone. The native select remains the semantic input beneath decorative indicators.

Edits to rationale, summary, and reviewer save immediately. A dismissed comment draft stays in memory for its exact target and is recoverable in this tab; save the comment before closing or reloading. Drafts are not silently promoted into exported comments. Keyboard focus survives rerendered named choices. Disclosure buttons expose expanded state and tabs expose pressed state.

## Acceptance and maintenance

Run the model tests and render the artifact. For optional browser acceptance with an existing Playwright installation:

```
node scripts/check-shell.mjs /absolute/path/to/playwright
```

This generates an isolated fixture with 30 units and 100 comments. It checks long content, effective override source, locate navigation, draft recovery, both panel views, keyboard interactions, search, persistence, and 320/390/1500px host widths. It removes its fixture afterward. No Playwright dependency is needed to build or use the artifact.

Also verify empty and partially reviewed artifacts, JSON import/export, clipboard/storage fallbacks, exact annotation anchors, and desktop/mobile render quality when changing these behaviors. Preserve the existing feedback schema and revision identity for shell-only presentation changes.

## Toolbar density

Toolbar selects use accessible names without visible field labels. Keep the panel's contextual field labels. Routine save/status messages live in a visually hidden live region rather than a persistent band; actionable failures remain visible.

## All-pages comparison

All pages is a vertical stack of page rows. Each row has one page heading and three raw proposal cards ordered A/B/C. Each card includes Inspect, an explicit Choose action, rationale/tradeoff and section navigation. Browsing does not change recorded choices. Global section choices and page overrides remain available through My selection in contextual page review; they do not silently modify raw alternatives on the overview.

At narrower widths each page row scrolls horizontally with native CSS scroll snapping and a partial next-card reveal. Pages remain stacked vertically. Preserve each row's scroll position when choosing. Keyboard users can reach every proposal's controls.

## Scroll continuity

Selection rerenders preserve canvas-main, panel, dialog and horizontal row scroll positions. The document is viewport-bound; the canvas and panel scroll independently. Hold the previous canvas height while replacement frames load, then release it and restore positions once their layout is ready. Cancel stale restoration when a newer render or user gesture supersedes it. Restore control focus with preventScroll. Keep stable IDs on selection controls even when their labels change. Explicit Locate navigation remains allowed to scroll to its target. A genuinely shorter destination can clamp to its available scroll range.

## Outcome-aware review

A collapsible “What this should accomplish” sits with current context and exposes only supplied intent. The default note scope in contextual review is the whole decision across alternatives. “Something is missing” opens that same choice-free feedback path (whole artifact in global mode). This is an invitation to explain a gap, not an automatic rejection of all alternatives. Categories default to no category needed. Decision notes can describe conditional choices without changing selections. Keep original language and do not require reviewer classification into reasoning lenses.


## Context picker coverage

The decision-unit picker groups all peer page units under Pages, then the current page’s section/component units under Sections on this page. Choosing a peer page updates page context and the header Page select together. Sections remain scoped to the destination page; shared units retain their existing page-context behavior. Browsing never records a choice.
