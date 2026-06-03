---
name: migration
load-when: migrating an adia-ui app — version upgrade, port-to-adia, or mode change
load-size: ~2.5k tokens
required-for: [adia-ui-migrate — all types]
---

# Migration — types, history, discipline

Consumer migrations. The framework MIGRATION GUIDE (in the framework repo) is the source of truth per version; this is the durable method + the shape of past breaks. Treat versions/examples as a snapshot.

## Types

- **version-upgrade** — bump `@adia-ai/*` X→Y (lockstep; all packages move together). PATCH cuts are drop-in; MINOR/MAJOR carry breaking items.
- **port-to-adia** — an existing app (raw HTML, or legacy `@agent-ui-kit`) → adia-ui: a tag rename map (`aui-button`→`button-ui`, `<button>`→`<button-ui>`) + token namespace swap (`--n-*`→`--a-*`).
- **mode-change** — SPA↔SSR: re-own routing (framework router vs `<router-ui>`), registration (top-level vs client-hook), and state (signals vs cookies). See `adia-ui-spa` / `adia-ui-ssr`.

## The 5-step discipline

1. **Read the guide** for the target version. Missing section → pause, ask, offer to draft it.
2. **Audit** — `git grep -nlE '<pattern>'` each breaking item; cluster by component; count files/occurrences. Surface before sweeping.
3. **Sweep** — mechanical per cluster:

   ```bash
   git grep -lE 'button-ui[^>]*variant="danger"' \
     | xargs perl -i -pe 's/(<button-ui[^>]*?)variant="danger"/$1color="danger"/g'
   ```

   …or a shipped codemod. **Flag, don't auto-apply, judgment items** (below).
4. **Verify** — `adia-lint` clean of `LEGACY-SHELL`/`NATIVE-PRIMITIVE`; build/render; then the **leftover-drift grep** across `.css`/`.js`/`.md`/`.json`; browser probe.
5. **Report** — per-axis counts, manual-review list, gate results, next actions.

## Real breaking-change history (before → after)

- **v0.0.20 (10 items):** `<button-ui variant="danger">` → `variant="solid" color="danger"`; stage Booleans (`completed`/`active`) → `status="completed|active"` enum (timeline/stepper/pipeline); `<table-toolbar-ui>` opt-out Booleans **inverted** (`searchable="false"` → `no-search`; default flipped); `<chat-input-ui busy>` → `loading`; `variant="error"` alias removed → `danger`; event prefixes dropped (`chat-submit`→`submit`); `<field-ui error>` moved to the child input; `<agent-trace-ui open>` → `collapsed` (**semantic flip — default-visible now**); kebab prop keys → camelCase (JS only). Safari floor → 18.
- **v0.0.29 — three-tier extraction:** `patterns/` moved `@adia-ai/web-components/patterns/*` → `@adia-ai/web-modules/{shell,chat,editor,runtime}/*`. Import-path rewrite + add the `web-modules` dep.
- **v0.4.0 — legacy shell shapes retired (ADR-0024):** `<aside data-sidebar>`→`<admin-sidebar slot>`; `<dialog data-command>`→`<admin-command>`; `[data-chat-messages/input/empty]`→`<chat-thread>/<chat-composer>/<chat-empty>`; `[data-editor-body]/[data-canvas]`→`<editor-canvas>` + `<editor-sidebar>`. JS selectors move with them. (`adia-lint` `LEGACY-SHELL` flags the remnants.)
- **v0.6.0/0.6.1:** `stat-ui.{js,css}`→`stat.{js,css}` (deep-import only); `<link-ui>` token rename `--link-color-*`→`--link-fg-*` (only if you override).

## Judgment items (flag for review — never auto-sweep)

Semantic flips (`[open]`→`[collapsed]` inverts default visibility), Boolean opt-out inversions (default changes), attribution transfers (`field-ui error` → child input may not exist yet). Surface these with their call sites; let the author decide.

## What the path-only sweep misses (leftover-drift categories)

Bare-name mentions in prose docs (README/AGENTS/ROADMAP); skill-directory names; JSON metadata fields (highest impact — silent harvest miss on rebuild); inventory tables in cross-cutting docs. Use a pre/post grep diff:

```bash
grep -rln 'OLD_NAME' . --include='*.md' --include='*.json' | sort > /tmp/pre.txt
# … sweep …
grep -rln 'OLD_NAME' . --include='*.md' --include='*.json' | sort > /tmp/post.txt && diff /tmp/pre.txt /tmp/post.txt
```

## MCP aids

`search_chunks` (the updated example for a changed component) · `check_anti_patterns` (a swept file is clean) · `convert_html` (map legacy/foreign markup → current components, for ports). There's no "list breaking changes" tool — the MIGRATION GUIDE is read by hand.
