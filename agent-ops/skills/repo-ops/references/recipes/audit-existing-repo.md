---
date: 2026-04-27
coverage: canonical
peers:
  - greenfield-setup.md
  - adr-introduction.md
  - memory-organization.md
primary_sources:
  - SKILL.md (this skill's own audit categories)
status: needs-research-enhancement
---

# Recipe: audit an existing repo

> **The end-to-end procedure** for running `repo-ops` against a real repo and producing an actionable gap report. Includes the v1.5 `.agents/brain/` layout migration recipe.

## Inputs

- A path to a git repo (working tree)
- Optional: severity threshold (`critical` / `high` / `medium` / `low`) — default `medium`
- Optional: write-mode flag (`recommend-only` / `apply-fixes`) — default `recommend-only`

## Outputs

- `stale-docs-audit.md` (or stdout) with the gap report
- (If `apply-fixes`) edits to `AGENTS.md`, `CLAUDE.md`, etc., or new files in `.agents/brain/`

## The 7-step procedure

### Step 1 — Discovery

Enumerate everything that matters:

```bash
# Entry-file candidates at root
ls -la AGENTS.md CLAUDE.md README.md CONTRIBUTING.md SECURITY.md \
       .cursorrules .windsurfrules .aider.conf.yml 2>/dev/null

# Cursor newer-style rules folder
ls -la .cursor/rules/ 2>/dev/null

# Continue config
ls -la .continue/ 2>/dev/null

# GitHub Copilot instructions
ls -la .github/copilot-instructions.md 2>/dev/null

# Brain artifacts (v1.5 layout) + legacy docs/ tree
find .agents/brain docs -type f -name '*.md' 2>/dev/null
find . -maxdepth 2 \( -name 'CHANGELOG*.md' -o -name 'ARCHITECTURE.md' -o -name 'PLAN.md' -o -name 'ROADMAP.md' \) 2>/dev/null
```

Build two sets:

- **EntryFiles**: files found at the root that are entry candidates
- **DocFiles**: files found anywhere under `.agents/brain/` or `docs/`, plus well-known top-level docs (CHANGELOG.md, ARCHITECTURE.md, PLAN.md, ROADMAP.md)

**Git-sync mode detection.** Check `.gitignore`. If `.agents/brain/` (the directory itself, not just `.agents/brain/cache/` or `.agents/brain/cold-start/`) appears in `.gitignore`, the repo is in `local-only` mode (per `../guidance/reliability-dial.md` § Git sync). The audit still runs against the working tree, but Promise 5 findings apply to the local clone only — multi-contributor recipes (`concurrent-learnings-merge.md`, `cold-start-harvest.md`) and the auto-archive PR workflow are moot in this mode and should be skipped.

### Step 2 — Pointer trace

For each file in `EntryFiles`, parse it as Markdown and extract every relative-path link or backtick-quoted path. Build a set:

- **PointedTo**: union of all paths referenced from any entry file

Cross-check against `DocFiles`:

- **PointedTo ∩ DocFiles** — files reachable from entry. ✅
- **PointedTo \ DocFiles** — referenced but missing. ❌ _Broken pointer._
- **DocFiles \ PointedTo** — exist but unreachable. 🟡 _Orphan._

### Step 3 — Canonical determination

Decide which entry file is _canonical_ (the one that should hold instructions; others should redirect to it).

Decision tree:

```text
Is AGENTS.md present and ≥30 lines?
  YES → AGENTS.md is canonical.
  NO  → Is exactly one fat (≥30 lines) entry file present?
          YES → Recommend renaming it to AGENTS.md.
          NO  → Are multiple fat files present?
                  YES → DRIFT. Recommend consolidation.
                  NO  → No canonical file. CRITICAL gap.
```

### Step 4 — Thin-pointer compliance

For every entry file that is NOT canonical, verify it's a thin pointer:

- Length ≤ 15 lines
- References the canonical file by name
- No substantive instructions of its own

Findings:

- **Fat non-canonical** → drift risk → recommend converting to pointer.
- **Wrong target** → e.g. CLAUDE.md exists, points at `AGENTS.md`, but AGENTS.md doesn't exist → broken redirect.

### Step 5 — Memory-primitive check

For each of the standard memory homes, check existence and pointer-from-AGENTS.md:

| Home | Required? | If missing |
| --- | --- | --- |
| `.agents/brain/adrs/` (or legacy `docs/adrs/`) | Recommended | "No ADR home — recommend introducing them. See `recipes/adr-introduction.md`." |
| `.agents/brain/decisions/` | Optional | If absent and no ADRs either, both flagged. |
| `.agents/brain/postmortems/` (or legacy `docs/postmortems/` / `docs/incidents/`) | Optional | Flag only if repo has had production incidents (heuristic: search for `incident`, `outage`, `post-mortem` in commit log). |
| `CHANGELOG.md` | Strongly recommended | Flag as gap if missing. |
| `.agents/brain/runbooks/` (or legacy `docs/runbooks/`) | Optional | Flag if production-facing repo. |

### Step 6 — Staleness probe

For each file in `DocFiles`:

- **Last modified** > 6 months ago AND **no `_Last reviewed:_` line** → flag as needs-review.
- File contains references to symbols/files that no longer exist in the repo → flag as broken-reference.
- File contains commands that fail dry-run (e.g., `npm install` but project is pnpm) → flag as command-stale. (Best-effort; may require running commands.)

### Step 7 — Synthesize the gap report

Write `stale-docs-audit.md` with sections:

```markdown
# Stale-docs audit — <repo name>

_Generated: 2026-04-27_

## Summary

- **Critical**: 1 finding
- **High**: 3 findings
- **Medium**: 7 findings
- **Low**: 4 findings

## Critical

### MISSING — AGENTS.md
[detail per the entry-file-coverage.md output shape]

## High

### DRIFT — CLAUDE.md vs .cursorrules
[detail]

### NO ADR HOME
The repo has architectural decisions scattered across PR descriptions and code
comments but no `.agents/brain/adrs/`. Recommend introducing ADRs.

[continue per severity]

## Recommended fixes (ordered)

1. Rename `CLAUDE.md` → `AGENTS.md`; create thin `CLAUDE.md` redirect.
2. Create `.agents/brain/adrs/` with `0001-record-architecture-decisions.md`.
3. Add "Where to find things" and "Memory primitives" sections to AGENTS.md.
4. Update `.cursorrules` to be a thin pointer.
5. Resolve drift between CLAUDE.md and .cursorrules: pnpm vs npm.

## Suggested edits (when in apply-fixes mode)

[concrete diffs — not applied without explicit user confirmation]
```

## Migration: legacy `docs/` layout → `.agents/brain/`

If the audit finds memory artifacts in `docs/{adrs,postmortems,runbooks,archive,architecture}/` (the pre-v1.5 layout), the recommended migration is one git move that preserves history:

```bash
mkdir -p .agents/brain

# Move each memory primitive that exists. Skip silently if absent.
[ -d docs/adrs ]         && git mv docs/adrs         .agents/brain/adrs
[ -d docs/postmortems ]  && git mv docs/postmortems  .agents/brain/postmortems
# Or if the repo used the docs/incidents alias:
[ -d docs/incidents ] && [ ! -d .agents/brain/postmortems ] && git mv docs/incidents .agents/brain/postmortems
[ -d docs/runbooks ]     && git mv docs/runbooks     .agents/brain/runbooks
[ -d docs/archive ]      && git mv docs/archive      .agents/brain/archive
[ -d docs/architecture ] && git mv docs/architecture .agents/brain/architecture
[ -d docs/repo-ops/audit-history ] && git mv docs/repo-ops/audit-history .agents/brain/audit-history

# Config + transient state homes
[ -f .repo-ops.toml ] && git mv .repo-ops.toml .agents/brain/config.toml
[ -d .repo-ops/changesets ] && git mv .repo-ops/changesets .agents/brain/changesets

git commit -m "chore: migrate memory layer to .agents/brain/ (repo-ops v1.5)"
```

After the move, also update:

- **`AGENTS.md`** — every "Where to find things" pointer (`docs/adrs/` → `.agents/brain/adrs/`, etc.)
- **`.gitignore`** — add `.agents/brain/cache/` and `.agents/brain/cold-start/working/` (transient state)
- **`.github/workflows/`** — rename `repo-fixer-*.yml` → `repo-brain-*.yml` if hooks were installed pre-v1.3
- **Workflow path filters / lychee globs** — add `'.agents/brain/**/*.md'` next to `'docs/**/*.md'` (verbatim recipes in `self-healing-hooks.md`)

The audit recognizes either layout — **migration is opt-in for v1.5**, not enforced. Repos that prefer the established `docs/{adrs,...}/` convention can stay there; the audit's checks adapt. Greenfield setup defaults to `.agents/brain/`.

**What stays at the repo root regardless of layout:**

- `AGENTS.md`, `CLAUDE.md`
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`
- `ARCHITECTURE.md` (matklad pattern)
- `CHANGELOG.md`
- `PLAN.md`, `ROADMAP.md` (if used)

## Apply-fixes mode safety rules

When `apply-fixes` is on:

1. **Never delete a file** without showing the user and asking.
2. **Never overwrite a file >50 lines** without showing a diff and asking.
3. **Always commit each fix as a separate commit** with a clear message — this is reversible.
4. **Never rewrite git history.**
5. If asked to delete an orphaned doc, prefer **moving to `.agents/brain/archive/`** with a date suffix over outright deletion.

## Common findings on real repos

From running this audit across real-world projects, the most frequent gaps:

1. **No AGENTS.md, fat CLAUDE.md** — repo predates the standard or only used Claude Code.
2. **No "Where to find things" section** — naked entry; agent has nothing to navigate.
3. **CLAUDE.md and .cursorrules drifted** — duplicate maintenance burden, rarely consistent.
4. **No ADR home** — decisions scattered across PRs.
5. **Stale build commands** — entry file says `npm` but repo migrated to pnpm/bun.
6. **Orphaned `docs/old-plan.md`** — never cleaned up after being superseded.
7. **Undated `ARCHITECTURE.md`** — no way to know if it's current.
8. **Pre-v1.5 `docs/` layout** — opportunity to migrate to `.agents/brain/` (see § Migration above).

## Cross-references

- Entry-file checks: `../audit-patterns/entry-file-coverage.md`
- Pointer validation: `../audit-patterns/pointer-validation.md`
- Orphan detection: `../audit-patterns/orphan-detection.md`
- Greenfield setup: `greenfield-setup.md`
- Adding ADRs to existing repo: `adr-introduction.md`
