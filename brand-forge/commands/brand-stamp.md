---
description: Stamp a finished brand corpus into a distributable artifact — a plugin (Claude Code/Cowork) or skill+docs (Claude chat).
argument-hint: [plugin|docs] [corpus path] [brand name]
---

You are in **stamp** mode: package a finished brand corpus into a shareable, host-appropriate artifact.

Request: **$ARGUMENTS** — parse as `[form] [corpus] [name]` (form ∈ `plugin` | `docs`; default `plugin`).

1. **Check readiness first** — via the **`brand-corpus`** skill, assess the corpus's maturity stage.
   A corpus stamps well only once **01-foundation** is decided (stage ≥ 1). Name the stage and what's
   missing; stamping a stage-1 corpus is allowed but say so plainly — you're shipping a seed, not a
   brand. **Confirm the form, corpus path, and brand name before writing anything.**

2. **Choose the form by destination** (see `skills/brand-corpus/references/stamping.md`):
   - `plugin` → Claude Code / Cowork: the corpus + the read-only `brand-corpus` MCP + a thin brand
     skill, as an installable plugin (folder convention). **Bundled** snapshot by default; `--linked`
     points the MCP at a live corpus dir via `userConfig.corpus_dir`.
   - `docs` → Claude chat / Projects: the flat-convention corpus as knowledge documents + a thin brand
     skill (no MCP — the host reads the knowledge directly).

   The two forms map onto this skill's two conventions: **folder → plugin**, **flat → docs**.

3. **Stamp it** with `${CLAUDE_PLUGIN_ROOT}/bin/brand-stamp`:
   - `brand-stamp plugin <corpus> --name <brand> -o <out>` (add `--linked` for a live corpus), or
   - `brand-stamp docs <corpus> --name <brand> -o <out>`.

4. **Validate the plugin form** against the standard — run plugins-factory's
   `validate_plugin.py plugin <out>/<brand>-brand`. The stamp output is authored to pass it; a failure
   is a finding to fix, not to ship. For a hostile read before distribution, `/plugin-promote` it.

The MCP **language** is a packaging detail, not a question to re-ask each time: the default is the
bundled Python reference server. Choose TS only to publish the MCP standalone via npm, or to integrate
with the brand's own app codebase (see `skills/brand-corpus/references/mcp-wiring.md`).
