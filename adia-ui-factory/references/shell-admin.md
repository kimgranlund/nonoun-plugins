---
name: shell-admin
load-when: authoring or debugging an admin-shell app frame (sidebar + topbar + command palette + pages)
load-size: ~2.5k tokens
required-for: [adia-ui-shells — admin path]
---

# admin-shell — the app frame

Full SaaS/admin chrome from `@adia-ai/web-modules`. Register the **cluster barrel**: `import '@adia-ai/web-modules/shell'`.

## Cluster roster

`<admin-shell>` (host coordinator) · `<admin-sidebar>` (resizable/collapsible, `slot="leading"|"trailing"`) · `<admin-command>` (Cmd+K palette) · `<admin-content>` (center column) · `<admin-topbar>` / `<admin-statusbar>` (chrome bars, shared slots) · `<admin-scroll>` (vertical scroll container) · `<admin-page>` + `<admin-page-header>` / `<admin-page-body>` / `<admin-page-footer>` (the page; header/footer sticky, body scrolls) · `<admin-entity-item>` (icon+label+badge identity row). Three are JS-bearing (shell, sidebar, command); the rest are CSS-only structure.

## Canonical skeleton

```html
<admin-shell mode="rounded borderless">
  <admin-sidebar slot="leading" resizable collapsible>
    <admin-topbar slot="header"><span slot="heading">Workspace</span></admin-topbar>
    <nav-ui>…</nav-ui>
    <admin-statusbar slot="footer"><admin-entity-item slot="heading">…</admin-entity-item></admin-statusbar>
    <div data-resize></div>                          <!-- required when [resizable] -->
  </admin-sidebar>
  <admin-content>
    <admin-topbar slot="header">
      <button-ui data-sidebar-toggle="leading" icon="sidebar" variant="ghost"></button-ui>
      <breadcrumb-ui slot="heading">…</breadcrumb-ui>
    </admin-topbar>
    <admin-scroll>
      <admin-page>
        <admin-page-header slot="header"><header-ui><span slot="heading">Page</span></header-ui></admin-page-header>
        <admin-page-body slot="body"><section-ui>…</section-ui></admin-page-body>
      </admin-page>
    </admin-scroll>
    <admin-statusbar slot="footer"><span>Status</span></admin-statusbar>
  </admin-content>
  <admin-command><command-ui placeholder="Search…"></command-ui></admin-command>
</admin-shell>
```

## Props · events · methods

- `<admin-shell mode>` — space-separated (`rounded` `borderless`; default `"rounded borderless"`). Events (forwarded): `sidebar-toggle {name, expanded}`, `sidebar-resize {name, width}`, `command-select {value}`. Methods: `toggleLeading()` `toggleTrailing()` `openCommand()` `closeCommand()`.
- `<admin-sidebar>` — `resizable` `collapsible` `name` `min-width`; reflects `[collapsed]` (snap ≤96px) / `[resizing]`. Methods `.toggle()/.collapse()/.expand()`. A `[data-sidebar-toggle="leading"]` button anywhere wires to it via delegation.
- `<admin-command>` — `open` `shortcut` (`both`|`cmd+k`|`ctrl+k`) `no-shortcut`; `.show()/.hide()`. A `[data-command-trigger]` opens it.
- Read cross-cutting state off the child: `shell.querySelector('admin-sidebar[slot="leading"]').hasAttribute('collapsed')`; style with `admin-shell:has(admin-sidebar[collapsed]) …`.

## SPA vs SSR

SPA mounts the full markup. SSR keeps the shell + chrome fixed and swaps only the **page body** via the framework outlet — replace the inner page content with `{children}` / `<slot/>`; never mount `<router-ui>` (see `adia-ui-ssr`).

## Gotchas (mechanized where noted)

- **Piecemeal import** → `AdminSidebar`/`AdminCommand` unregistered; `.toggle()/.show()` undefined. Import the barrel.
- **Wrapping shell children in `<col-ui>`/`<row-ui>`** → breaks the grid (it reads tag selectors). Generics go _inside_ `admin-content`/`admin-page-body`.
- **Raw `<header>` inside `<admin-page-header>`** → slot routing silently drops; wrap `<header-ui>`.
- **`[resizable]` without a child `<div data-resize>`** → no drag handle.
- **Hardcoded `[collapsed]`** → won't auto-clear on resize; use `.collapse()/.expand()`.
- **Multiple `<admin-page>` in one `<admin-scroll>`** → single-axis scroll breaks; one page per scroll.
- **`@container (…)` instead of `@container page-content (…)`** → won't react to sidebar collapse.
- **Legacy shapes** (`<aside data-sidebar>`, `<dialog data-command>`) — retired v0.4.0 (`adia-lint` `LEGACY-SHELL`).

Real usage: `apps/saas/app/admin-dashboard/`.
