---
description: Stamp a finished brand corpus into a distributable — a plugin (Code/Cowork), a cloud skill (Claude chat), or a standalone MCP.
argument-hint: [plugin|skill|mcp] [corpus path] [brand name]
---

You are in **stamp** mode: package a finished brand corpus into a shareable, host-appropriate artifact.

Request: **$ARGUMENTS** — parse as `[form] [corpus] [name]` (form ∈ `plugin` | `skill` | `mcp`). **There is no default form.**

1. **Ask which shape — always.** If the user did not explicitly name a form, **stop and ask** which they want. Each emits into its **own folder** under `-o <out>` (`<out>/plugin/`, `<out>/skill/`, `<out>/mcp/`) and is **kept pure** — the plugin never carries the cloud skill or the standalone-MCP packaging.
   - `plugin` → **Claude Code / Cowork**: an installable plugin — corpus + the read-only `brand-corpus` **stdio MCP** + a thin brand skill. **Bundled** snapshot by default; `--linked` points the MCP at a live `corpus_dir`.
   - `skill` → **Claude chat (cloud)**: a standard **Agent Skill folder** — `SKILL.md` + the corpus bundled in `references/` (one folder per layer). **No MCP, no scripts** — cloud can't run local processes, so the corpus travels _inside_ the skill.
   - `mcp` → **standalone deployable MCP**: the stdio server + the corpus (bundled or `--linked`) + a `README.md` with the `claude mcp add` recipe. For self-hosting / wiring the MCP on its own (a cloud connector needs an HTTP transport — see its README).

   Never assume — the three target different hosts and runtimes, so a wrong guess wastes the stamp. (`plugin`/`mcp` use the folder convention + the MCP; `skill` bundles the corpus as the skill's own references.)

2. **Check readiness** — via the **`brand-corpus`** skill, assess the corpus's maturity stage. A corpus stamps well only once **01-foundation** is decided (stage ≥ 1); name the stage and what's missing. Stamping a stage-1 corpus is allowed but say so plainly — you're shipping a seed, not a brand. Confirm the corpus path and brand name before writing anything.

3. **Stamp it** with `${CLAUDE_PLUGIN_ROOT}/bin/brand-stamp`:
   - `brand-stamp plugin <corpus> --name <brand> -o <out>` (add `--linked` for a live corpus),
   - `brand-stamp skill <corpus> --name <brand> -o <out>`, or
   - `brand-stamp mcp <corpus> --name <brand> -o <out>` (add `--linked`).

4. **Validate the plugin form** against the standard — run plugins-factory's `validate_plugin.py plugin <out>/plugin/<brand>-brand`. The stamp output is authored to pass it; a failure is a finding to fix, not to ship. For a hostile read before distribution, `/plugin-promote` it.

The MCP **language** is a packaging detail, not a question to re-ask each time: the default is the bundled Python reference server. Choose TS only to publish the MCP standalone via npm, or to integrate with the brand's own app codebase (see `skills/brand-corpus/references/mcp-wiring.md`).
