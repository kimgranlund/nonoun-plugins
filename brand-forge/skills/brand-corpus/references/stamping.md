# Stamping a corpus into a distributable

A finished (or partial) brand corpus is **stamped** into one of three forms, chosen by where it will be
used. Each is produced by `bin/brand-stamp` into its **own folder** under `-o <out>`, kept **pure and
separate** — the plugin never carries the cloud skill or the standalone-MCP packaging. The *judgment*
(is it ready? which form? what name?) lives in `/brand-stamp` and this skill.

## Readiness — don't stamp a snapshot of nothing

Stamp against the corpus maturity stages (see `corpus-architecture.md`). A corpus needs a decided
**01-foundation** (stage ≥ 1) to be worth stamping; below that you're shipping scaffolding. Stamping is
allowed at any stage, but the stamp should **name the stage**, so the recipient knows whether they hold a
seed or a stewarded brand. Build down the stack before stamping ahead of it.

## The form is the user's choice — always ask

`/brand-stamp` **always asks** which form; it never defaults. The three target different hosts and
runtimes, so a wrong guess wastes the stamp.

| | **plugin** | **skill** | **mcp** |
|---|---|---|---|
| **For** | Claude Code / Cowork | Claude chat (cloud) | self-host / `claude mcp add` |
| **Is** | installable plugin: corpus + the stdio `brand-corpus` MCP + a thin brand skill | a standard **Agent Skill folder** + the corpus bundled in `references/` | the stdio MCP server + corpus + a wiring `README.md` |
| **Local code?** | yes (bin/ MCP) | **no** — cloud can't run a local process | yes (stdio server) |
| **Retrieval** | the bundled MCP | the skill reads its own `references/` | the MCP, once wired |
| **Corpus** | folder-convention snapshot (or `--linked`) | bundled inside the skill (`references/<layer>/…`) | folder-convention snapshot (or `--linked`) |
| **Output** | `<out>/plugin/<brand>-brand/` | `<out>/skill/<brand>-brand/` | `<out>/mcp/<brand>-brand-mcp/` |

`plugin`/`mcp` use the folder convention + the MCP; `skill` bundles the corpus as the skill's own
references (sub-folders are fine in a skill — the flat `NN-layer--name` convention is only needed when the
corpus goes in as *separate* claude.ai Project knowledge rather than bundled in the skill).

## What each folder contains

```
<out>/
├── plugin/<brand>-brand/          .claude-plugin/plugin.json · .mcp.json · bin/brand-corpus-mcp.py
│                                  corpus/<layer>/… (bundled) · skills/<brand>-brand/SKILL.md
├── skill/<brand>-brand/           SKILL.md · references/<layer>/… (the corpus, bundled in the skill)
└── mcp/<brand>-brand-mcp/         brand-corpus-mcp.py · corpus/<layer>/… (bundled) · README.md (claude mcp add recipe)
```

## Bundled vs linked (`plugin` and `mcp`)

- **Bundled** (default): the corpus is copied in as a **snapshot** at stamp time — self-contained and
  distributable. Env `BRAND_CORPUS_DIR=${CLAUDE_PLUGIN_ROOT}/corpus` (plugin) or `$(pwd)/corpus` (mcp).
- **Linked** (`--linked`): no corpus is copied; the MCP points at a **live** corpus dir — `userConfig.corpus_dir`
  for the plugin, or a `BRAND_CORPUS_DIR` you set for the standalone MCP. What a brand's own team wants.

(The `skill` form has no bundled/linked switch — the corpus *must* travel inside the skill, since cloud has no MCP.)

## Cloud limits — why `skill` carries no MCP

Claude chat can run **skills** (with bundled files/sub-folders) and use **remote (HTTP) MCP connectors**, but
it **cannot run a local process** — no stdio MCP, no `bin/` scripts, no hooks. So the cloud form ships the
corpus *inside the skill*. If you want live MCP retrieval in chat, host the `mcp` form's tools behind an HTTP
transport and add it as a connector (the tool contract is identical — see `mcp-wiring.md`).

## After stamping

- **plugin**: `validate_plugin.py plugin <out>/plugin/<brand>-brand` (it's authored to pass); then add it to a
  marketplace or install it. `/plugin-promote` for a hostile read first.
- **skill**: upload `<out>/skill/<brand>-brand/` to Claude chat as a skill — it carries its own corpus.
- **mcp**: follow `<out>/mcp/<brand>-brand-mcp/README.md` to wire it (`claude mcp add`), or host it as a connector.

The factory feeding the factory: brand-forge stamps all three; **plugins-factory** is the standard the plugin
form is validated against, and `brand-corpus` is its worked MCP exemplar.
