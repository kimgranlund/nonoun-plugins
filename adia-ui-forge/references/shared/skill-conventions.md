# Skill Conventions (Canonical)

Structural conventions every rollup-family skill should follow. Distilled from `core-skills-best-practices` — particularly its `skills-authoring.md`, `harness-design.md`, `progressive-context-construction.md`, `inversion-and-abstraction.md` references — plus the patterns surfaced by per-skill refactor-spec reviews.

---

## §1 Required files

Every skill directory MUST have:

| File | Purpose | Conventions |
| --- | --- | --- |
| `SKILL.md` | Cold-start seed (frontmatter + posture + capability menu) | YAML frontmatter `name` matches directory name; `description` is WHAT + WHEN + NOT (≤1024 chars); body <50KB; loaded on every invocation |
| `skill.json` | Manifest (machine-readable contract) | `name`, `version` (semver), `description`, `status`, `tags`, `peer_skills`, `files` (every file on disk listed); validated by `audit-<name>-roster.mjs` |
| `CHANGELOG.md` | Version history | Per-version entry; matches `skill.json version`; new entries prepended above prior entries |

## §2 Required directories (when applicable)

| Directory | When required |
| --- | --- |
| `references/` | When SKILL.md would otherwise exceed ~50KB. Procedural detail extracted; SKILL.md becomes a thin seed with a §ColdStartTriage menu. |
| `scripts/` | When the skill has any §SelfAudit, verify-step, or §Teach mechanization. Scripts named in SKILL.md verify steps MUST ship in `scripts/` (not at substrate paths). |
| `evals/` | All skills. Minimum: `routing-corpus.json` (≥10 trigger + ≥5 adversarial) + `adversarial-corpus.json` (≥5 behavioral). |
| `assets/` | Optional. For templates, case studies, fixtures the skill emits or references. |

## §3 Required SKILL.md sections

A senior skill MUST have these top-level sections (H2):

| Section | Purpose | Required for |
| --- | --- | --- |
| `§ColdStartTriage` (or `## What this skill can do`) | Mode-to-reference matrix; entry-point routing | Any skill with ≥3 modes |
| `§Posture` | Operational rules: load-on-demand discipline, content-trust rule, skill-specific posture | All skills |
| `§Plan-Execute-Verify` | Per-mode verify-target table; cites `${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md` | All senior skills |
| `§SelfAudit` | Pointer to `scripts/audit-<name>-roster.mjs` | Any skill with `scripts/` |
| `§Teach` | Extensibility binding; pointer to the skill's `teach-protocol.md` | Senior skills (the rollup family) |
| `§FileMap` | Topology (subdirectories + counts); per-file enumeration delegated to an `INDEX.md` if the catalog is large | All skills |
| `§Status` | Single-line pointer to CHANGELOG.md. **No inline version narratives.** | All skills |

## §4 Required §Posture rules

Every skill's §Posture MUST include:

- **Load-on-demand discipline** — references load when needed, not preemptively
- **Content-trust** — cite `${CLAUDE_PLUGIN_ROOT}/references/shared/content-trust.md`; name the surfaces this skill reads
- **CITATION not KNOWLEDGE layer** — the skill cites the substrate by tag/ADR/spec; doesn't duplicate

