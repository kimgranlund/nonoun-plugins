# Roadmap

Phased build (via plugins-factory's `author` method):

- **[a] Skeleton** ✅ — structure + `plugin.json` + marketplace entry + a2ui MCP wiring + stubs (validates clean).
- **[b] Core skills** — `adia-ui-factory` (decision tree), `adia-ui-compose` (catalog literacy + component authoring + theming), `adia-ui-spa`, `adia-ui-ssr`. Vendor the methodology into `references/` (SPA best-practices + SSR rendering-model).
- **[c] Tooling** — `adia-ui-llm` + `adia-ui-verify`; `bin/adia-scaffold` (deterministic per-mode app scaffolder); an advisory authoring-lint **hook** (raw colors, `attachShadow`, width-on-tag, dead `--a-font`, top-level import in SSR, double route-owner).
- **[d] Validate + red-team** — full `validate_plugin.py` + the 9-critic council; fold findings. Watch P6 (the a2ui MCP's 24 always-on tool defs) and P9 (MCP trust surface).

## Open
- Re-bake discipline for the vendored methodology when the framework version bumps.
- Decide whether the a2ui MCP is always-on or gated (P6 context cost).
