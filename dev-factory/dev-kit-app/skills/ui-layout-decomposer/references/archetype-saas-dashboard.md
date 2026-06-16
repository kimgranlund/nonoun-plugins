# Archetype · saas-dashboard

An app you **navigate**: many pages, records, and settings behind a persistent **clamshell** (a nav shell that wraps
swappable page content). Examples: Stripe, Linear, Vercel, GitHub, an admin console. The defining idea: **navigation
is permanent chrome; the page content is the variable**. Where the productivity-shell frames *one artifact*, the
dashboard frames *a route*.

## Primary wireframe (clamshell + page)

```
┌─sidebar-nav─┬─section-nav─┬─────────────────────── page ───────────────────────┐
│ ◆ logo    ⟨ │ Overview    │ ⌂ › Settings › Members            [⌘K search]        │
│ [⌘K search] │ Members  ◂  │ ┌─ page-header ─────────────────────────────────────┐│
│             │ Billing     │ │ Members                         [Export] [+ Invite]││
│ ▾ Workspace │ Roles       │ │ Manage who can access this workspace.             ││
│   • Projects│ Audit log   │ │ [ Active | Invited | Disabled ]   ← tabs          ││
│   • Members │             │ ├─ page-content ────────────────────────────────────┤│
│ ▾ Develop ▸ │             │ │ [search____]  [filter ▾] [sort ▾]      12 results ││
│   flyout ▸  │             │ │ ┌───────────────────────────────────────────────┐ ││
│ ▸ Settings  │             │ │ │ ☑  Name        Role     Last seen      [⋯]    │ ││
│             │             │ │ │ ──────────────────────────────────────────── │ ││
│ ─────────── │             │ │ │ ☐  Ada L.      Admin    2h ago         [⋯]    │ ││
│ 👤 Ada L.   │             │ │ │ ☐  Grace H.    Member   1d ago         [⋯]    │ ││
│   ⚙ settings│             │ │ └───────────────────────────────────────────────┘ ││
│   ↪ sign out│             │ │ ‹ Prev   1 2 3 … 9   Next ›        rows: 25 ▾      ││
└─────────────┴─────────────┴───┴────────────────────────────────────────────────┘┘
     overlays:  ▸ drawer (edit record)   ▢ modal (confirm/dialog)   ▭ snackbar (toast)
```

## Named-pattern vocabulary

| Pattern | Job | Notes / sub-parts |
|---|---|---|
| **sidebar-nav** | the primary route switcher; permanent | **collapsible** (icon-rail ⟨⟩); **header** (logo + workspace switcher + ⌘K); **nav list** with **accordions** (▾ expanding groups) and/or **flyouts** (▸ hover menus on collapse); **bottom user section** (avatar · settings · sign-out) |
| **section-nav** | second-level nav within a section | optional column between sidebar and content; the sub-pages of the chosen section |
| **breadcrumbs** | where-am-I trail + up-navigation | `⌂ › Section › Page`, atop the page |
| **command-bar / search** | the keyboard jump/run surface (⌘K) | global; jump-to-page, run-action, search records |
| **page-header** | the page's identity + page-level actions | **title** · optional **description** · **actions** (right-aligned: primary + secondary) · optional **tabs** (sub-views of this page) |
| **page-content** | the variable body | one of the content patterns below |
| **modal** ▢ | blocking dialog | confirm, create, focused form — dims the app |
| **drawer** ▸ | side-sliding panel | edit/inspect a record without leaving the list |
| **snackbar** ▭ | transient confirmation/undo | bottom toast; "Invited ✓  Undo" |

## Page-content patterns

```
TABLE (records)                         DATA DASHBOARD (charts)            SETTINGS (forms)
┌ search  filter ▾  sort ▾ ─ N ─┐       ┌ KPI ┐┌ KPI ┐┌ KPI ┐┌ KPI ┐       ┌ section title ───────────┐
│ ☑ col   col    col    [⋯]     │       │ 12k ││ 98% ││ 3.4 ││ ▲7% │       │ desc                     │
│ ─────────────────────────────│       └─────┘└─────┘└─────┘└─────┘       │ Label        [input____] │
│ ☐ row …................. [⋯] │       ┌ time-series ───────┐┌ break ┐    │ Label        ◉ toggle    │
│ ☐ row …................. [⋯] │       │     ╱╲    ╱╲        ││ ▰▰▰    │    │ Label        [select ▾]  │
│ ‹ 1 2 3 … ›  rows: 25 ▾       │       │  ╱╲╱  ╲╱╲╱          ││ ▰▰     │    │           [Cancel][Save] │
└──────────────────────────────┘       └────────────────────┘└───────┘    └──────────────────────────┘
 pagination · sort · filter · search    KPI row + chart grid + legend      grouped fieldsets + sticky save
```

Settings sub-pages worth naming explicitly (left-rail or section-nav): **Organization/General** · **Members &
roles** (access) · **Billing & payment** · **Plans/usage** · **API keys & integrations** · **Audit log** ·
**Security/SSO** · **Notifications**. Each is a settings-form page with grouped fieldsets + a sticky save bar.

## Variants
- **Top-nav instead of sidebar** (horizontal primary nav) for shallow apps; the clamshell becomes a header + page.
- **Collapsed icon-rail** with flyout submenus for dense navigation.
- **Split-view list/detail** (master-detail) — the table on the left, the selected record's detail on the right
  (borrows the productivity-shell's right pane).

## Outside-in notes (A)
- **A1:** the clamshell (sidebar + optional section-nav) is fixed; **only the page-content scrolls**. Breadcrumbs +
  page-header are sticky atop the scroll region.
- **A2:** sidebar ~240–280px (collapses to ~56px icon-rail) · section-nav ~200px · content elastic.
- **A4/A5:** content is cards/tables/fieldsets; tables align columns, right-align numerics, pin the header row.

## Inside-out notes (B)
- **B1/B2:** *navigate* → sidebar/section-nav/breadcrumbs/⌘K; *page actions* → page-header (right); *row actions* →
  the `[⋯]` row menu or a drawer; *bulk actions* → a selection toolbar that appears when rows are checked;
  *create/confirm* → modal; *transient confirm/undo* → snackbar.
- **B3:** active nav item highlighted; current breadcrumb bold; a saved/error state on every form; optimistic row
  updates with snackbar-undo.
- **B5:** the sidebar selection, breadcrumb, page-header title, and ⌘K "recent" all agree on the current route.
