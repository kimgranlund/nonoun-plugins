---
date: 2026-05-06
---

# repo-ops — Reference Index

_Authoritative manifest of reference files. v1.7.0 — released 2026-05-02 (skill-stewardship as co-equal artifact class; harvest+import flow operations; +4 audit-patterns; v1.6 added findings-index readout + postmortem trigger rules; v1.5 introduced `.brain/` layout + prose-and-writing genre axis)._

## The five promises

The artifacts compound, not the agents. Agents stay deterministic; humans curate; trip-wires enforce structure (per Yegge, "Welcome to Gas City").

| # | Promise | Primary references |
| --- | --- | --- |
| 1 | Less-wasteful | `audit-patterns/orphan-detection.md`, `audit-patterns/redundancy-detection.md`, `audit-patterns/coverage-gaps.md`, `audit-patterns/changelog-unreleased-bloat.md` |
| 2 | Token-and-context-optimized | `guidance/context-budget.md`, `guidance/llm-doc-writing.md`, `audit-patterns/token-waste-detection.md` |
| 3 | Less-prone-to-staleness | `audit-patterns/staleness-tooling.md`, `audit-patterns/stale-content.md`, `audit-patterns/format-hygiene.md`, `audit-patterns/spec-dating-sweep.md`, `audit-patterns/archive-link-sweep.md`, `audit-patterns/browser-bundle-node-imports.md` |
| 4 | Self-healing | `recipes/self-healing-hooks.md`, `recipes/recommend-then-validate.md`, `audit-patterns/lockstep-versioning.md`, `audit-patterns/browser-bundle-node-imports.md` |
| 5 | Continuously-learning indefinitely (declarative + procedural memory) | `recipes/continuous-learning-loop.md`, `recipes/findings-index-readout.md`, `recipes/skill-stewardship-loop.md`, `audit-patterns/memory-fragmentation.md`, `audit-patterns/audit-history-ledger.md`, `doc-types/adr-pattern.md`, `doc-types/postmortem-pattern.md` |
| — | **Reliability dial** (cross-cutting) | `guidance/reliability-dial.md` (configures every trip-wire's threshold via `.brain/config.toml`) |
| — | **Flow operations** (cross-cutting) | `recipes/harvest-repo-brain.md`, `recipes/import-repo-brain-harvest.md` (bridge brain matter into agent memory + portable bundles) |

## Status legend

- ✅ — present, research-verified, current

## Axes (6)

| # | Axis | Files | Purpose |
| --- | --- | --- | --- |
| 1 | `standards/` | 4 | Entry-file conventions for major LLM coding agents |
| 2 | `doc-types/` | 6 | Common doc-file types and their canonical formats |
| 3 | `audit-patterns/` | 15 | What each audit category checks (Promises 1, 2, 3, 4, 5) |
| 4 | `guidance/` | 3 | Content-quality + reliability-dial guidance (Promise 2 + cross-cutting) |
| 5 | `recipes/` | 15 | End-to-end procedures (Promises 3, 4, 5; multi-contributor + cold-start + harvest/import + skill-stewardship + audit-recall eval) |
| 6 | `genres/` | 1 | Applying repo-ops to non-code domains (prose, fiction, technical writing) |
|  | **Total** | **44** | (plus this INDEX, SKILL.md, CHANGELOG.md, skill.json) |

## File manifest

### standards/ (4)

| Status | Path | Purpose |
| --- | --- | --- |
| ✅ | `standards/agents-md-spec.md` | AGENTS.md as canonical (AAIF/Linux Foundation, Aug 2025, 60K+ projects) |
| ✅ | `standards/claude-md-convention.md` | CLAUDE.md as thin pointer / symlink (Claude Code does NOT read AGENTS.md natively as of April 2026) |
| ✅ | `standards/cross-tool-matrix.md` | Codex, Devin, Cursor, Windsurf, Copilot, Aider, Continue, Jules, Junie, Amp — what each reads natively |
| ✅ | `standards/readme-conventions.md` | README.md / CONTRIBUTING.md / SECURITY.md / CODE_OF_CONDUCT.md — 9-row redundancy matrix |

### doc-types/ (6)

| Status | Path | Purpose |
| --- | --- | --- |
| ✅ | `doc-types/adr-pattern.md` | Nygard, MADR 4.0.0, Y-statements; decision-log canonical meaning |
| ✅ | `doc-types/architecture-md.md` | matklad (Aleksey Kladov) ARCHITECTURE.md pattern |
| ✅ | `doc-types/changelog.md` | Keep-a-Changelog 1.1.0; SemVer; auto-gen anti-pattern |
| ✅ | `doc-types/decisions-log.md` | Canonical meaning = collection of ADRs (Microsoft/AWS/adr.github.io); team-split alternative |
| ✅ | `doc-types/plan-roadmap.md` | PLAN.md vs ROADMAP.md; cadence; TODO-graveyard anti-pattern |
| ✅ | `doc-types/postmortem-pattern.md` | Google SRE blameless template + Atlassian template |

### audit-patterns/ (15)

| Status | Path | Purpose | Promise |
| --- | --- | --- | --- |
| ✅ | `audit-patterns/archive-link-sweep.md` | Depth-aware path rewrites after cross-tree doc moves (e.g. docs/X.md → .brain/archive/Y.md); per-file `(old, new)` tuples in Python | 1, 3 |
| ✅ | `audit-patterns/audit-history-ledger.md` | Persistent JSON record per audit run (`.brain/audit-history/`); SOC2-friendly | 5 |
| ✅ | `audit-patterns/browser-bundle-node-imports.md` | Top-level static `import 'node:*'` in modules reachable from browser bundles; Vite's externalization stub throws on property access at module init. Discriminating grep + dual-mode fix pattern from chat-ui §72 follow-up | 3, 4 |
| ✅ | `audit-patterns/changelog-unreleased-bloat.md` | After release cuts, `[Unreleased]` blocks accumulate stale promoted-content; periodic clear | 1, 3 |
| ✅ | `audit-patterns/coverage-gaps.md` | Missing canonical files (3-tier rubric: required / conditional / advisory) | 1, 5 |
| ✅ | `audit-patterns/entry-file-coverage.md` | Entry files exist, well-formed, point at `.brain/` | 1 |
| ✅ | `audit-patterns/format-hygiene.md` | Form checks: dates, frontmatter, status, severity (precondition for staleness) | 3 |
| ✅ | `audit-patterns/lockstep-versioning.md` | Multi-package monorepo pre-1.0 caret-lock trap; coordinated bumps + CI gate | 4, 5 |
| ✅ | `audit-patterns/memory-fragmentation.md` | Scattered ADRs, missing memory-primitives section in AGENTS.md | 5 |
| ✅ | `audit-patterns/orphan-detection.md` | Files in `.brain/` or `docs/` not reachable from any entry (transitive closure) | 1 |
| ✅ | `audit-patterns/pointer-validation.md` | Cross-references resolve to real files | 1, 3 |
| ✅ | `audit-patterns/redundancy-detection.md` | Drift between CLAUDE.md/AGENTS.md; repeated commands; repeated facts | 1 |
| ✅ | `audit-patterns/spec-dating-sweep.md` | Specs without `date:` frontmatter or `_Last reviewed:_` are invisible to staleness detection; backfill from git log | 3 |
| ✅ | `audit-patterns/stale-content.md` | git-mtime + symbol-grep + command-vs-lockfile heuristics | 3 |
| ✅ | `audit-patterns/staleness-tooling.md` | lychee, Vale, markdownlint, LLM-on-diff, git-mtime baseline | 3 |
| ✅ | `audit-patterns/token-waste-detection.md` | Bloated entry files, bloated subfolder docs, verbose prose | 2 |

### guidance/ (3)

| Status | Path | Purpose | Promise |
| --- | --- | --- | --- |
| ✅ | `guidance/context-budget.md` | Token math, 200-line ceiling, layered docs, compression recipe | 2 |
| ✅ | `guidance/llm-doc-writing.md` | Anthropic <200-line guidance + GitHub Blog 2,500-repo empirical findings | 2 |
| ✅ | `guidance/reliability-dial.md` | `.brain/config.toml` strictness (lax / normal / strict) + git-sync (shared / local-only); per-trip-wire threshold routing | cross-cutting |

### recipes/ (15)

| Status | Path | Purpose | Promise |
| --- | --- | --- | --- |
| ✅ | `recipes/adr-introduction.md` | Retrofit ADRs into an established repo (anti-burnout) | 5 |
| ✅ | `recipes/audit-existing-repo.md` | Full audit pass with 7-step procedure + `.brain/` migration recipe | All |
| ✅ | `recipes/audit-recall-eval.md` | **Audit-recall eval**: planted-defect fixture (10 categories) + recall-per-category measurement — does the audit catch what it claims? Ships as spec+procedure (run in target repo) | 4, 5 |
| ✅ | `recipes/cold-start-harvest.md` | Importing existing learnings (inventory → triage → archive-not-delete → human-reviewed supersession) | All |
| ✅ | `recipes/concurrent-learnings-merge.md` | Multi-contributor sync-and-reason: timestamp ADRs, AGENTS.md changesets, post-merge redundancy scan, supersession protocol | 5 |
| ✅ | `recipes/continuous-learning-loop.md` | Anthropic iterate pattern + ADR-on-change + postmortem-on-incident | 5 |
| ✅ | `recipes/external-reference-verification.md` | WebFetch-powered probe for cited URLs (Karpathy autoresearch DNA); catches live-link-stale-content | 3 |
| ✅ | `recipes/findings-index-readout.md` | Close the read side of the audit ledger — `.brain/findings/INDEX.md` aggregates all `findings[]` across `audit-history/*.json`; status taxonomy with auto-promotion to CLOSED-LATER; hand-curated `## Graduations` section | 5 |
| ✅ | `recipes/greenfield-setup.md` | Day-one setup with `.brain/` layout that ships all 5 promises from first commit | All |
| ✅ | `recipes/harvest-repo-brain.md` | **Flow operation**: lift findings from `.brain/` + `docs/conventions/` into agent memory at `~/.claude/projects/<repo>/memory/` and (optionally) emit a portable bundle for cross-repo ingestion | Cross-cutting |
| ✅ | `recipes/import-repo-brain-harvest.md` | **Flow operation**: inverse of harvest. Consumes a portable bundle into this repo's `.brain/` then runs the harvest pipeline so merged content propagates to memory + harness | Cross-cutting |
| ✅ | `recipes/memory-organization.md` | ADR vs runbook vs postmortem vs decisions decision-tree | 5 |
| ✅ | `recipes/recommend-then-validate.md` | Two-agent fix pattern (Yegge); required for `strict` strictness | 4 |
| ✅ | `recipes/self-healing-hooks.md` | Pre-commit + GitHub Actions + auto-archive workflow | 4 |
| ✅ | `recipes/skill-stewardship-loop.md` | **Procedural memory**: audit-and-iterate loop for `.claude/skills/`. Pairs with four reference scripts (check-skill-frontmatter, audit-skills, draft-skill, iterate-skill) and six detection signals | 5 |

### genres/ (1)

| Status | Path | Purpose | Promise |
| --- | --- | --- | --- |
| ✅ | `genres/prose-and-writing.md` | Applying repo-ops to non-code domains: technical writing, fiction, journalism. Vocabulary translation (ADR → EDR, postmortem → revision retrospective). Five-promise applicability table. | All (with translation) |

## Layout (v1.5)

The canonical artifact home is `.brain/`:

```text
repo-root/
├── AGENTS.md             # entry file (canonical)
├── CLAUDE.md             # symlink → AGENTS.md OR thin pointer
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── ARCHITECTURE.md       # matklad pattern; repo root
├── CHANGELOG.md
├── PLAN.md (optional)
├── ROADMAP.md (optional)
├── .brain/
│   ├── config.toml       # was .repo-ops.toml
│   ├── adrs/             # numbered ADRs
│   ├── postmortems/      # blameless incident write-ups
│   ├── runbooks/         # operational procedures
│   ├── archive/          # superseded/abandoned (auto-archived after 30d)
│   ├── architecture/     # diagrams + extended docs
│   ├── audit-history/    # JSON ledger (queryable, SOC2-friendly)
│   ├── changesets/       # AGENTS.md changesets staging (multi-contributor)
│   ├── cache/            # WebFetch cache (gitignored)
│   └── cold-start/       # harvest working state (gitignored)
└── docs/                 # genuine human prose (tutorials, API ref, getting-started)
```

Legacy `docs/{adrs,postmortems,runbooks,archive,architecture}/` is recognized by the audit; migration is opt-in via one `git mv` (recipe in `recipes/audit-existing-repo.md` § Migration).

## Conventions

- **YAML frontmatter** on every reference file: `date` (ISO), `coverage` (canonical/extended/esoteric/advisory), `peers`, `primary_sources`, `status` (research-verified).
- **Cross-references use relative paths** (e.g., `../standards/<file>.md`).
- **Every claim cites a source.** No fabricated specifications, RFCs, or commit SHAs.
- **Each file maps to at least one of the 5 promises and says so explicitly.**
- **Length target**: most reference files 120-180 lines; long-form deep dives (self-healing-hooks, context-budget) up to ~350 lines.

## Companion files at skill root

- [`SKILL.md`](../SKILL.md) — flat-prose entry, 5-promises framework, two-tier decompose, §SelfAudit, verify target, route table. v1.10.0.
- `CHANGELOG.md` — version history. v1.10.0 adds routing corpus, two-tier decompose, §SelfAudit, output naming convention.
- `skill.json` — machine-readable manifest, v1.10.0, status `stable`.
- The routing-corpus eval — routing accuracy baseline: 14 trigger phrases + 6 adversarial phrases (first baseline, v1.10.0).
