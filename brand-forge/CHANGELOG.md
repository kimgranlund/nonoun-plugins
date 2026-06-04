# Changelog

## [0.2.0] — 2026-06-03

- **`/brand-stamp`** — emit a finished brand corpus as a distributable artifact, in one of **three pure, separate** forms (each to its own folder under `-o`): **plugin** (`<out>/plugin/<brand>-brand/` — corpus + the stdio `brand-corpus` MCP + a thin skill, for Claude Code / Cowork; bundled or `--linked`), **skill** (`<out>/skill/<brand>-brand/` — a standard Agent Skill with the corpus bundled in `references/`, for Claude chat; no MCP/scripts), and **mcp** (`<out>/mcp/<brand>-brand-mcp/` — the standalone server + corpus + a `claude mcp add` README). The command **always asks** which form. Mechanized by `bin/brand-stamp`; the plugin form is authored to pass plugins-factory's `validate_plugin.py`.
- **`brand-corpus` MCP wiring** captured in `skills/brand-corpus/references/mcp-wiring.md` — the language-agnostic tool contract, Python-vs-TS guidance, and the three registration recipes (bundled / standalone / published). `brand-corpus-mcp.py` now also accepts the `BRAND_CORPUS_ROOT` env alias.

- **Corpus distribution hygiene** — every bundled corpus now ships a per-layer `INDEX.md`; the plugin form takes `--version` (re-baking a corpus is a release — bump it); and `stamping.md` documents size-tiered retrieval (small inline / large indexed-MCP) and keeps the source-of-truth corpus in the consumer's version-controlled workspace, never in the plugin.

- **Tool-scoped the council (security).** All 15 brand-council agents now declare a `tools:` allowlist — the 14 critics `Read, Grep, Glob`, the orchestrator `+ Task` — so a reviewer reading an untrusted brand artifact/corpus is _structurally_ read-only, not merely instructed to be. Matches plugins-factory and closes the same trifecta-class gap brand-forge's own critics flag in others.

- **Red-teamed (the plugins-factory plugin-council, full panel).** Recorded in `reviews/2026-06-03-v0.2-red-team.md`. Verified clean on dependency legality and security (no bundled lethal trifecta, council structurally read-only, `_safe()` correct against traversal + symlink escape, ST5 injection sweep clean, the 14-critic roster well-sourced). Folded the MUST-fixes: reconciled the manifest/README to the shipped five-command surface (this `0.2.0` cut moves the previously "Unreleased" work into a dated release), and **removed an orphaned `bin/brand-stack` renderer + its SVG template** — a six-tier "Brand Stack" model the methodology never adopted and nothing referenced. The `brand-corpus` MCP was also hardened — truncation past 20k chars is now signalled, and a `selftest` exercises the `_safe()` path-guard against traversal / symlink / prefix-sibling escape (in CI, and traveling into stamped artifacts via `_copy_mcp`).

## 0.1.0 — 2026-06-02

Initial release. brand-forge packages the cultural-authority brand methodology as a self-contained Claude Code plugin, re-cast through the five plugin primitives for component-fit:

- **Commands** — four thin, typed entry points (`/brand-build`, `/brand-evaluate`, `/brand-council`, `/brand-orient`) that set mode + posture and route to the right skill or agent without re-containing the methodology.
- **Agents** — a 14-critic named-practitioner council plus an orchestrator that fans out the relevant sub-council (strategy · design · voice · full) in parallel, isolated contexts, returns severity-classified cited findings, and runs the B–S synthesis.
- **Skills** — `brand-methodology` (research → strategy → expression → stewardship), `brand-evaluate` (rubric library + adversarial scoring), and `brand-corpus` (corpus inventory + state read) hold all the depth.
- **Hooks + bin** — a `brand-lint` advisory structural lint on prose artifact writes (it surfaces smells, never blocks), catching only mechanizable smells (archetype/VMV/persona/DNA-word-cloud language, values-without-trade-offs); cultural judgment stays in the skill and council.
- **.mcp.json** — declares the `brand-corpus` retrieval slot, pointed at a brand via `userConfig.corpus_dir`; ships the contract, not any brand's data.

Self-contained: zero cross-plugin dependencies. Authored, validated, and red-teamed via `plugins-factory`.
