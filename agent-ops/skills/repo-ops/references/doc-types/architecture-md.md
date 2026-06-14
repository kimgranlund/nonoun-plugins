---
date: 2026-04-27
coverage: canonical
peers:
  - adr-pattern.md
  - decisions-log.md
  - changelog.md
primary_sources:
  - https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html — Aleksey Kladov (matklad), "ARCHITECTURE.md" (the canonical pattern essay, Feb 2021)
  - https://github.com/rust-lang/rust-analyzer/blob/master/docs/dev/architecture.md — rust-analyzer's ARCHITECTURE.md (the canonical example)
  - https://github.com/sourcegraph/sourcegraph/blob/main/doc/dev/background-information/architecture/index.md — Sourcegraph's adoption of the pattern
  - https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record — Microsoft Azure WAF on architecture documentation
status: research-verified
---

# ARCHITECTURE.md — current state, in 30 minutes

> **ARCHITECTURE.md answers: "I'm new here. Where do I look first?"** Not "what did we decide?" (that's ADRs) and not "what shipped?" (that's CHANGELOG). It is a _map of the codebase as it currently is_, optimized for someone landing in the repo cold.

This pattern delivers **Promise 2 (token-and-context-optimized)** by giving an LLM agent a single high-signal entry into the codebase's structure, and **Promise 1 (less-wasteful)** by replacing the scattered "tribal knowledge" that otherwise accumulates in PR comments, Slack threads, and 3-year-old wiki pages.

## Origin and canonical source

The pattern was named and codified by **Aleksey Kladov** (handle: _matklad_, lead author of rust-analyzer) in the February 2021 blog post [**"ARCHITECTURE.md"**](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html). The canonical exemplar is rust-analyzer's own [`docs/dev/architecture.md`](https://github.com/rust-lang/rust-analyzer/blob/master/docs/dev/architecture.md).

Kladov's framing:

> "Looking at someone else's code is hard, but very useful sometimes. The best help for an outsider is a single document, a map, which describes the _bird's-eye view_ of the project, and explains how to navigate the code."

The pattern has spread widely — Sourcegraph, Tantivy, hyperqueue, ripgrep, and many others use a doc by the same name (or `architecture/` folder with the same shape).

## What ARCHITECTURE.md _is_ (and what it's not)

| ARCHITECTURE.md | Not ARCHITECTURE.md |
| --- | --- |
| Current state of the system | History of how it got here (→ git log, ADRs) |
| Map of the codebase ("Module X lives at `src/x/`") | Decision rationale ("Why did we pick X?" → ADRs) |
| 30-minute onboarding | Comprehensive technical reference (→ separate docs) |
| Names directories and the responsibility of each | Lists every file (→ tooling) |
| Cross-cutting concerns (concurrency model, error handling, lifetime) | API documentation (→ generated docs) |
| Non-obvious intentional choices ("we deliberately don't use X") | Future plans (→ ROADMAP.md) |
| Updated when architecture changes | Updated weekly (→ PLAN.md) |

The discipline is: **document things that won't change much, that an experienced engineer would still want explained.** Module purpose, layering, where-data-flows-from-input-to-output, how-tests-are-organized, what-not-to-do.

## The 30-minute onboarding shape

Kladov's recommended sections (with this skill's annotations):

### 1. Bird's-eye view

One paragraph or one diagram. What does this project _do_? Who calls it, what does it call?

```markdown
## Bird's-eye view

`acme-cli` is a Rust binary that reads YAML config from `acme.yaml`,
queries an HTTPS API, and writes Markdown reports to stdout. It has
no persistent state. It is invoked from CI in the user's repo.
```

If a diagram clarifies — use one. ASCII boxes are fine; Mermaid is fine; an image is fine. Don't gold-plate.

### 2. Code map

The load-bearing section. **For each top-level directory, one paragraph: what's in it, what's the responsibility, where the boundaries are.**

```markdown
## Code map

### `src/cli/`
Argument parsing (clap), command dispatch. No business logic — delegates to `src/core/`.

### `src/core/`
The orchestrator. Reads config, fans out to API client, aggregates results. **The only module allowed to depend on both the config layer and the API layer.**

### `src/api/`
HTTP client (reqwest). One module per endpoint group. Adding a new endpoint? Look here.

### `tests/`
Integration tests. Use the `wiremock` fixture, not real HTTP.
```

A reader (human or agent) can immediately answer: _"I want to add a new API endpoint. Where?"_

### 3. Cross-cutting concerns

Things that span modules and aren't inferable from the code map.

```markdown
## Cross-cutting concerns

- **Error handling**: `anyhow::Error` everywhere except `src/api/` (typed errors). See ADR-0007.
- **Concurrency**: single-threaded by default; `--parallel N` spawns tokio. Only `src/core/parallel.rs` knows async.
- **Logging**: `tracing`, structured JSON. `RUST_LOG` configures.
```

