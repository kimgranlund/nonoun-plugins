# Archetype · mobile-app

A phone app — **thumb-first**, a small viewport navigated as a **stack of views** with a few top-level **tabs**, and
**modality expressed through sheets** (popover / bottom / full) rather than side panes. Examples: iOS/Android native
apps, a PWA. The defining idea: **one view at a time**; depth is a navigation *stack* (push/pop), breadth is the
*tab bar*, and transient tasks are *sheets* that rise over the current view. There is no room for permanent side
chrome — everything is top bar, bottom bar, or overlay.

## Primary wireframe (tabbed stack)

```
┌───────────────────────────┐   ← status bar (OS)
│ ‹  Title              ⋯ +  │   header: back · title (or large-title) · actions
├───────────────────────────┤
│  ┌─────────────────────┐  │
│  │ list / card / feed  │  │   VIEW — the scrolling content of the
│  │ row ............. ›  │  │   current stack entry. Push a row → next view.
│  │ row ............. ›  │  │
│  │ row ............. ›  │  │
│  └─────────────────────┘  │
│                           │
│                  ╭─ FAB ─╮ │   floating primary action (optional)
│                  │   +   │ │
│                  ╰───────╯ │
├───────────────────────────┤
│  ◉ Home  ○ Search  ○ Library  ○ Profile │  bottom-tab-bar (3–5 top-level destinations)
└───────────────────────────┘
        ⌂ home indicator
```

## Modality — sheets (the "popover sheets" family)

```
BOTTOM SHEET (partial)        FULL-SCREEN MODAL            POPOVER / ACTION SHEET        SNACKBAR / TOAST
┌───────────────────────┐     ┌───────────────────────┐     ┌───────────────────────┐     ┌───────────────────────┐
│        content        │     │ ✕  New item     Save  │     │        content        │     │                       │
│       (dimmed)        │     ├───────────────────────┤     │                       │     │                       │
│ ╭───────────────────╮ │     │  form …               │     │      (dimmed)         │     │                       │
│ │ ═ grabber          │ │     │  field [_________]    │     │ ╭───────────────────╮ │     │ ╭───────────────────╮ │
│ │ Sheet title        │ │     │  field [_________]    │     │ │ Share              │ │     │ │ Saved ✓     Undo  │ │
│ │ option ›           │ │     │                       │     │ │ Edit               │ │     │ ╰───────────────────╯ │
│ │ option ›           │ │     │                       │     │ │ ─────────          │ │     │   (auto-dismiss)      │
│ │ [ Primary action ] │ │     │                       │     │ │ Delete  (danger)   │ │     │                       │
│ ╰───────────────────╯ │     │                       │     │ │ Cancel             │ │     │                       │
└───────────────────────┘     └───────────────────────┘     │ ╰───────────────────╯ │     └───────────────────────┘
 drag-to-dismiss · detents     full task · ✕ or Save         contextual menu / confirm    transient confirm + undo
```

## Named-pattern vocabulary

| Pattern | Job | Notes |
|---|---|---|
| **header / nav-bar** | title + back + screen actions | `‹ back` (pop) · title or **large-title** (collapses on scroll) · trailing actions (`⋯`, `+`) |
| **view** | the current stack screen | scrolls; a **list/feed/detail**; pushing a row → the next view (depth) |
| **navigation stack** | depth (push/pop) | back gesture / `‹`; each tab owns its own stack |
| **bottom-tab-bar** | breadth — top-level destinations | 3–5 tabs; the app's primary `switch-section` verb; selected tab highlighted |
| **global menu** | account / cross-cutting nav | a Profile tab, a hamburger drawer (Android), or a long-press menu |
| **bottom sheet** | lightweight modality, stays in context | grabber + **detents** (partial/expanded); drag-to-dismiss |
| **full-screen modal** | a self-contained task | `✕`/`Cancel` left, `Save`/`Done` right; covers everything |
| **popover / action sheet** | contextual choices / confirm | rises from the invoking control or bottom; destructive action set off |
| **snackbar / toast** | transient confirm + undo | auto-dismiss, non-blocking |
| **FAB** | the one primary create action | floats over the view (Android-idiom; iOS often uses a header `+`) |
| **segmented control / tabs (in-view)** | switch sub-views of one screen | top of the view, under the header |
| **pull-to-refresh / infinite scroll** | refresh / paginate a feed | gesture verbs |

## Workflows (multi-step flows)
Onboarding, checkout, and wizards are a **sequence of full-screen views** with a progress indicator (dots / step
bar) and `Back / Next`, often presented modally so the flow owns the screen until `Done`/`✕`.

## Variants
- **Tabs vs drawer:** iOS leans bottom-tab-bar; Android may use a nav-drawer (hamburger) for >5 destinations.
- **Large-title vs compact:** large-title collapses into the nav-bar on scroll.
- **Master-detail on tablet:** the view splits into a list pane + detail pane (it borrows the saas/productivity
  split when the viewport grows) — note the responsive graft.

## Outside-in notes (A)
- **A1:** the frame is **header (top) + view (elastic, scrolls) + tab-bar (bottom)**; sheets and modals are
  overlays *above* the frame, not new regions. Respect safe-areas (notch, home indicator).
- **A2/A5:** one column, full-bleed; touch targets ≥44px; thumb-reachable primary actions live **low** (bottom
  sheet, tab bar, FAB) — not in the top corners.

## Inside-out notes (B)
- **B1/B2:** *switch top-level* → tab-bar; *go deeper* → push a view; *go back* → `‹`/back-gesture; *transient
  task* → sheet; *contextual choice/confirm* → action sheet; *create* → FAB or header `+`; *confirm+undo* →
  snackbar. The orphan to catch: a destructive verb with no confirmation surface (always an action sheet / modal).
- **B3:** selected tab highlighted; pushed views animate direction; sheets show a grabber so their dismissal is
  discoverable; every async action gets a spinner or skeleton, every result a toast.
- **B4:** keep modality *shallow* — prefer a bottom sheet that stays in context over a full modal when the task is
  light; reserve full-screen modals for self-contained flows.
