# Changelog

## 0.2.0 — 2026-06-03

Evolved **skill + agent authoring** — closing the methodology gap that was producing thin, single-`SKILL.md` skills.

- **`references/authoring/skill-architecture.md`** — the construction methodology (the successor to the standalone `skills-studio`): the five layers (metadata · seed · references · scripts · evals); the required `SKILL.md` seed surface (cold-start mode table, Quick Start, posture, modes, loading manifest, per-mode verify targets, anti-pattern gallery, §SelfAudit, §Teach); size tiers; the `references/` taxonomy with per-file `load-when`/`required-for` frontmatter; the mechanization threshold; voice/posture; and the not-thin checklist. `plugin-build` now builds skills against it.
- **`references/authoring/agent-architecture.md`** — the agent-authoring discipline the plugin lacked: when an agent earns its isolated context (else it's a skill), the role taxonomy (critic · worker · analyst · orchestrator · actor), tool-scope minimal-sufficiency + the lethal trifecta, the in-agent trust boundary, persona design, isolation/memory, and the council orchestration pattern.
- **`references/rubrics/agent-fit.md`** — the scoring face (8 dimensions; tool-scope/trifecta + loader-rule are `[gate]`). Registered in `rubric-manifest.json`; `plugin-evaluate` loads it when a plugin bundles agents.
- Wired into `plugin-build` (new first principle: *components are authored to depth, not stubbed*; the author/edit sub-modes read the new docs) and cross-linked from `frontmatter.md` (the field contract → the structure methodology).

## 0.1.0 — 2026-06-02

Initial release as a **plugin**. plugins-factory was re-cast from a single mega-skill into a self-contained Claude Code plugin, authored by (and against) its own standard — the dogfood test of the tool. Re-shaped through the five plugin primitives for component-fit:

- **Commands** — six thin, typed entry points (`/plugin-author`, `/plugin-carve`, `/plugin-edit`, `/plugin-score`, `/plugin-critique`, `/plugin-promote`) that set mode + posture and route to a skill or the council, without re-containing the methodology.
- **Skills** — split by posture: `plugin-build` (the maker — author/carve/edit) and `plugin-evaluate` (the judge — score/critique/promote, carrying the untrusted-target trust boundary). Both draw on one shared standard.
- **Agents** — the 9-critic council promoted from prose personas to **isolated parallel agents** (`critic-boris … critic-david-f`) plus a `plugin-council` orchestrator that fans them out and runs the cross-critic synthesis; `carve-analyst` (the composition-graph fan-out worker) retained.
- **Hook** — an advisory `validate_plugin.py hook` on `plugin.json` / `marketplace.json` writes (surfaces manifest/layout/path smells, never blocks).
- **Shared spine (`references/`)** — the 9-dimension rubric library, the 5 foundation↔rubric pairs, `plugin-architecture.md`, `carve-method.md`, the authoring bridge, and the critic prompt corpus (`eval-prompts.md`), referenced by both skills via `${CLAUDE_PLUGIN_ROOT}`.
- **Bin** — `validate_plugin.py` (plugin + marketplace static validators, `selftest`, and the advisory `hook` mode), `check-foundations-coverage.py`, and `reference-lint.py` (fails on doc/command references that don't resolve on disk).

**Decision A (self-contained):** the four cross-cutting rubrics that score P1/P7/P8/P9 (`cold-start-orientation`, `skills-authoring`, `skill-extensibility`, `security-and-scope-containment`) are **co-located** from `skills-studio` rather than referenced across the install boundary — zero `../` cross-plugin paths, zero `dependencies`. (Future: promote the shared critics + cross-cutting rubrics to a foundation plugin both studios depend on, once skills-studio is also packaged.)

Status **draft, N=0 empirical applications** — every rubric dimension is a falsifiable hypothesis until applied to ≥3 real plugins. Build-time red-team (full 9-critic panel, given it bundles a hook and is a meta/orchestrator plugin) returned **CONDITIONAL**; all Critical/Major findings folded — every council agent tool-scoped to read-only (closing the P9 trifecta), `scripts/`→`bin/` drift and dead persona pointers fixed, hook invocation + injection-framing hardened, and a `reference-lint.py` + CI workflow added to gate the regression class. Structural items (council-calibration eval, dimension MECE audit) tracked in ROADMAP. See `reviews/2026-06-02-plugin-red-team.md`.
