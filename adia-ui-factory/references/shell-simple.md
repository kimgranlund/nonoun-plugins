---
name: shell-simple
load-when: authoring a simple-shell — marketing / error / landing / auth page (minimal centered chrome)
load-size: ~0.8k tokens
required-for: [adia-ui-shells — simple path]
---

# simple-shell — minimal centered chrome

The lightest shell from `@adia-ai/web-modules` — for marketing, landing, error (404/500/maintenance), thank-you, and auth pages. Register: `import '@adia-ai/web-modules/shell'` (simple ships in the shell cluster). Behavior-only host + two CSS-only children.

## Cluster roster

`<simple-shell>` (host) · `<simple-hero>` (the focal block — `slot="heading"` / `slot="lede"` / `slot="actions"`) · `<simple-content>` (supporting content below).

## Canonical skeleton

```html
<simple-shell centered full-bleed>
  <simple-hero>
    <h1 slot="heading">Welcome</h1>
    <p slot="lede">Get started in seconds.</p>
    <div slot="actions"><button-ui variant="primary">Sign up</button-ui></div>
  </simple-hero>
  <simple-content><p>Additional content.</p></simple-content>
</simple-shell>
```

## Props

`centered` (vertically center the hero) · `full-bleed` (edge-to-edge background). No events — it's pure chrome; you author the content.

## Gotchas

- Controls inside are `*-ui` (`button-ui`, `link-ui`), not raw `<button>`/`<a>` (`adia-lint` `NATIVE-PRIMITIVE`).
- For an error page, a page-DUO (no `.contents.js`) is usually right — see `project-shapes.md`.

Real usage: `apps/errors/`, `apps/user-flow/` (auth).