### 4. Non-obvious intentional choices

The "we deliberately don't do X" section. Saves future contributors hours.

```markdown
## Things we deliberately don't do

- **No async by default.** Tokio startup dominated benchmarks. See ADR-0011.
- **No plugin system.** Rejected (ADR-0014).
- **No config format other than YAML.** TOML support was removed in v1.2.0.
```

ARCHITECTURE.md _summarizes_ the decision and points at the ADR for _why_.

### 5. Where to look first

The newcomer's quick-start. Optional but high-value for LLM agents — it's a routing table for common tasks.

```markdown
## Where to look first

- **Adding a CLI flag?** `src/cli/args.rs`, then dispatch in `src/cli/mod.rs`.
- **Adding an API endpoint?** `src/api/`. Mirror an existing endpoint.
- **Investigating a CI failure?** `tests/integration/` first, then logs.
- **Performance regression?** `benches/` and `cargo bench`.
```

## Length and ergonomics

Kladov's own rust-analyzer ARCHITECTURE.md is ~600 lines. That's at the upper end. **For most repos, 200–400 lines is right.**

Under 100 lines → probably missing the code map. Over 800 lines → split. Move detail into per-module READMEs (`src/api/README.md`) and keep ARCHITECTURE.md as the bird's-eye + index.

This skill's general guidance: **entry-level docs under ~200 lines, pushed-down detail in subdirectory READMEs.** See `../guidance/context-budget.md`.

## Distinction from ADRs

The most-confused boundary: ARCHITECTURE.md is **present-tense, mutable, system-wide**; ADRs are **past-tense, immutable, per-decision**. ARCHITECTURE.md answers "Where does X live?"; ADRs answer "Why did we choose X?". ARCHITECTURE.md _links_ to ADRs ("see ADR-0007"), never duplicates them.

## Update discipline

ARCHITECTURE.md goes stale faster than ADRs and slower than PLAN.md. Recommended cadence:

1. **PR-level**: any PR that adds, renames, or removes a top-level directory must update ARCHITECTURE.md in the same PR. Enforce with a CI check or a CODEOWNERS rule. See `../recipes/self-healing-hooks.md`.
2. **Quarterly review**: a maintainer re-reads ARCHITECTURE.md against the current tree and patches drift.
3. **LLM-on-diff**: when a large refactor lands, run an LLM-on-diff pass against ARCHITECTURE.md to flag suspect sections. See `../audit-patterns/staleness-tooling.md`.

## How AGENTS.md links ARCHITECTURE.md

In the `Where to find things` section:

```markdown
- **Architecture:** `ARCHITECTURE.md` — start here if you're new to the codebase
```

In the `Memory primitives` section:

```markdown
- **Before making changes that span multiple modules**, read `ARCHITECTURE.md` for the code map and cross-cutting concerns. Architecture-altering changes also require a new ADR.
```

`ARCHITECTURE.md` at repo root is the recommended location (matklad's pattern). Avoid `.agents/brain/architecture/index.md` unless you have a folder full of related docs.

## Audit checks

1. **File exists** at `/ARCHITECTURE.md` (repo root, per matklad).
2. **Code map covers all top-level src directories.** Diff `ls src/` against the headings in the code map; missing entries = staleness.
3. **No directory mentioned in the code map is missing from disk.** Renames or removals that didn't update the doc.
4. **Length is in 100–800 range.** Both extremes are flagged.
5. **AGENTS.md references ARCHITECTURE.md**, not just `.agents/brain/`.
6. **`Last reviewed:` line or YAML `date:` is within the last 180 days.** Older = quarterly review missed.

## Common anti-patterns

- **No ARCHITECTURE.md** — newcomers and agents navigate by `ls` and pattern-match. Slow.
- **Feature list, not a code map** — describes what the product does, not how it's built.
- **History, not present-tense** — narrates evolution. That's a blog post.
- **Duplicates ADR content** — copy-pasted "why" rationale. Link to the ADR instead.
- **Alphabetical code map** — group by responsibility (core → adapters → entry-points).
- **Stale code map** — directories renamed in code, not in the doc. Catch with the audit.
- **Outsourced to a wiki** — agents can't read Confluence; drift is guaranteed. Keep it in the repo.

## Cross-references

- ADR pattern (decisions, not state): `adr-pattern.md`
- Decision log (collection of ADRs): `decisions-log.md`
- Changelog (shipped, not state): `changelog.md`
- Plan / roadmap (planned, not state): `plan-roadmap.md`
- Self-healing PR-gate hooks: `../recipes/self-healing-hooks.md`
- LLM-on-diff staleness detection: `../audit-patterns/staleness-tooling.md`
- Context budget guidance (200-line target): `../guidance/context-budget.md`
- AGENTS.md "Where to find things" section: `../standards/agents-md-spec.md`
