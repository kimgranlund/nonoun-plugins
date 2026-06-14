---
date: 2026-04-27
coverage: canonical
peers:
  - adr-pattern.md
  - architecture-md.md
  - plan-roadmap.md
primary_sources:
  - https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record — Microsoft Azure Well-Architected Framework on ADR / decision log
  - https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/welcome.html — AWS Prescriptive Guidance, "ADRs"
  - https://adr.github.io — ADR organization (canonical hub)
  - https://github.com/joelparkerhenderson/architecture-decision-record — Joel Parker Henderson catalog (most-cited examples library)
  - https://github.com/npryce/adr-tools — adr-tools, including `adr generate toc`
  - https://github.com/adr/adr-log — adr-log Markdown index generator
status: research-verified
---

# Decision log — what it actually is

> **The canonical "decision log" is the index of all ADRs in `.agents/brain/adrs/`. It is _not_ a separate folder.** This is the load-bearing nuance most teams get wrong.

## The canonical meaning (cite-able)

Microsoft Azure Well-Architected Framework, AWS Prescriptive Guidance, and adr.github.io all converge on the same definition:

> "An Architectural Decision Record (ADR) captures a single AD and its rationale; **the collection of ADRs constitutes the decision log.**" — Microsoft Azure WAF, _Architecture decision record_

> "A collection of ADRs creates a decision log that captures the architectural decisions for a project." — AWS Prescriptive Guidance, _Architectural decision records_

So when a repo has `.agents/brain/adrs/0001-…md` … `0042-…md` and a `.agents/brain/adrs/README.md` listing them, **that is the decision log**. There is no second folder needed.

This skill delivers **Promise 5 (continuously-learning)** by ensuring the decision log is _navigable_ — an ADR folder without an index is a scrapyard.

## The two shapes the audit detects

The repo-fixer audit must accept both shapes and not flag either as wrong. Just note which one is in play.

| Shape | What's on disk | When appropriate |
| --- | --- | --- |
| **Canonical (single-folder)** | `.agents/brain/adrs/` containing all decisions; `.agents/brain/adrs/README.md` is the log index | Default. Fits 90% of teams. |
| **Split (two-folder)** | `.agents/brain/adrs/` for big architecture decisions; `.agents/brain/decisions/` for lighter day-to-day picks (tooling swaps, library choices, formatting conventions) | Larger orgs where ADR review is heavyweight and would gate routine choices |

The split is **a team convention, not industry standard**. Some teams find it useful: ADRs gate architecture, `.agents/brain/decisions/` lets engineers move on a tooling swap without scheduling an architecture review. Other teams find it confusing — two homes invites drift over which decision goes where.

The audit's recommendation order:

1. If only `.agents/brain/adrs/` exists → recommend keeping it canonical; ensure `README.md` index is present and current.
2. If only `.agents/brain/decisions/` exists → recommend renaming to `.agents/brain/adrs/` for tool/community alignment (ADR tooling expects `.agents/brain/adrs/`).
3. If both exist → recommend documenting the split rule in `AGENTS.md`'s "Where to find things" section so the agent knows which folder to write to.

## Generating the index

Three options, ordered by maintenance burden (lowest first):

### Option 1 — `adr-log` (auto-generate)

[`adr-log`](https://github.com/adr/adr-log) reads a folder of ADRs and writes a Markdown table of contents into a delimited region of `README.md`:

```bash
npm i -g adr-log
adr-log -d .agents/brain/adrs -i .agents/brain/adrs/README.md
```

Wrap the index in begin/end markers so subsequent runs only update that region:

```markdown
# Architecture Decision Records

<!-- adrlog -->
- [ADR-0001](0001-record-architecture-decisions.md) — Record architecture decisions
- [ADR-0002](0002-use-postgres-not-mysql.md) — Use Postgres, not MySQL
<!-- adrlogstop -->
```

Add to a pre-commit hook or CI workflow so the index never drifts from filenames. See `../recipes/self-healing-hooks.md`.

### Option 2 — `adr-tools generate toc`

[`adr-tools`](https://github.com/npryce/adr-tools) ships a similar generator. Lightly maintained as of April 2026 — works, but no recent releases.

```bash
adr generate toc > .agents/brain/adrs/README.md
```

### Option 3 — Hand-written index

For small repos (<20 ADRs) the index is one line per ADR. Maintain by hand:

```markdown
# Architecture Decision Records

| # | Title | Status | Date |
|---|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted | 2024-01-12 |
| [0002](0002-use-postgres-not-mysql.md) | Use Postgres, not MySQL | Accepted | 2024-03-04 |
| [0003](0003-rest-not-graphql.md) | REST, not GraphQL | Superseded by 0017 | 2024-03-19 |
| [0017](0017-graphql-for-public-api.md) | GraphQL for public API | Accepted | 2025-11-08 |
```

The hand-written form **adds the Status column**, which the auto-generated forms typically omit. Worth it for a navigable log.

## How AGENTS.md links the decision log

In the `Where to find things` section:

```markdown
- **Architecture Decision Records:** `.agents/brain/adrs/` — see `.agents/brain/adrs/README.md` for the indexed log; newest-first
- **Lightweight decisions** (if your team uses the split): `.agents/brain/decisions/`
```

In the `Memory primitives` section:

```markdown
- **Before making architectural decisions**, consult the decision log at `.agents/brain/adrs/README.md`. If your proposed change conflicts with an `Accepted` ADR, write a new ADR superseding it; don't silently override.
```

## Audit checks for the decision log

1. **`.agents/brain/adrs/` exists** (or `.agents/brain/architecture/decisions/` — accepted alias).
2. **An index file exists** at `.agents/brain/adrs/README.md` listing all ADRs.
3. **The index is current** — every `NNNN-*.md` filename in the folder appears in the index. No orphans, no broken links.
4. **The index sort order is meaningful** (chronological or by status group, not random).
5. **AGENTS.md points at the index file**, not just the folder. Folder-only pointers force the agent to `ls` and guess.
6. **If `.agents/brain/decisions/` also exists**, AGENTS.md documents the split rule.

The "index is current" check is the high-value one — it catches drift after a teammate adds an ADR but forgets to update the index.

## Common anti-patterns

- **No index** — folder of 40 ADRs, no `README.md`. The decision log exists but isn't navigable.
- **Stale index** — index lists 18 ADRs; folder has 26. Catch with the audit + auto-generation.
- **Two parallel logs that drift** — `.agents/brain/adrs/` and `.agents/brain/decisions/` both have ADRs about Postgres. Pick a rule and document it.
- **Decision log as a single Markdown file** — `.agents/brain/decisions.md` with all decisions in one document. Editing one decision rewrites file history; no per-decision audit trail. Strongly recommended against.
- **Folder named `.agents/brain/architecture-decisions/`** — works, but `.agents/brain/adrs/` is what tooling expects. Prefer `.agents/brain/adrs/`.
- **Numbering reset on folder split** — if you split into `.agents/brain/adrs/` and `.agents/brain/decisions/`, do NOT restart numbering at 0001 in the second folder. Keep the global sequence so cross-references work.

## Cross-references

- ADR pattern (canonical): `adr-pattern.md`
- Architecture overview (current state, not decisions): `architecture-md.md`
- Plan / roadmap (forward-looking, not decisions): `plan-roadmap.md`
- Self-healing index generation: `../recipes/self-healing-hooks.md`
- Memory organization: `../recipes/memory-organization.md`
- AGENTS.md memory primitives section: `../standards/agents-md-spec.md`
