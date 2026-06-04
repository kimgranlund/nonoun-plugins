---
date: 2026-04-27
coverage: canonical
peers:
  - decisions-log.md
  - architecture-md.md
  - postmortem-pattern.md
primary_sources:
  - Michael Nygard, "Documenting Architecture Decisions" (cognitect.com/blog/2011/11/15) — the original ADR essay
  - https://adr.github.io — ADR organization (canonical hub)
  - https://github.com/joelparkerhenderson/architecture-decision-record — Joel Parker Henderson's ADR catalog (most-cited examples library, actively maintained)
  - https://adr.github.io/madr/ — MADR 4.0.0 (released 2024-09-17, "Markdown Any Decision Records")
  - https://medium.com/olzzio/y-statements-10eb07b5a177 — Olaf Zimmermann, Y-statements (SATURN 2012)
  - https://github.com/npryce/adr-tools — adr-tools CLI (lightly maintained)
  - https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record — ADR / Decision Log canonical meaning
status: research-verified
---

# Architecture Decision Records (ADRs)

> **One ADR captures one architectural decision and its context — _immutably_.** Decisions don't get edited; they get superseded. The newest ADR wins; older ADRs remain as history.

## What an ADR is (and isn't)

An ADR is a **dated, numbered, status-bearing Markdown file** that captures:

- **Why** a decision was made (the problem and constraints)
- **What** was decided (the chosen path)
- **What was considered** (the alternatives and why they lost)
- **Consequences** (the trade-offs the team is signing up for)

An ADR is **not** a design doc, RFC, spec, or proposal. Those describe future work; an ADR records a _commitment that has been made_. Once accepted, it is rarely edited — instead, a new ADR supersedes it.

## File layout

Standard:

```text
.brain/adrs/
├── 0001-record-architecture-decisions.md
├── 0002-use-postgres-not-mysql.md
├── 0003-rest-not-graphql.md
├── 0004-deprecate-redis-cache.md
└── README.md
```

Numbering is strictly sequential. Filename pattern: `NNNN-kebab-case-title.md`.

## The Nygard format (canonical, ~2011)

Michael Nygard's [original 2011 essay](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) gave the field its first standard:

```markdown
# 1. Record architecture decisions

Date: 2026-04-27

## Status

Accepted

## Context

What is the issue we're seeing that motivates this decision?

## Decision

What is the change we're making?

## Consequences

What becomes easier or harder because of this change?
```

Five sections: Title, Date, Status, Context, Decision, Consequences. Short and disciplined.

## Status values

The set is small and load-bearing:

| Status | Meaning |
| --- | --- |
| `Proposed` | Drafted, under discussion, not yet accepted |
| `Accepted` | Decided. The team is committed. |
| `Rejected` | Considered and not adopted. Recorded so it doesn't get re-proposed without context. |
| `Deprecated` | No longer active but not yet replaced |
| `Superseded by ADR-NNNN` | Replaced by a newer decision |

## ADR vs Architecture Decision Log (ADL) — canonical meaning

The widely-cited industry view (Microsoft Azure Well-Architected Framework, AWS Prescriptive Guidance, adr.github.io):

> "An Architectural Decision Record (ADR) captures a single AD and its rationale; **the collection of ADRs constitutes the decision log.**"

So the canonical "decision log" is **the index of all ADRs** in `.brain/adrs/`, not a separate folder. Generate it from filenames + status fields, or maintain `.brain/adrs/README.md` as a hand-written index.

Some teams _additionally_ maintain a lighter `.brain/decisions/` folder for non-architectural decisions (tooling picks, library swaps, day-to-day commitments). That's a **team convention, not industry standard** — but it's a useful split when ADRs feel too heavyweight for routine choices. The audit should detect both shapes and not flag either as wrong; just note which convention is in play.

## MADR 4.0.0 (Markdown Any Decision Records)

