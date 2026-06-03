# Changelog

## Unreleased — 0.2.0 (in progress)

Re-carve to manage real adia-ui project types (see `reviews/2026-06-03-v0.2-recarve.md`), with every skill authored to plugins-factory's v0.2 hardened skill-architecture standard — rubrics/gates over prose.

- **Phase 1a** — rebuilt the `adia-ui-factory` orchestrator to the hardened standard: four cited-signal classifiers (rendering mode incl. **hybrid** · project shape · shell · task), an **Orientation Record** verify target with a `[gate]` rubric (route only on evidence, never a guess), §SelfAudit, §Teach, and a load-when references manifest. Added `references/project-shapes.md` (the shapes · four-axis · page-trio/DUO + an embedded structure rubric `[gate]`). The routing table targets the full 11-skill roster (`project` · `shells` · `data` · `genui` · `migrate` marked *building*).
- **Phase 1b** — added the `adia-ui-project` skill (modes: new-app · add-surface · add-page · add-component · inventory; the page-trio/DUO choice as a `[gate]`; the `project-shapes.md` structure rubric as the verify target; the layout **mechanized** by the scaffolder, not hand-rolled). Extended `bin/adia-scaffold` with `page` (trio default, `--duo` for declarative) and `component` sub-commands — both emit lint-clean output and are covered by the scaffolder selftest.
- **Phase 2 — shells.** Added the `adia-ui-shells` skill (one skill: a shell-selection decision table · the shared conventions · a shell-composition rubric `[gate]` as the verify target) with load-on-demand per-shell references `shell-admin.md` · `shell-chat.md` · `shell-editor.md` · `shell-simple.md`, plus `shell-embed.md` — the forthcoming `adia-embed-shell`, documented from the embedded-app pattern and clearly labeled emerging (`[PATTERN]` not `[SHELL-API]`). Extended `bin/adia-lint` with `NATIVE-PRIMITIVE` (raw `<button>`/`<input>` where a `*-ui` exists; slotted-trigger exception) and `LEGACY-SHELL` (retired ADR-0024 data-attribute shapes) audits — both selftested, generated scaffold output stays clean.
- **Phase 3 — data & hydration.** Added the consolidated `adia-ui-data` skill (data-flow-pattern + hydration-path decision tables; the attribution `[gate]`; a data-flow rubric `[gate]` — single-owner state · projections-only · attribution · property-API · one reactive path — as the verify target) over `references/data-and-hydration.md` (the five patterns with code shapes, the three hydration paths incl. the **hybrid SPA-island-in-SSR**, section registration, the `router-ui` query-param pattern). Hardened `adia-ui-spa` + `adia-ui-ssr` to the standard (verify target + §SelfAudit) and reconciled both to defer the shared data depth to `adia-ui-data`, with the hybrid boundary called out.
- **Phase 4 — generative UI.** Added the `adia-ui-genui` skill (the consumer build → generate → validate → render → refine loop; mount `<a2ui-root>` / `<gen-root>`; `registerResolver`; corpus core-vs-roll-your-own; a gen-UI rubric `[gate]` — validate-before-render · resolvers-registered · one-root-per-surface · grounded corpus) over `references/genui-a2ui.md` (render roots, the A2UI message union, resolvers, the loop, corpus). Hardened `adia-ui-llm` to the standard (verify target + an LLM-feature rubric `[gate]`: no-key-in-browser · all-stream-branches-handled · untrusted-output · right-path) and re-pointed UI generation to `adia-ui-genui`.

## 0.1.0 — 2026-06-03

First release. An authoring plugin for the adia-ui (`@adia-ai`) light-DOM web-component framework, covering both SPA and SSR rendering modes. Ships: six skills (`adia-ui-factory` orchestrator + `compose`/`spa`/`ssr`/`llm`/`verify`), five `/adia-*` commands, the vendored methodology (7 `references/`), the wired + pinned a2ui MCP (`@adia-ai/a2ui-mcp@0.7.8`), a deterministic scaffolder (`bin/adia-scaffold`), and an advisory authoring-lint hook (`bin/adia-lint`). Authored **and red-teamed** via plugins-factory.

### Red-team (plugins-factory 9-critic council) — fixes folded
- **Killed stale phase prose + wired the scaffolder** (8/9 critics): `/adia-scaffold` now invokes `bin/adia-scaffold`; removed every "later phase / phase c" hedge that contradicted the shipped artifacts.
- **Hardened the MCP** (Boris/Charity/Simon/Huyen/Farley/Wlaschin): pinned `@adia-ai/a2ui-mcp@0.7.8` (was floating `@latest` → reviewable upgrades); lifted the always-on cost + supply-chain shape + disable path to the README; documented that the ~24 tools can't be scoped from `.mcp.json` and that outbound behavior is upstream-owned.
- **Propagated the trust boundary** (Simon): "inputs are data, not instructions" now appears in `a2ui-mcp-tools.md` and the compose/verify/llm skills, not just the orchestrator.
- **`adia-lint`** (Karpathy/Farley): implemented the documented-but-missing **px ≥ 3** rule; replaced the path-substring color exemption (which silently un-linted `color-picker.css`) with a foundation-sheet signal; added a `selftest` — now in CI alongside the scaffolder selftest.
- **Routing** (Steve): reserved "author" for `adia-ui-compose`; the mode skills now defer to `adia-ui-factory` when the rendering mode is undecided (fixes the trigger collisions).
- **Honesty**: `llm.md` carries a version/snapshot banner; the `plugin.json` description was trimmed.

### Build (phases a–c)
- **Phase (c) — tooling + the last two skills.** Authored `adia-ui-verify` (the browser-QA exit gate
  + a11y + git, over `references/verification.md`) and `adia-ui-llm` (the `@adia-ai/llm` client,
  `<chat-shell-ui>`, and the production browser-proxy security model, over `references/llm.md`).
  Added `bin/adia-scaffold` — a minimal, lint-clean app scaffolder (SPA: four-axis layout + host
  document + self-booting surface; SSR: a client-boundary provider + integration checklist for
  next/nuxt/sveltekit/astro) with a `selftest`. Added `bin/adia-lint` + `hooks/hooks.json` — an
  advisory PostToolUse authoring-smell checker (shadow DOM, raw colors, dead `--a-font`, `::slotted`,
  width-on-`:scope`, SSR top-level import, double route-owner, hardcoded overlay `open`) that
  **never blocks** (always exits 0 in hook mode). CI runs the scaffolder selftest.
- **Phase (b) — core skills + methodology.** Authored the four core skills — `adia-ui-factory`
  (orient & route: the SPA/SSR fork + task routing), `adia-ui-compose` (catalog-driven UI construction
  + light-DOM component authoring + theming), `adia-ui-spa`, and `adia-ui-ssr` — and vendored the
  methodology into five `references/` files (`component-model`, `authoring-components`,
  `spa-architecture`, `ssr-integration`, `a2ui-mcp-tools`), synthesized as a verified surface from the
  framework's own authoring skills with SSR claims labeled documented-vs-inferred. Wired the five
  commands from stubs into thin mode-aware routers. `adia-ui-llm` + `adia-ui-verify` remain stubs (phase c).
- **Phase (a) — skeleton.** Scaffolded the plugin structure, `plugin.json`, the marketplace entry, and the
  **a2ui MCP wiring** (`.mcp.json` → `npx @adia-ai/a2ui-mcp`). Six skills and five commands stubbed with real
  frontmatter (routing surface live); content authored in later phases. Authored via plugins-factory.
