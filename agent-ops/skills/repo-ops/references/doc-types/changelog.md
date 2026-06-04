---
date: 2026-04-27
coverage: canonical
peers:
  - plan-roadmap.md
  - decisions-log.md
  - architecture-md.md
primary_sources:
  - https://keepachangelog.com/en/1.1.0/ — Keep a Changelog 1.1.0 (the canonical convention)
  - https://semver.org/spec/v2.0.0.html — Semantic Versioning 2.0.0
  - https://github.com/changesets/changesets — changesets (monorepo-friendly)
  - https://github.com/orhun/git-cliff — git-cliff (commit-message-driven generator)
  - https://github.com/googleapis/release-please — release-please (Conventional-Commits release automation)
  - https://www.conventionalcommits.org/en/v1.0.0/ — Conventional Commits 1.0.0
status: research-verified
---

# CHANGELOG.md — what shipped, organized for humans

> **A changelog is for humans, not machines.** That single line, from [keepachangelog.com](https://keepachangelog.com/en/1.1.0/), is the load-bearing principle. An auto-generated dump of commit messages is _not_ a changelog — it's a commit log with a different filename.

This pattern delivers **Promise 1 (less-wasteful)** by giving the agent a single canonical "what shipped, when" surface, and **Promise 5 (continuously-learning)** by giving the team a release ritual that captures intent, not just diffs.

## The Keep-a-Changelog convention (canonical)

[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) is the de facto industry standard. It defines:

### Six change categories — pick from these, do not invent new ones

| Category       | Meaning                                           |
| -------------- | ------------------------------------------------- |
| **Added**      | New features                                      |
| **Changed**    | Changes in existing functionality                 |
| **Deprecated** | Soon-to-be-removed features (still works for now) |
| **Removed**    | Now-removed features                              |
| **Fixed**      | Bug fixes                                         |
| **Security**   | Vulnerabilities patched (cite CVE if applicable)  |

### The "Unreleased" section pattern

The top of every active CHANGELOG.md has an `## [Unreleased]` section. Engineers add entries there as they merge PRs. At release time, the `[Unreleased]` heading is renamed to `[X.Y.Z] - YYYY-MM-DD` and a fresh empty `[Unreleased]` is added at the top.

This means the changelog is _always_ drafting the next release; it never lags behind.

### Date format

ISO 8601 (`YYYY-MM-DD`). Always. Anything else triggers ambiguity (US vs EU date order).

### Newest-on-top ordering

Most recent release at the top. The most-recently-shipped change is what the agent (and humans) usually want to know about.

## Sample minimal CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `--strict` flag to validate frontmatter before commit.

### Fixed
- Pointer validator no longer crashes on Windows path separators (#412).

## [1.4.0] - 2026-04-19

### Added
- Pre-commit hook scaffold for AGENTS.md freshness checks.
- Lychee-based broken-link detector wired into CI.

### Changed
- Default ADR template upgraded to MADR 4.0.0.

### Deprecated
- `--legacy-format` flag; will be removed in 2.0.0.

## [1.3.1] - 2026-03-22

### Fixed
- Crash on empty `.brain/postmortems/` folder (#388).

### Security
- Bumped `@some/dep` to 4.2.1 to patch CVE-2026-12345.

[Unreleased]: https://github.com/acme/repo/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/acme/repo/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/acme/repo/compare/v1.3.0...v1.3.1
```

The reference links at the bottom let readers click through to the diff. Tools regenerate them automatically.

## Relationship to git tags and SemVer

[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) gives the version-number meaning:

- **MAJOR** — incompatible API change
- **MINOR** — backward-compatible new feature
- **PATCH** — backward-compatible bug fix

The CHANGELOG is the **human narrative** that justifies the version bump. The git tag is the **machine pointer** to the commit that release was cut from.

Convention: tag is `vX.Y.Z` (with the `v` prefix); changelog heading is `[X.Y.Z]` (without the `v`). The reference link at the bottom of the changelog connects them.

The changelog **drives** the version, not the reverse. If `Unreleased` has only `Fixed` entries → next release is PATCH. If it has `Added` → MINOR. If it has `Removed` of a public API → MAJOR.

## Tooling — automation that helps vs. automation that hurts

### Tools that help

| Tool | Approach | Best for |
| --- | --- | --- |
| **[changesets](https://github.com/changesets/changesets)** | Each PR adds a `.changeset/*.md` describing the change + intended bump; CI aggregates at release time | Monorepos (especially `pnpm` workspaces); strong fit for libraries |
| **[release-please](https://github.com/googleapis/release-please)** | Reads Conventional Commits, opens release PRs that update CHANGELOG and bump version | Repos already on Conventional Commits; lightweight to adopt |
| **[git-cliff](https://github.com/orhun/git-cliff)** | Highly configurable Conventional-Commits → CHANGELOG generator | Teams that want full templating control |

All three preserve the **categorical narrative** — they classify changes into Added/Changed/Fixed/etc. via commit-prefix conventions, not just paste commit messages.

### The auto-generated-commits anti-pattern

```markdown
## v1.4.0

- Merge pull request #412 from feat/hooks
- Update README.md
- chore(deps): bump foo from 1.0 to 1.1
- fix lint
- wip
- address review
- Merge pull request #418 from fix/edge
```

This is **not a changelog**. It is a low-signal commit dump with no narrative. The agent (and humans) get nothing actionable from it.

If you can't justify the cost of writing categorized entries, **do not auto-generate this**. Instead: link to GitHub Releases or `git log --oneline` from a brief CHANGELOG note. At least that's honest about what it is.

## How AGENTS.md links the changelog

In the `Where to find things` section:

```markdown
- **Released changes:** `CHANGELOG.md` — what shipped, by version, newest-first
```

In the `Memory primitives` section:

```markdown
- **Before claiming "feature X exists/doesn't exist"**, check `CHANGELOG.md` — features are added, removed, deprecated over time. The current state is the diff of all releases.
```

## Audit checks

1. **`CHANGELOG.md` exists at repo root.** Not in `.brain/`. Convention is root.
2. **Header credits Keep a Changelog and SemVer.** A common 2-line preamble; signals the format.
3. **An `[Unreleased]` section exists at the top.** Without it, the changelog is always lagging.
4. **Every release entry has an ISO date** (`YYYY-MM-DD`).
5. **Categories used are from the Keep-a-Changelog set** (Added, Changed, Deprecated, Removed, Fixed, Security). Custom categories like "Misc" or "Other" → flag.
6. **Latest release date in CHANGELOG matches latest git tag.** Drift = either an untagged release or an unreleased changelog entry.
7. **Reference-link footnotes resolve** — `[1.4.0]: https://…` URLs are reachable. Lychee catches this; see `../audit-patterns/staleness-tooling.md`.

## Common anti-patterns

- **No CHANGELOG** — releases are silent; GitHub Releases is the only narrative.
- **Auto-generated commit dump** — discussed above. Low-signal noise.
- **CHANGELOG inside `.brain/`** — convention is repo root; tools look there.
- **Mixed date formats** (`19-04-2026`, `Apr 19 2026`). ISO only.
- **Invented categories** ("New stuff", "Tweaks") — stick to the canonical six.
- **No `[Unreleased]` section** — entries get lost between releases.
- **Skipped versions** (1.3.0 → 1.5.0) — usually a hot-fix branch wasn't backported.
- **Overlap with ROADMAP** — CHANGELOG is shipped past; ROADMAP is unshipped future. See `plan-roadmap.md`.

## Cross-references

- Plan / roadmap (forward-looking, not shipped): `plan-roadmap.md`
- Decision log (decisions, not features): `decisions-log.md`
- Architecture overview (current state, not history): `architecture-md.md`
- Self-healing release automation: `../recipes/self-healing-hooks.md`
- Staleness detection: `../audit-patterns/staleness-tooling.md`
- AGENTS.md memory primitives section: `../standards/agents-md-spec.md`
