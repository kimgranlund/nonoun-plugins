---
description: Stamp a finished brand corpus into a distributable artifact — a plugin (Claude Code/Cowork) or skill+docs (Claude chat).
argument-hint: [plugin|docs] [corpus path] [brand name]
---

You are in **stamp** mode: package a finished brand corpus into a shareable, host-appropriate artifact.

Request: **$ARGUMENTS** — parse as `[form] [corpus] [name]` (form ∈ `plugin` | `docs`). **There is no default form.**

1. **Ask which shape — always.** If the user did not explicitly name `plugin` or `docs`, **stop and ask**, showing both and what each is for:
   - `plugin` → **Claude Code / Cowork**: the corpus + the read-only `brand-corpus` MCP + a thin brand skill, as an installable plugin (folder convention). When they pick `plugin`, also confirm **bundled** snapshot (default, self-contained) vs **`--linked`** (the MCP points at a live `corpus_dir`).
   - `docs` → **Claude chat / Projects**: the flat-convention corpus as knowledge documents + a thin brand skill (no MCP — the host reads the knowledge directly).

   Never assume — the two produce different artifacts for different hosts, so a wrong guess wastes the stamp. (They map onto this skill's two conventions: **folder → plugin**, **flat → docs** — see `skills/brand-corpus/references/stamping.md`.)

2. **Check readiness** — via the **`brand-corpus`** skill, assess the corpus's maturity stage. A corpus stamps well only once **01-foundation** is decided (stage ≥ 1); name the stage and what's missing. Stamping a stage-1 corpus is allowed but say so plainly — you're shipping a seed, not a brand. Confirm the corpus path and brand name before writing anything.

3. **Stamp it** with `${CLAUDE_PLUGIN_ROOT}/bin/brand-stamp`:
   - `brand-stamp plugin <corpus> --name <brand> -o <out>` (add `--linked` for a live corpus), or
   - `brand-stamp docs <corpus> --name <brand> -o <out>`.

4. **Validate the plugin form** against the standard — run plugins-factory's `validate_plugin.py plugin <out>/<brand>-brand`. The stamp output is authored to pass it; a failure is a finding to fix, not to ship. For a hostile read before distribution, `/plugin-promote` it.

The MCP **language** is a packaging detail, not a question to re-ask each time: the default is the bundled Python reference server. Choose TS only to publish the MCP standalone via npm, or to integrate with the brand's own app codebase (see `skills/brand-corpus/references/mcp-wiring.md`).
