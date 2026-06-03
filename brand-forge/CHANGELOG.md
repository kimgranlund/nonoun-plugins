# Changelog

## 0.1.0 — 2026-06-02

Initial release. brand-forge packages the cultural-authority brand methodology as a self-contained Claude Code plugin, re-cast through the five plugin primitives for component-fit:

- **Commands** — four thin, typed entry points (`/brand-build`, `/brand-evaluate`, `/brand-council`, `/brand-orient`) that set mode + posture and route to the right skill or agent without re-containing the methodology.
- **Agents** — a 14-critic named-practitioner council plus an orchestrator that fans out the relevant sub-council (strategy · design · voice · full) in parallel, isolated contexts, returns severity-classified cited findings, and runs the B–S synthesis.
- **Skills** — `brand-methodology` (research → strategy → expression → stewardship), `brand-evaluate` (rubric library + adversarial scoring), and `brand-corpus` (corpus inventory + state read) hold all the depth.
- **Hooks + bin** — a `brand-lint` advisory structural lint on prose artifact writes (it surfaces smells, never blocks), catching only mechanizable smells (archetype/VMV/persona/DNA-word-cloud language, values-without-trade-offs); cultural judgment stays in the skill and council.
- **.mcp.json** — declares the `brand-corpus` retrieval slot, pointed at a brand via `userConfig.corpus_dir`; ships the contract, not any brand's data.

Self-contained: zero cross-plugin dependencies. Authored, validated, and red-teamed via `plugins-factory`.
