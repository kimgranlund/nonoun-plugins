---
name: shell-editor
load-when: authoring an editor-shell — a design tool / canvas with resizable side panes
load-size: ~1.2k tokens
required-for: [adia-ui-shells — editor path]
---

# editor-shell — the canvas + panes

Design-tool / code-editor chrome from `@adia-ai/web-modules`. Register: `import '@adia-ai/web-modules/editor'`.

## Cluster roster

`<editor-shell>` (host; reflects `[focus-mode]`) · `<editor-toolbar>` (top bar; icon/heading/action slots) · `<editor-sidebar slot="leading"|"trailing">` (collapsible, holds `<pane-ui resizable>`) · `<editor-canvas>` (center work surface; optional `<editor-canvas-toolbar>` + `<editor-canvas-empty>`) · `<editor-statusbar>` (footer).

## Canonical skeleton

```html
<editor-shell>
  <editor-toolbar>
    <span slot="icon"><icon-ui name="brackets-curly"></icon-ui></span>
    <span slot="heading">Editor</span>
    <span slot="action"><button-ui icon="fullscreen" variant="ghost" size="sm"></button-ui></span>
  </editor-toolbar>
  <editor-sidebar slot="leading" collapsible><pane-ui resizable><tree-ui></tree-ui></pane-ui></editor-sidebar>
  <editor-canvas>
    <editor-canvas-toolbar><tabs-ui></tabs-ui></editor-canvas-toolbar>
    <div id="surface"></div>
  </editor-canvas>
  <editor-sidebar slot="trailing" collapsible><pane-ui resizable><!-- inspector --></pane-ui></editor-sidebar>
  <editor-statusbar>Status…</editor-statusbar>
</editor-shell>
```

## Props · events · methods

- **Prop:** `focus-mode` (reflected) — distraction-free; propagates `[full-screen]` to the toolbar, `[focused]` to the canvas.
- **Event:** `editor-mode-change {focusMode}`.
- **Method:** `.toggleFocusMode()`.
- Panes resize via `<pane-ui resizable>`; sidebars collapse via `collapsible`.

## Gotchas

- Import the **editor barrel**.
- Legacy shapes (`[data-editor-body]`, `[data-canvas]`, `data-pane-side/grow`) retired v0.4.0 — use the bespoke tags (`adia-lint` `LEGACY-SHELL`).
- SSR: swap the canvas content via the framework outlet, not `<router-ui>`.

Real usage: `apps/genui/app/a2ui-editor/`.
