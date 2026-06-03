# Token Contract Audit — Mode 5

Use when adding a new component, modifying an existing component's CSS, or investigating why a component misrenders under a theme.

Absorbed from the legacy `component-token-audit` skill at v2.0 (now removed; this file replaces it).

---

## The Component Token Contract (mandatory)

Spec: `docs/specs/component-token-contract.md` (live source of truth — if this doc contradicts that one, the spec wins; patch this skill).

Every component's `.css` file must follow the **two-block @scope** pattern:

```css
/* Block 1: token declarations on :where(:scope) — zero specificity */
@scope (my-component-ui) {
  :where(:scope) {
    --my-bg: var(--a-surface-1);
    --my-text: var(--a-fg);
    --my-radius: var(--a-radius-md);
  }
}

/* Block 2: styles using those tokens on :scope */
@scope (my-component-ui) {
  :scope {
    background: var(--my-bg);
    color: var(--my-text);
    border-radius: var(--my-radius);
  }

  /* Variants override TOKENS, not base styles */
  :scope[variant="danger"] {
    --my-bg: var(--a-danger-surface);
    --my-text: var(--a-danger-text);
  }
}
```

## Hard rules

1. **Zero raw color values** anywhere in component CSS
   - No `#fff`, `rgb(...)`, `oklch(...)` literals
   - All colors must reference `--a-chrome-*`, `--a-data-0..9`, `--a-fg*`, `--a-surface-*`, or family tokens (`--a-brand-*`, `--a-accent-*`, etc.)
2. **Two-block pattern** — token declarations separate from style rules
3. **Variants override tokens** — never rewrite base styles inside `[variant]` selectors. Change token values; the base styles absorb the change.
4. **`:where(:scope)`** for token defaults — zero specificity lets consumers override tokens from outside

## Audit procedure

1. **Find raw colors**

   ```bash
   grep -nE "#[0-9a-fA-F]{3,8}\b|rgb\(|rgba\(|oklch\(" \
     packages/web-components/components/<name>/*.css
   ```

   Any hit is a violation unless explicitly exempted (see below).

2. **Check for single-block @scope**

   ```bash
   grep -c "@scope" packages/web-components/components/<name>/*.css
   ```

   Should be `2` (or `0` for layout-only components).

3. **Check for variant rewrites of base properties**

   ```bash
   grep -nE ":scope\[variant.*\] \{" packages/web-components/components/<name>/*.css
   ```

   Inspect each match. If it sets `background`, `color`, `border` directly instead of `--my-bg`, `--my-text`, etc., it violates the variant rule.

4. **Check token usage in parent stylesheet**

   ```bash
   grep -n "--a-chrome\|--a-data\|--a-fg\|--a-surface" \
     packages/web-components/components/<name>/*.css
   ```

   Should have references; absence often indicates raw-value regressions.

## Documented exemptions (do not "fix")

- `chart.css` data slots reference `--a-data-0..9` (tokens, not raw)
- `card.css` mask uses `--a-chrome-light` (mask is opacity-only; value is semantic)
- Drawer/modal scrims use `--a-chrome-backdrop`

If you find a raw value elsewhere, either:

- Fix it by adding a proper token at `packages/web-components/styles/tokens.css`
- Or document the exemption in `docs/specs/component-token-contract.md`

## Chrome token palette

Added in v0.5.0 — use these for UI chrome:

- `--a-chrome-light` — light scrim / overlay
- `--a-chrome-dark` — dark scrim
- `--a-chrome-border` — subtle hairline borders
- `--a-chrome-ring-subtle` — focus rings, outlines
- `--a-chrome-shadow-soft` — elevation shadows
- `--a-chrome-backdrop` — modal/drawer backdrops

## Data palette

For charts, stat colors, category markers — use `--a-data-0` through `--a-data-9`. Do NOT hardcode chart colors.

## When to update this reference

If you add a new token category (like `--a-chrome-*` was added), update both this file and `docs/specs/component-token-contract.md`. The spec doc is the live source of truth; this file is the practitioner's checklist.

## Cross-references

- [authoring-cycle.md](authoring-cycle.md) Step 5 — verification gates (`npm run verify:palette` is the mechanical check for raw colors)
- [css-patterns.md](css-patterns.md) — the two-block `@scope` pattern in depth, with rationale
- [anti-patterns.md](anti-patterns.md) — failure catalogue including variant-rewrites-base bugs