MADR ([adr.github.io/madr](https://adr.github.io/madr/)) is the current canonical structured variant. Released **4.0.0 on 2024-09-17** with a notable rename: the _A_ now stands for _Any_ (was _Architectural_) — explicitly broadening scope to non-architectural decisions. Templates: `adr-template.md`, `adr-template-minimal.md`, `adr-template-bare.md`. **YADR** (YAML ADRs) added March 2026.

MADR adds:

- `Deciders:` (who decided)
- `Consulted:` / `Informed:` (who else was looped in)
- More explicit "Considered Options" with pros/cons per option

```markdown
---
status: accepted
date: 2026-04-27
deciders: alice, bob
consulted: data-team
informed: engineering-all
---

# Use Postgres, not MySQL

## Context and Problem Statement

We need a relational database for the user-account service.

## Decision Drivers

- Mature JSONB support
- Strong concurrency story
- Existing team skills

## Considered Options

- Postgres
- MySQL
- SQLite

## Decision Outcome

Chosen: **Postgres**, because of JSONB + concurrency + team skills.

### Consequences

- Good: rich query power, strong type system
- Bad: ops overhead vs SQLite

## Pros and Cons of the Options

### Postgres
- Good: ...
- Bad: ...

### MySQL
- Good: ...
- Bad: ...
```

MADR's structure scales better to larger teams and audit trails. Nygard's brevity is right for smaller teams. Pick one and stick with it.

## Y-statements (Zimmermann)

A concise alternative format positioned by adr.github.io as current best practice. Single-sentence form:

> _"In the context of `<use case / user story>`, facing `<concern>` we decided for `<option>` and neglected `<other options>`, to achieve `<system qualities>` / `<desired consequences>`, accepting `<downside / undesired consequences>`."_

Origin: Olaf Zimmermann, SATURN 2012. Useful as a one-line summary line at the top of a longer ADR, or as the entire ADR for small reversible choices. Pairs well with MADR.

## Tooling (April 2026)

- **`adr-tools`** by Nat Pryce: <https://github.com/npryce/adr-tools> — Bash CLI; **lightly maintained** as of April 2026 (no recent releases; MADR-support PR #43 was rejected for maintenance burden). Still functional for the ADR-creation workflow it was built for.
- **`adr-log`**: generates a Markdown index from a folder of ADRs.
- **`log4brains`**: web-based ADR browser; check current maintenance state before adopting.
- **`adr-manager`**: web-UI ADR editor.
- **For new projects, no tool is required.** `mkdir -p .brain/adrs && cp ~/.adr-templates/madr-minimal.md .brain/adrs/0001-record-architecture-decisions.md` is enough. Tooling adds friction; many teams now skip it.

## How AGENTS.md should reference ADRs

In the `Where to find things` section:

```markdown
- **Architecture Decision Records:** `.brain/adrs/` — newest-first; read before making architectural changes
```

In the `Memory primitives` section:

```markdown
- **Before making architectural decisions**, read `.brain/adrs/` newest-first. If your proposed change conflicts with an `Accepted` ADR, write a new ADR superseding it; don't silently override.
```

## Common anti-patterns

- **No `.brain/adrs/` folder at all** — decisions live in random PR descriptions, Slack, code comments. Memory fragmentation.
- **ADRs as RFCs** — files marked `Proposed` that never get marked `Accepted` or `Rejected`. Status drift.
- **Editing accepted ADRs** — defeats the audit trail. Edits should be supersessions instead.
- **No `Status:` field** — readers can't tell what's current.
- **Mixed numbering schemes** — `001-foo.md`, `2-bar.md`, `0003-baz.md`. Pick `NNNN-` four-digit and stick with it.
- **No ADR for the introduction of ADRs themselves** — the first ADR (`0001`) should be "Record architecture decisions" so the practice itself is decided.

## Audit checks for ADRs

1. **Folder exists** at `.brain/adrs/` (or close — `.brain/architecture/decisions/`, `adrs/`, etc.).
2. **Numbering is consistent** (`NNNN-` four-digit, sequential).
3. **Each ADR has a `Status:` field**.
4. **No ADRs are in `Proposed` for >30 days** (probably abandoned — flag).
5. **`.brain/adrs/` is referenced from AGENTS.md**.

## Cross-references

- Decision log (looser): `decisions-log.md`
- Architecture overview: `architecture-md.md`
- Adding ADRs to existing repo: `../recipes/adr-introduction.md`
- Memory organization: `../recipes/memory-organization.md`