Skill-specific rules (e.g., kit's "Light-DOM is load-bearing", release's "Filesystem is the substrate", a2ui's "Eval is the source of truth") are added in the §Posture below the required rules.

## §5 Required §PEV table

Per `pev-rationale.md`, every senior skill MUST have:

1. **Top-band `## §Plan-Execute-Verify` H2** (above §LoadingProtocol / §FileMap)
2. **Per-mode verify-target table** naming real-product verify (not internal self-checks)
3. **Cross-reference from §Teach** to §PEV (so §Teach landings inherit the loop)
4. **Cold-start triage mention** of PEV
5. **`skill.json description`** mentions verification or the verify target

A `scripts/skills/check-pev.mjs` substrate-side gate enforces these 5 points.

## §6 Forbidden patterns

| Pattern | Why forbidden | Detection |
| --- | --- | --- |
| Inline cross-references to monorepo-only docs (e.g. `../<monorepo-doc>.md`, `../../../.brain/adrs/*`) from skills claiming portability | These substrate-only paths don't resolve in consumer-repo invocations. Cite `${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md` instead. | grep for `../V`, `../B`, `../../../.brain/` in SKILL.md |
| Version literals in body text that drift from `skill.json version` | The body says v1.0 while skill.json says v1.7; reader's mental model becomes wrong | `audit-axes.versionLiteralParity` (from `${CLAUDE_PLUGIN_ROOT}/bin/lib/audit-axes.mjs`) |
| Phase labels in `§FileMap` (e.g., `(Phase 1)`, `(Phase 2 — planned)`) | These rot as phases complete; use `skill.json phase_status` instead | `audit-axes.phaseLabelAbsence` |
| Stale `§Status` sections with inline version narratives | The CHANGELOG is canonical; §Status duplicates and rots | Grep for `Version X.Y.Z` / `vX.Y.Z` inside §Status body |
| `SKILL.md > 50KB` for senior skills | Cold-start cost exceeds the load-on-demand discipline | `wc -c SKILL.md` |
| References to deleted/absorbed skills | Reader follows dangling link; trust erodes | `audit-axes.referenceGraph` |

## §7 Required §SelfAudit axes

Every `scripts/audit-<name>-roster.mjs` MUST check at least these axes (composable from `${CLAUDE_PLUGIN_ROOT}/bin/lib/audit-axes.mjs`):

| Axis | Check |
| --- | --- |
| **Manifest enforcement** | `skill.json files` matches `find references scripts evals -type f` (both directions: declared-but-missing + on-disk-but-undeclared); RECURSIVE walker for subdirectory catalogs |
| **Reference graph** | Every `references/*.md` link in SKILL.md or any reference file resolves to an existing file |
| **Capability-menu drift** | Every §ColdStartTriage mode row has a valid entry-reference path |
| **Version-literal parity** | SKILL.md frontmatter version matches `skill.json version`; no stale `vX.Y.Z` mentions in §Status |
| **Script existence** | Every cited `scripts/X.mjs` / `node scripts/X` exists on disk OR is explicitly labeled `(substrate-only)` |

Plus per-skill axes (e.g., authoring's "absorbed-roster currency", release's "gate-catalog roster currency", ops's "audit-pattern catalog parity").

## §8 Eval corpus minimums

Per `progressive-context-construction.md` and `evaluation-workflows.md` (in `core-skills-best-practices/references/`):

| Corpus | Minimum entries | Required adversarial fraction | File (in `evals/`) |
| --- | --- | --- | --- |
| Routing | 10 trigger + 5 adversarial | ≥33% | `routing-corpus.json` |
| Behavioral | 5 happy + 5 adversarial | ≥50% | `adversarial-corpus.json` |
| §Teach routing | 1 per branch | 0% (deterministic) | `teach-routing.json` |
| DecisionModel (composition skills only) | 3 vague-intent | 100% | `decision-corpus.json` |

Run via `${CLAUDE_PLUGIN_ROOT}/bin/lib/run-skill-evals.mjs --skill=<name>`.

## §9 Substrate-binding declaration

Skills that operate on framework-monorepo-specific infrastructure (e.g., adia-ui-release, adia-ui-a2ui) MUST declare in `skill.json`:

```json
"environment": {
  "portable": false,
  "requires": ["framework monorepo with <specific structure>"],
  "rationale": "<one-line why the skill doesn't work elsewhere>"
}
```

Skills that ARE portable declare `"portable": true`. Skills with partial portability (some modes portable, some substrate-bound) declare `"portable": "partial"` with `"portable_modes"` and `"substrate_modes"` arrays.

## §10 Cross-skill reference rules

| Reference target | Convention |
| --- | --- |
| Sibling skill's reference file | `../<sibling-skill>/references/X.md` |
| Shared infrastructure | `${CLAUDE_PLUGIN_ROOT}/references/shared/*.md` |
| Substrate code | `packages/...` / `scripts/...` — works only from the framework monorepo; if the skill is portable, vendor the relevant content or mark cross-ref as `(substrate-only)` |
| Substrate-level docs (extensibility vision, senior-review notes, etc.) | Cite via `${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md` (vendored). Do not cite monorepo-only doc paths from inside skill bodies. |

## §11 §Teach decision tree mechanization

Per the meta-refactor spec and `core-skills-best-practices/references/inversion-and-abstraction.md`:

Prose §Teach decision trees in the skill's `teach-protocol.md` MUST be paired with a `scripts/teach-route.mjs` script that:

1. Takes a payload description as input
2. Emits the landing target (file path or "no skill landing" for substrate edits / arc stories)
3. Composes from `${CLAUDE_PLUGIN_ROOT}/bin/lib/teach-router.mjs`

The prose remains for human readers (worked examples, anti-patterns, rationale). The script is the authoritative routing.
