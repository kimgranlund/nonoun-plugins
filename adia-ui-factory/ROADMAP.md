# Roadmap

## Shipped

- **v0.1.0** ✅ — the 6-skill plugin (orchestrator + compose/spa/ssr/llm/verify), the scaffolder + advisory lint hook, the wired a2ui MCP; built and red-teamed via plugins-factory.
- **v0.2.0** ✅ — the re-carve to **11 hardened skills** across the full authoring lifecycle (added `project` · `shells` · `data` · `genui` · `migrate`; hardened the rest to plugins-factory's skill-architecture standard — mode + verify target + `[gate]` rubric + §SelfAudit + load-on-demand references). `bin/adia-scaffold` gained `page`/`component`; `bin/adia-lint` gained px / native-primitive / legacy-shell audits. Full 9-critic council pass folded — see `reviews/2026-06-03-v0.2-red-team.md`.

## Open (deferred from the v0.2 red-team)

- **Re-bake discipline + a `tools/list` snapshot** — the vendored methodology and the pinned MCP (`@0.7.8`) are a coupled snapshot; bump and re-verify together on a framework move. Commit a `tools/list` capture so the "~24 tools" count is auditable and a version bump is a reviewable tool-surface diff. No automated reference↔catalog drift check yet.
- **a2ui MCP context cost (P6)** — pinned + documented + disable-path given, but the host starts the MCP on enable and the tool set can't be scoped from `.mcp.json`; a methodology-only user pays ~24 tool defs. Upstream/host limit; revisit if per-server gating lands.
- **Mechanize the render gate** — the highest-value verify gate (browser render + _read_ the screenshot) is self-verified; a `bin/adia-probe` (Playwright) could return a machine-checkable verdict.
- **Uniform snapshot banners** — add the "verified-against-version; the MCP is authoritative" banner to every reference that states concrete API (the per-shell refs especially).
- **Command namespace** — commands are `/adia-*`, skills `adia-ui-*`; consider aligning to `/adia-ui-*` before external adoption (a breaking rename — cheapest now).
- **Skill-count tension (Elon vs Steve/Boris/Chip H.)** — 11 skills is the chosen comprehensiveness↔cost trade; the `genui`↔`llm` and `migrate`↔`verify` merges stay declined unless the cost proves too high in real use.
- **`adia-embed-shell`** — currently the embedded-app _pattern_ (`references/shell-embed.md`, labeled emerging); re-bake the shell reference when the official web-module ships.
- **SSR top-level-import lint blind spot** — `adia-lint` flags the kit's top-level import only in framework-signal files; a bare `register.ts` won't trip it. Known limitation.

## Next plugin

- **`adia-ui-forge`** — the maintainer-side plugin (authoring the framework _itself_: new library components, git releases, training-data/corpus, the token/CSS system). Carved and built after adia-ui-factory, same discipline, against plugins-factory's v0.2 skill/agent-architecture standard.
