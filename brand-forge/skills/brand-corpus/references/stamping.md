# Stamping a corpus into a distributable

A finished (or partial) brand corpus is **stamped** into one of two forms, chosen by where it will be
used. Both are produced by `bin/brand-stamp`; the *judgment* (is it ready? which form? what name?)
lives in `/brand-stamp` and this skill.

## Readiness — don't stamp a snapshot of nothing

Stamp against the corpus maturity stages (see `corpus-architecture.md`). A corpus needs a decided
**01-foundation** (stage ≥ 1) to be worth stamping; below that you're shipping scaffolding. Stamping
is allowed at any stage, but the stamp should **name the stage**, so the recipient knows whether they
hold a seed or a stewarded brand. Build down the stack before stamping ahead of it.

## The two forms

The form is a **destination decision the user makes** — `/brand-stamp` always asks which; it never defaults to one (the two artifacts target different hosts, so a wrong guess wastes the stamp).

| | **plugin** | **docs** |
|---|---|---|
| **For** | Claude Code / Cowork | Claude chat / Projects |
| **Is** | corpus + the `brand-corpus` MCP + a thin brand skill, as an installable plugin | the flat-convention corpus as knowledge documents + a thin brand skill |
| **Convention** | folder (path = layer); the MCP reads it | flat (`NN-layer--doc.md`); uploaded as knowledge |
| **Retrieval** | the MCP (`list` / `search` / `fetch` / `outline` / `get_tokens`) | the host reads the attached knowledge directly |
| **Corpus** | **bundled** snapshot (default) or `--linked` to a live `corpus_dir` | bundled as knowledge files |
| **Built to** | pass plugins-factory's `validate_plugin.py` | drop into a Project + a skill |

The two map onto the two corpus conventions this skill already defines: **folder → plugin**, **flat → docs**. (`brand-stamp` reads either input convention and emits the right one.)

## Bundled vs linked (plugin form)

- **Bundled** (default): the corpus is copied into the plugin (`corpus/`), MCP env
  `BRAND_CORPUS_DIR=${CLAUDE_PLUGIN_ROOT}/corpus`. Self-contained, distributable — a **snapshot** at
  stamp time.
- **Linked** (`--linked`): the plugin ships only the MCP + skill; `userConfig.corpus_dir` points the
  MCP at a **live** corpus dir (what a brand's own team wants). Env `BRAND_CORPUS_DIR=${user_config.corpus_dir}`.

## After stamping

- **plugin**: run `validate_plugin.py plugin <out>/<brand>-brand` (it's authored to pass); then add it
  to a marketplace or install it. The MCP can also be published standalone — see `mcp-wiring.md`.
- **docs**: upload the `NN-layer--*.md` files as Claude Project knowledge; use the generated `SKILL.md`
  as the brand skill.

The factory feeding the factory: brand-forge stamps the docs form directly and scaffolds the plugin
form; **plugins-factory** is the standard the plugin form is validated against (and `/plugin-promote`
can red-team it before you ship).
